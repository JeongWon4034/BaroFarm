"""
FreshGrowth 행동로그 파라메트릭 시뮬레이터
================================================
실트래픽이 없는 상태에서 Layer 2 행동로그(조회·검색·찜·구매 이벤트)를
확률분포 기반으로 합성한다. 데이터는 합성이지만, 그 위에서 돌리는 지표는 실제 계산.

설계 원칙
  - 차원(users, products) → 행동(events) → 결과(orders, wishlists, reviews)를
    하나의 인과로 생성해 2-Layer 정합성을 유지한다.
  - 모든 무작위성은 SEED로 고정 → 재현 가능.
  - 가정/파라미터는 CONFIG 한곳에 모아 시나리오를 손잡이처럼 조절한다.

산출물 (analytics/data/)
  users.csv, products.csv         (차원 = RDB Layer 1)
  events.ndjson                   (행동로그 = NoSQL Layer 2)
  orders.csv, wishlists.csv, reviews.csv  (결과 = RDB Layer 1, 이벤트와 정합)
"""
import csv
import json
import os
import numpy as np
from datetime import datetime, timedelta

# ──────────────────────────────────────────────────────────────────
# CONFIG — 시뮬레이션 손잡이 (값만 바꾸면 시나리오가 바뀐다)
# ──────────────────────────────────────────────────────────────────
CONFIG = {
    "seed": 42,
    # 규모
    "n_buyers": 900,
    "n_sellers": 100,
    "n_products": 200,
    "start_date": "2026-03-01",
    "days": 92,                       # ≈ 3개월
    # 유저 활동량 (세션 수) — 음이항: 헤비유저 소수 + 롱테일
    "sessions_mean": 18.0,
    "sessions_dispersion": 1.4,       # 작을수록 편차 큼
    # 세션 내부
    "p_search": 0.70,                 # 세션에 검색이 있을 확률
    "views_per_session_lambda": 3.0,  # 세션당 상품 조회 수 ~ 1+Poisson
    # 퍼널 전환율 (조회 단위)
    "p_detail_given_view": 0.35,      # 조회 → 상세조회
    "p_wishlist_given_detail": 0.12,  # 상세 → 찜
    "p_purchase_given_detail": 0.05,  # 상세 → 구매
    # 마감임박 딜 효과 (배수)
    "deal_view_share": 0.20,          # 전체 조회 중 딜(마감임박) 노출 비중
    "deal_purchase_mult": 1.8,        # 딜이면 구매율 ×
    "deal_wishlist_mult": 1.4,        # 딜이면 찜율 ×
    # 상품 인기도 (Zipf 멱함수)
    "popularity_alpha": 1.1,
    # 시간대/요일 가중
    "weekend_weight": 1.5,            # 주말 세션 가중
    # 구매 후 리뷰 작성률
    "p_review_given_purchase": 0.45,
}

