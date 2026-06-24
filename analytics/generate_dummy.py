"""
FreshGrowth 더미 데이터 생성기 — 유저(판매자+구매자) & 주문(lot 단위)
=====================================================================
products·product_lots 는 외부(KAMIS) 적재분을 그대로 둔다. 이 스크립트는 **DB의 실제
품목·폐기기간옵션(lot)을 읽어 참조**하면서, 유저(users)와 주문(orders)만 생성한다.

핵심: 주문은 품목이 아니라 **폐기기간 옵션(lot)** 을 사서, 그 lot 의 할인가로 결제한다
(orders.lot_id). 할인가는 백엔드 WastePricingEngine 과 동일 규칙을 파이썬으로 재현.

적용한 통계 규칙
  1) 페르소나 4그룹 → 카테고리 구매 가중치 차등.
  2) 일별 주문수 ~ Poisson(λ), 주말 ×1.5.
  3) 계절성: 품목명 키워드로 제철 매핑 → 제철 구매확률 ↑.
  4) 가격탄력성: lot 할인가가 쌀수록(=폐기 임박) 구매수량 ↑ (역상관).
  5) 딜 선호: 임박(D-3 이내) lot 을 더 자주 선택.

실행: python3 generate_dummy.py        # CSV (data/dummy/users.csv, orders.csv)
      python3 generate_dummy.py --load # 생성 + DB 적재(주문·구매자 교체)
"""
import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, date
from scipy import stats
from faker import Faker

CONFIG = {
    "seed": 42,
    "n_buyers": 1_500,                 # 1만 주문 기준 1인당 ~6.7건 → 모델 시그널 적정 (판매자는 seed_products_kamis 가 생성)
    "start_date": "2026-01-01",
    "end_date": "2026-06-22",
    "daily_orders_lambda": 50,         # 평일 평균 주문수 → 총 ~1만 건(주말 1.5배 포함)
    "weekend_multiplier": 1.5,
    "price_elasticity": 1.3,
    "deal_purchase_boost": 1.8,        # 임박(D-3 이내) lot 선택 가중
    "db_url": os.getenv("DB_URL",
        "mysql+pymysql://root:1234@127.0.0.1:3306/freshgrowth?charset=utf8mb4"),
    "password_hash": "$2b$10$5I3GEXrJghnjSVepCQmjFucBk9jGYpPUDEAEQ5sOC.ltXkgnSSh4O",
}

# WastePricingEngine 상수 (backend 와 동일) — lot 할인가 재현용
W = {"SAFE_DAYS": 7, "HIGH_STOCK": 50, "URGENCY": 0.7, "STOCK": 0.3,
     "MAX_DISCOUNT": 60, "FLOOR": 0.15}

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "dummy")

PERSONAS = {
    "single":  {"share": 0.40, "base_qty": 1.4, "price_sensitivity": 1.2,
                "cat_w": {"vegetable": 3, "fruit": 2, "seafood": 1, "meat": 1.5, "grain": 1, "processed": 4}},
    "family":  {"share": 0.30, "base_qty": 3.2, "price_sensitivity": 0.9,
                "cat_w": {"vegetable": 4, "fruit": 4, "seafood": 2, "meat": 5, "grain": 3, "processed": 2}},
    "health":  {"share": 0.18, "base_qty": 2.0, "price_sensitivity": 0.5,
                "cat_w": {"vegetable": 5, "fruit": 4, "seafood": 4, "meat": 2, "grain": 3, "processed": 0.5}},
    "bargain": {"share": 0.12, "base_qty": 2.2, "price_sensitivity": 2.0,
                "cat_w": {"vegetable": 3, "fruit": 3, "seafood": 2, "meat": 3, "grain": 2, "processed": 3}},
}