CATEGORIES = ["채소", "과일", "수산", "축산", "곡물", "가공식품"]
# 카테고리별 가격대(원) — 농수산물 현실 가격대에 그라운딩 (평균, 표준편차)
PRICE_BY_CAT = {
    "채소":   (4000, 1800),
    "과일":   (12000, 5000),
    "수산":   (18000, 8000),
    "축산":   (22000, 9000),
    "곡물":   (9000, 3000),
    "가공식품": (7000, 3000),
}
ITEM_WORDS = {
    "채소": ["양파", "대파", "감자", "상추", "오이", "애호박"],
    "과일": ["사과", "딸기", "샤인머스캣", "참외", "복숭아", "감귤"],
    "수산": ["고등어", "오징어", "광어", "새우", "전복", "갈치"],
    "축산": ["삼겹살", "한우등심", "닭가슴살", "계란", "목살", "양지"],
    "곡물": ["백미", "현미", "찹쌀", "콩", "보리", "귀리"],
    "가공식품": ["김치", "두부", "된장", "고추장", "참기름", "젓갈"],
}

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def main():
    cfg = CONFIG
    rng = np.random.default_rng(cfg["seed"])
    start = datetime.strptime(cfg["start_date"], "%Y-%m-%d")

    # ── ① 차원: 유저 ──────────────────────────────────────────────
    sellers, buyers, users = [], [], []
    uid = 1
    for _ in range(cfg["n_sellers"]):
        users.append({"user_id": uid, "role": "SELLER", "name": f"판매자{uid}",
                      "status": "ACTIVE",
                      "created_at": _rand_dt(rng, start, cfg["days"])})
        sellers.append(uid); uid += 1
    for _ in range(cfg["n_buyers"]):
        users.append({"user_id": uid, "role": "BUYER", "name": f"구매자{uid}",
                      "status": "ACTIVE",
                      "created_at": _rand_dt(rng, start, cfg["days"])})
        buyers.append(uid); uid += 1

    # ── ① 차원: 상품 ──────────────────────────────────────────────
    products = []
    for pid in range(1, cfg["n_products"] + 1):
        cat = CATEGORIES[rng.integers(0, len(CATEGORIES))]
        mu, sd = PRICE_BY_CAT[cat]
        price = int(max(500, rng.normal(mu, sd)) // 100 * 100)
        word = ITEM_WORDS[cat][rng.integers(0, len(ITEM_WORDS[cat]))]
        products.append({
            "product_id": pid,
            "seller_id": int(rng.choice(sellers)),
            "name": f"{word} {price//1000}k상품{pid}",
            "category": cat,
            "price": price,
            # 딜 성향: 상품마다 마감임박이 잘 뜨는 정도 (Beta로 다양화)
            "_deal_propensity": float(rng.beta(2, 8)),
        })

    # 인기도: Zipf 멱함수 가중 (순위가 셔플된 상품에 부여)
    order = rng.permutation(cfg["n_products"])
    ranks = np.empty(cfg["n_products"], dtype=float)
    ranks[order] = np.arange(1, cfg["n_products"] + 1)
    pop_w = 1.0 / np.power(ranks, cfg["popularity_alpha"])
    pop_w /= pop_w.sum()

    # ── ② 행동: 세션·이벤트 ───────────────────────────────────────
    events, orders, wishlists, reviews = [], [], [], []
    ev_id = order_id = 1
    # 음이항 파라미터 변환 (평균 m, dispersion r)
    r = cfg["sessions_dispersion"]
    m = cfg["sessions_mean"]
    p_nb = r / (r + m)

    for bid in buyers:
        n_sessions = int(rng.negative_binomial(r, p_nb))
        for _s in range(n_sessions):
            ts = _session_ts(rng, start, cfg)
            sess_id = f"s{bid}_{_s}"
            # 검색 이벤트
            if rng.random() < cfg["p_search"]:
                cat = CATEGORIES[rng.integers(0, len(CATEGORIES))]
                q = ITEM_WORDS[cat][rng.integers(0, len(ITEM_WORDS[cat]))]
                events.append(_ev(ev_id, bid, sess_id, ts, "search",
                                  product=None, query=q, category=cat)); ev_id += 1
            # 상품 조회 → 퍼널
            n_views = 1 + int(rng.poisson(cfg["views_per_session_lambda"]))
            viewed = rng.choice(cfg["n_products"], size=n_views, p=pop_w)
            for k, pidx in enumerate(viewed):
                p = products[pidx]
                t_view = ts + timedelta(seconds=int(k * rng.integers(20, 120)))
                is_deal = rng.random() < _deal_prob(p, cfg)
                events.append(_ev(ev_id, bid, sess_id, t_view, "list_view",
                                  product=p, is_deal=is_deal)); ev_id += 1
                if rng.random() >= cfg["p_detail_given_view"]:
                    continue
                t_detail = t_view + timedelta(seconds=int(rng.integers(5, 40)))
                events.append(_ev(ev_id, bid, sess_id, t_detail, "detail_view",
                                  product=p, is_deal=is_deal)); ev_id += 1
                # 찜
                p_wish = cfg["p_wishlist_given_detail"] * (
                    cfg["deal_wishlist_mult"] if is_deal else 1.0)
                if rng.random() < p_wish:
                    t_w = t_detail + timedelta(seconds=int(rng.integers(2, 20)))
                    events.append(_ev(ev_id, bid, sess_id, t_w, "wishlist",
                                      product=p, is_deal=is_deal)); ev_id += 1
                    wishlists.append({"user_id": bid, "product_id": p["product_id"],
                                      "created_at": _fmt(t_w)})
                # 구매
                p_buy = cfg["p_purchase_given_detail"] * (
                    cfg["deal_purchase_mult"] if is_deal else 1.0)
                if rng.random() < p_buy:
                    t_b = t_detail + timedelta(seconds=int(rng.integers(10, 90)))
                    qty = 1 + int(rng.poisson(0.6))
                    total = qty * p["price"]
                    events.append(_ev(ev_id, bid, sess_id, t_b, "purchase",
                                      product=p, is_deal=is_deal,
                                      qty=qty, total=total)); ev_id += 1
                    orders.append({"order_id": order_id, "buyer_id": bid,
                                   "product_id": p["product_id"], "quantity": qty,
                                   "total_price": total, "status": "COMPLETED",
                                   "is_deal": int(is_deal), "order_date": _fmt(t_b)})
                    if rng.random() < cfg["p_review_given_purchase"]:
                        t_r = t_b + timedelta(days=int(rng.integers(1, 8)))
                        reviews.append({"order_id": order_id, "buyer_id": bid,
                                        "product_id": p["product_id"],
                                        "rating": int(rng.integers(3, 6)),
                                        "created_at": _fmt(t_r)})
                    order_id += 1

    # ── 정렬 & 저장 ───────────────────────────────────────────────
    events.sort(key=lambda e: e["ts"])
    os.makedirs(OUT_DIR, exist_ok=True)
    _write_csv(os.path.join(OUT_DIR, "users.csv"),
               [{k: v for k, v in u.items()} for u in users])
    _write_csv(os.path.join(OUT_DIR, "products.csv"),
               [{k: v for k, v in p.items() if not k.startswith("_")} for p in products])
    _write_ndjson(os.path.join(OUT_DIR, "events.ndjson"), events)
    _write_csv(os.path.join(OUT_DIR, "orders.csv"), orders)
    _write_csv(os.path.join(OUT_DIR, "wishlists.csv"), wishlists)
    _write_csv(os.path.join(OUT_DIR, "reviews.csv"), reviews)

    _summary(events, orders, users, products)


# ── helpers ───────────────────────────────────────────────────────
def _deal_prob(p, cfg):
    # 상품 딜 성향을 전체 평균이 deal_view_share에 맞도록 스케일
    return min(1.0, p["_deal_propensity"] / 0.20 * cfg["deal_view_share"])


def _ev(ev_id, uid, sess, ts, etype, product=None, is_deal=False,
        query=None, category=None, qty=None, total=None):
    e = {"event_id": ev_id, "user_id": uid, "session_id": sess,
         "ts": ts, "event_type": etype}
    if product is not None:
        e.update({"product_id": product["product_id"],
                  "category": product["category"], "price": product["price"],
                  "is_deal": bool(is_deal)})
    if query is not None:
        e["query"] = query
    if category is not None and product is None:
        e["category"] = category
    if qty is not None:
        e["quantity"] = qty; e["total_price"] = total
    return e


def _rand_dt(rng, start, days):
    d = int(rng.integers(0, days))
    return _fmt(start + timedelta(days=d,
                                  seconds=int(rng.integers(0, 86400))))


def _session_ts(rng, start, cfg):
    # 요일 가중: 주말 ↑
    while True:
        day = int(rng.integers(0, cfg["days"]))
        dt = start + timedelta(days=day)
        w = cfg["weekend_weight"] if dt.weekday() >= 5 else 1.0
        if rng.random() < w / cfg["weekend_weight"]:
            break
    # 시간대 가중: 저녁 18~22 피크
    hours = np.arange(24)
    base = np.ones(24) * 0.3
    base[7:10] += 0.6        # 아침
    base[12:14] += 0.5       # 점심
    base[18:23] += 1.6       # 저녁 피크
    hour = int(rng.choice(hours, p=base / base.sum()))
    minute = int(rng.integers(0, 60))
    return dt + timedelta(hours=hour, minutes=minute)


def _fmt(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S") if isinstance(dt, datetime) else dt


def _write_csv(path, rows):
    if not rows:
        open(path, "w").close(); return
    # ts 같은 datetime 직렬화
    norm = []
    for r in rows:
        norm.append({k: (_fmt(v) if isinstance(v, datetime) else v)
                     for k, v in r.items()})
    keys = list(norm[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader(); w.writerows(norm)


def _write_ndjson(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            r = {k: (_fmt(v) if isinstance(v, datetime) else v)
                 for k, v in r.items()}
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def _summary(events, orders, users, products):
    n = len(events)
    by = {}
    for e in events:
        by[e["event_type"]] = by.get(e["event_type"], 0) + 1
    sessions = len({e["session_id"] for e in events})
    detail = by.get("detail_view", 0)
    purch = by.get("purchase", 0)
    # 딜 효과: 딜 상세조회 대비 구매 vs 정상 상세조회 대비 구매
    dd = [e for e in events if e["event_type"] == "detail_view" and e.get("is_deal")]
    nd = [e for e in events if e["event_type"] == "detail_view" and not e.get("is_deal")]
    dp = [e for e in events if e["event_type"] == "purchase" and e.get("is_deal")]
    npd = [e for e in events if e["event_type"] == "purchase" and not e.get("is_deal")]
    gmv = sum(o["total_price"] for o in orders)
    cvr_deal = (len(dp) / len(dd) * 100) if dd else 0
    cvr_norm = (len(npd) / len(nd) * 100) if nd else 0
    print("=" * 56)
    print("  시뮬레이션 결과 요약")
    print("=" * 56)
    print(f"  유저            {len(users):>8,}  (BUYER {sum(u['role']=='BUYER' for u in users)})")
    print(f"  상품            {len(products):>8,}")
    print(f"  세션            {sessions:>8,}")
    print(f"  이벤트 총계      {n:>8,}")
    for t in ["search", "list_view", "detail_view", "wishlist", "purchase"]:
        print(f"    - {t:<12}{by.get(t,0):>8,}")
    print("-" * 56)
    print(f"  세션→구매 전환율  {purch/sessions*100:>7.2f}%")
    print(f"  상세→구매 전환율  {purch/detail*100:>7.2f}%")
    print(f"  [딜 효과] 상세→구매:  딜 {cvr_deal:.2f}%  vs  정상 {cvr_norm:.2f}%"
          f"  (×{cvr_deal/cvr_norm:.2f})" if cvr_norm else "")
    print(f"  주문 건수        {len(orders):>8,}")
    print(f"  GMV             {gmv:>12,} 원")
    print(f"  객단가(AOV)      {gmv//max(1,len(orders)):>12,} 원")
    print("=" * 56)


if __name__ == "__main__":
    main()