SEASON_MAP = {
    "딸기": ({12, 1, 2, 3, 4}, 0.8), "감귤": ({11, 12, 1, 2}, 0.8), "귤": ({11, 12, 1, 2}, 0.8),
    "수박": ({6, 7, 8}, 0.9), "참외": ({5, 6, 7}, 0.7), "복숭아": ({7, 8}, 0.8),
    "샤인": ({8, 9, 10}, 0.7), "포도": ({8, 9, 10}, 0.7), "사과": ({10, 11, 12, 1}, 0.4),
    "배": ({9, 10, 11, 12}, 0.5), "시금치": ({11, 12, 1, 2}, 0.6), "토마토": ({5, 6, 7, 8}, 0.5),
    "상추": ({4, 5, 6, 9, 10}, 0.4), "오이": ({5, 6, 7, 8}, 0.4), "애호박": ({6, 7, 8, 9}, 0.4),
    "깻잎": ({6, 7, 8}, 0.4), "감자": ({6, 7, 8, 9}, 0.3), "고등어": ({9, 10, 11}, 0.4),
    "오징어": ({5, 6, 7, 8}, 0.4), "새우": ({10, 11, 12}, 0.5), "갈치": ({9, 10, 11}, 0.4),
}


def waste_price(days, stock, base):
    """WastePricingEngine.compute 재현 → lot 의 폐기기간별 할인가(100원 단위)."""
    if days < 0:
        return base, 0
    urgency = min(max((W["SAFE_DAYS"] - days) / W["SAFE_DAYS"], 0), 1)
    sp = min(max((stock or 0) / W["HIGH_STOCK"], 0), 1)
    risk = W["URGENCY"] * urgency + W["STOCK"] * sp
    rate = 0
    if risk >= W["FLOOR"]:
        rate = round(min(max((risk - W["FLOOR"]) / (1 - W["FLOOR"]), 0), 1) * W["MAX_DISCOUNT"])
    disc = max(round(base * (1 - rate / 100) / 100) * 100, 0)
    return int(disc), int(rate)


def main(do_load=False):
    cfg = CONFIG
    rng = np.random.default_rng(cfg["seed"])
    fake = Faker("ko_KR"); Faker.seed(cfg["seed"])
    start = datetime.strptime(cfg["start_date"], "%Y-%m-%d")
    end = datetime.strptime(cfg["end_date"], "%Y-%m-%d")
    n_days = (end - start).days + 1

    # ── ① products + lots: DB에서 읽기 ───────────────────────────
    prod_df, lots_by_pid, max_uid = load_db(cfg)
    products = _enrich(prod_df, lots_by_pid)
    products = [p for p in products if p["lots"]]              # lot 있는 품목만 주문 대상
    if not products:
        sys.exit("  ✖ lot 이 달린 상품이 없습니다. 먼저 seed_products_kamis.py --load 를 실행하세요.")
    by_cat = {}
    for i, p in enumerate(products):
        by_cat.setdefault(p["category"], []).append(i)
    for c in by_cat:
        by_cat[c] = np.array(by_cat[c])
    print(f"  · 주문대상 품목 {len(products):,}개 / lot {sum(len(p['lots']) for p in products):,}개, "
          f"카테고리 {list(by_cat)} / 기존 MAX(user_id)={max_uid}")

    # ── ② users: 구매자만 생성 (판매자는 seed_products_kamis 가 담당) ──
    users, uid = [], max_uid + 1
    buyer_ids, buyer_persona = [], {}
    pnames = list(PERSONAS)
    pp = np.array([PERSONAS[p]["share"] for p in pnames]); pp /= pp.sum()
    for _ in range(cfg["n_buyers"]):
        users.append(_user_row(uid, "BUYER", fake))
        buyer_persona[uid] = pnames[rng.choice(len(pnames), p=pp)]
        buyer_ids.append(uid); uid += 1
    users_df = pd.DataFrame(users)

    # ── ③ orders: 포아송 + 주말 + 페르소나 + 계절 + lot선택 + 탄력성 ──
    orders, order_id = [], 1
    buyer_arr = np.array(buyer_ids)
    for d in range(n_days):
        day = start + timedelta(days=d)
        lam = cfg["daily_orders_lambda"] * (cfg["weekend_multiplier"] if day.weekday() >= 5 else 1.0)
        month = day.month
        for _ in range(int(stats.poisson.rvs(lam, random_state=rng))):
            buyer = int(rng.choice(buyer_arr))
            persona = PERSONAS[buyer_persona[buyer]]
            cats = [c for c in persona["cat_w"] if c in by_cat]
            if not cats:
                continue
            cw = np.array([persona["cat_w"][c] for c in cats], dtype=float)
            cat = cats[rng.choice(len(cats), p=cw / cw.sum())]
            cand = by_cat[cat]
            # (a) 품목 선택: 인기도 × 계절성
            w = np.empty(len(cand))
            for i, idx in enumerate(cand):
                p = products[idx]
                seas = 1.0
                if p["peak"]:
                    seas = 1.0 + p["seas"] if month in p["peak"] else 1.0 - p["seas"] * 0.5
                w[i] = max(0.05, p["pop"] * seas)
            prod = products[int(cand[rng.choice(len(cand), p=w / w.sum())])]
            # (b) lot 선택: 임박(딜) lot 가중
            lots = prod["lots"]
            lw = np.array([(cfg["deal_purchase_boost"] if lo["days"] <= 3 else 1.0) * (1 + lo["rate"] / 100.0)
                           for lo in lots])
            lot = lots[int(rng.choice(len(lots), p=lw / lw.sum()))]
            # (c) 가격탄력성: 할인가 쌀수록 수량 ↑
            elasticity = cfg["price_elasticity"] * persona["price_sensitivity"]
            qty_scale = (prod["base"] / max(lot["dprice"], 1)) ** elasticity
            qty = max(1, int(round(persona["base_qty"] * qty_scale * rng.uniform(0.6, 1.4))))
            odt = day + timedelta(hours=int(_hour(rng)),
                                  minutes=int(rng.integers(0, 60)), seconds=int(rng.integers(0, 60)))
            orders.append({"order_id": order_id, "buyer_id": buyer,
                           "product_id": prod["product_id"], "lot_id": lot["lot_id"],
                           "quantity": qty, "total_price": lot["dprice"] * qty,
                           "original_unit_price": lot["price"],   # 할인 전 정가 → 절약액/회수매출 산출
                           "status": _status(rng), "order_date": odt.strftime("%Y-%m-%d %H:%M:%S")})
            order_id += 1
    orders_df = pd.DataFrame(orders)

    os.makedirs(OUT_DIR, exist_ok=True)
    users_out = users_df[["user_id", "role", "email", "password", "name",
                          "intro", "phone", "status", "created_at"]]
    orders_out = orders_df[["order_id", "buyer_id", "product_id", "lot_id", "quantity",
                            "total_price", "original_unit_price", "status", "order_date"]]
    users_out.to_csv(f"{OUT_DIR}/users.csv", index=False)
    orders_out.to_csv(f"{OUT_DIR}/orders.csv", index=False)
    _summary(users_df, products, orders_df, cfg)

    if do_load:
        bulk_insert(users_out, orders_out, cfg)


# ── data source ───────────────────────────────────────────────────
def load_db(cfg):
    """products + product_lots + MAX(user_id) 를 읽는다."""
    from sqlalchemy import create_engine, text
    eng = create_engine(cfg["db_url"])
    with eng.connect() as c:
        prod = pd.read_sql(text("SELECT product_id, name, category, price FROM products"), c)
        lots = pd.read_sql(text("SELECT lot_id, product_id, expiration_date, stock_qty, price FROM product_lots"), c)
        max_uid = c.execute(text("SELECT COALESCE(MAX(user_id),0) FROM users")).scalar()
    today = date.today()
    lots_by_pid = {}
    for r in lots.itertuples(index=False):
        exp = pd.to_datetime(r.expiration_date).date()
        days = (exp - today).days
        dprice, rate = waste_price(days, int(r.stock_qty), int(r.price))
        lots_by_pid.setdefault(int(r.product_id), []).append(
            {"lot_id": int(r.lot_id), "days": days, "rate": rate,
             "price": int(r.price), "dprice": dprice})   # price=정가, dprice=할인가
    return prod, lots_by_pid, int(max_uid)


def _enrich(df, lots_by_pid):
    out = []
    for r in df.itertuples(index=False):
        name = str(r.name)
        peak, seas = set(), 0.0
        for kw, (pk, st) in SEASON_MAP.items():
            if kw in name:
                peak, seas = pk, st; break
        pop = float(np.random.default_rng(int(r.product_id)).lognormal(0, 0.6))
        out.append({"product_id": int(r.product_id), "category": r.category,
                    "base": int(r.price), "peak": peak, "seas": seas, "pop": pop,
                    "lots": lots_by_pid.get(int(r.product_id), [])})
    return out


# ── helpers ───────────────────────────────────────────────────────
def _user_row(uid, role, fake):
    prefix = "seller" if role == "SELLER" else "buyer"
    created = datetime.strptime(CONFIG["start_date"], "%Y-%m-%d") - timedelta(days=int(np.random.default_rng(uid).integers(0, 120)))
    return {"user_id": uid, "role": role,
            "email": f"{prefix}{uid}@fresh.test", "password": CONFIG["password_hash"],
            "name": fake.name(), "intro": None, "phone": fake.numerify("010-####-####"),
            "status": "ACTIVE", "created_at": created.strftime("%Y-%m-%d %H:%M:%S")}


def _hour(rng):
    base = np.ones(24) * 0.3
    base[7:10] += 0.6; base[12:14] += 0.5; base[18:23] += 1.6
    return rng.choice(24, p=base / base.sum())


def _status(rng):
    return rng.choice(["COMPLETED", "SHIPPING", "CONFIRMED", "PENDING"], p=[0.70, 0.12, 0.10, 0.08])


def _summary(users, products, orders, cfg):
    gmv = orders["total_price"].sum()
    saved = int((orders["original_unit_price"] * orders["quantity"] - orders["total_price"]).clip(lower=0).sum())
    wk = orders.copy(); wk["dow"] = pd.to_datetime(wk["order_date"]).dt.dayofweek
    wd = wk[wk["dow"] < 5].groupby(wk["order_date"].str[:10]).size().mean()
    we = wk[wk["dow"] >= 5].groupby(wk["order_date"].str[:10]).size().mean()
    print("=" * 60)
    print("  더미 생성 완료  (products·lots 는 DB 원본 그대로, 주문은 lot 참조)")
    print("=" * 60)
    print(f"  더미 구매자 {len(users):>10,}  (BUYER only · 판매자는 seed 단계)")
    print(f"  주문대상품목 {len(products):>9,}")
    print(f"  주문        {len(orders):>10,}")
    print(f"  GMV         {gmv:>13,} 원   AOV {gmv//max(1,len(orders)):,}")
    print(f"  폐기회수 절약 {saved:>12,} 원  (정가 대비 할인 합계)")
    print(f"  평일 일평균 {wd:.0f} / 주말 {we:.0f}  (배수 {we/wd:.2f})")
    print(f"  저장: {OUT_DIR}/users.csv, orders.csv")
    print("=" * 60)


# ── DB 적재 — products·lots·소유 판매자 보존, 주문·구매자만 교체 ──
def bulk_insert(users_df, orders_df, cfg):
    from sqlalchemy import create_engine, text
    eng = create_engine(cfg["db_url"])
    with eng.begin() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        conn.execute(text("DELETE FROM reviews"))
        conn.execute(text("DELETE FROM orders"))
        conn.execute(text("DELETE FROM users WHERE role='BUYER'"))
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
    for df, table in [(users_df, "users"), (orders_df, "orders")]:
        df.where(pd.notnull(df), None).to_sql(
            table, eng, if_exists="append", index=False, method="multi", chunksize=2_000)
        print(f"  ✔ {table}: {len(df):,} rows inserted")


if __name__ == "__main__":
    main(do_load="--load" in sys.argv)
