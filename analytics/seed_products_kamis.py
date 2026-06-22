"""
KAMIS(농수산물유통정보) → products 적재기
===========================================
KAMIS dailySalesList(소매 일별 시세)를 호출해 실제 품목·가격으로 products 행을 만든다.
백엔드 KamisClient.parse() 와 동일한 필드 규약을 따른다:
  price[] 배열, product_cls_code=="01"(소매), category_name/item_name/unit/dpr1(당일 소매가).

인증
  KAMIS_CERT_KEY / KAMIS_CERT_ID 를 환경변수 또는 backend/.env 에서 읽는다(application.yml 규약과 동일).
  base-url 기본값 = https://www.kamis.or.kr/service/price/xml.do (application.yml과 동일, returntype=json).

스키마 정합
  products(seller_id FK→users, name, category, price, stock_qty, expiration_date ...).
  seller_id 는 DB의 기존 SELLER 들에 분배. product_id 는 MAX(product_id)+1 부터 append(기존 보존).

실행
  python3 seed_products_kamis.py --dry-run   # 호출·파싱만, DB 미변경 (검증용)
  python3 seed_products_kamis.py             # CSV 저장 (data/dummy/products.csv)
  python3 seed_products_kamis.py --load      # CSV 저장 + DB products 에 append
  python3 seed_products_kamis.py --selftest  # 네트워크 없이 파싱/매핑 로직만 검증
"""
import os
import sys
import json
import urllib.parse
import urllib.request
import numpy as np
import pandas as pd
from datetime import date, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, "..", "backend", ".env")
OUT_DIR = os.path.join(BASE_DIR, "data", "dummy")

CONFIG = {
    "seed": 42,
    "base_url": "https://www.kamis.or.kr/service/price/xml.do",
    "lots_per_item": 4,         # 품목당 폐기기간 옵션(lot) 수 → 목록은 품목 1장, 상세에 옵션 N개
    "lot_exp_days": [1, 3, 6, 10, 14, 18],  # lot 유통기한 후보(D-day). 떨이가는 엔진이 D-day로 계산
    "db_url": os.getenv("DB_URL",
        "mysql+pymysql://root:1234@127.0.0.1:3306/freshgrowth?charset=utf8mb4"),
}

# KAMIS category_name → 우리 products.category 코드
CAT_MAP = {
    "식량작물": "grain", "채소류": "vegetable", "과일류": "fruit",
    "축산물": "meat", "수산물": "seafood", "특용작물": "processed",
}


def load_env():
    """환경변수 → backend/.env 순으로 KAMIS 키를 읽는다.
    backend/.env 는 application-local.yml 템플릿(YAML) 이라 두 형식을 모두 지원:
      flat:  KAMIS_CERT_KEY=...   /   YAML: kamis:\\n  cert-key: ..."""
    key = os.getenv("KAMIS_CERT_KEY", "").strip()
    cid = os.getenv("KAMIS_CERT_ID", "").strip()
    if (not key or not cid) and os.path.exists(ENV_PATH):
        for raw in open(ENV_PATH, encoding="utf-8"):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            for sep in ("=", ":"):                       # flat(=) 와 YAML(:) 모두 처리
                if sep in line:
                    k, v = line.split(sep, 1)
                    k, v = k.strip().lower(), v.strip().strip('"').strip("'")
                    if k in ("kamis_cert_key", "cert-key") and not key:
                        key = v
                    elif k in ("kamis_cert_id", "cert-id") and not cid:
                        cid = v
                    break
    return key, cid


def fetch_kamis(cert_key, cert_id, base_url):
    qs = urllib.parse.urlencode({
        "action": "dailySalesList", "p_cert_key": cert_key,
        "p_cert_id": cert_id, "p_returntype": "json",
    })
    url = f"{base_url}?{qs}"
    with urllib.request.urlopen(url, timeout=15) as r:
        return r.read().decode("utf-8")


def parse_items(raw):
    """KamisClient.parse() 와 동일: price[] 중 소매(01) + dpr1 보유 품목만."""
    root = json.loads(raw)
    price = root.get("price")
    if not isinstance(price, list):  # 일부 응답은 data.item 형태 폴백
        price = (root.get("data") or {}).get("item", [])
    items = []
    for n in price:
        if str(n.get("product_cls_code")) != "01":
            continue
        p = _num(n.get("dpr1"))
        if p is None:
            continue
        items.append({
            "category_name": n.get("category_name"),
            "item_name": (n.get("item_name") or "").strip(),
            "unit": (n.get("unit") or "").strip(),
            "price": p,
        })
    return items


def build_catalog(items, seller_ids, start_pid, cfg):
    """KAMIS 품목 → (products 1행, product_lots N행).
    품목당 lot 들은 '같은 정가, 다른 유통기한' → 떨이가는 조회 시 WastePricingEngine 이 D-day 로 산출."""
    rng = np.random.default_rng(cfg["seed"])
    prods, lots, pid = [], [], start_pid
    today = date.today()
    exp_pool = cfg["lot_exp_days"]
    n_lots = min(cfg["lots_per_item"], len(exp_pool))
    for it in items:
        cat = CAT_MAP.get(it["category_name"], "processed")
        base = int(max(300, it["price"]) // 100 * 100)            # 품목 정가(100원 단위)
        unit = f" ({it['unit']})" if it["unit"] else ""
        prods.append({
            "product_id": pid,
            "seller_id": int(rng.choice(seller_ids)),
            "name": f"{it['item_name']}{unit}",                    # 중복 #pid 제거 → 목록 간결
            "description": f"KAMIS 시세 기반 {it['category_name']} · {it['item_name']}",
            "category": cat,
            "price": base,                                        # 대표가(lot 없을 때 폴백용)
            "stock_qty": 0,                                       # 재고는 lot 이 보유
            "thumbnail_url": None,
            "expiration_date": None,                              # 유통기한은 lot 이 보유
        })
        # 폐기기간이 서로 다른 lot N개 (유통기한 빠른 것일수록 엔진이 더 큰 할인)
        for d in sorted(rng.choice(exp_pool, size=n_lots, replace=False)):
            lots.append({
                "product_id": pid,
                "expiration_date": (today + timedelta(days=int(d))).isoformat(),
                "stock_qty": int(rng.integers(10, 120)),
                "price": base,
            })
        pid += 1
    return pd.DataFrame(prods), pd.DataFrame(lots)


def _num(s):
    if s is None:
        return None
    c = str(s).replace(",", "").replace(" ", "")
    if c in ("", "-"):
        return None
    try:
        return int(float(c))
    except ValueError:
        return None


def get_db_context(cfg):
    """기존 SELLER user_id 목록과 다음 product_id 를 DB에서 읽는다."""
    from sqlalchemy import create_engine, text
    eng = create_engine(cfg["db_url"])
    with eng.connect() as c:
        sellers = [r[0] for r in c.execute(text("SELECT user_id FROM users WHERE role='SELLER'"))]
        next_pid = c.execute(text("SELECT COALESCE(MAX(product_id),0)+1 FROM products")).scalar()
    if not sellers:
        sys.exit("  ✖ SELLER 가 없습니다. 먼저 판매자(users)를 적재하세요.")
    return eng, sellers, int(next_pid)


def insert_catalog(products_df, lots_df, eng):
    # FK 순서: products(명시 product_id) → product_lots(그 product_id 참조)
    products_df.where(pd.notnull(products_df), None).to_sql(
        "products", eng, if_exists="append", index=False, method="multi", chunksize=2_000)
    print(f"  ✔ products: {len(products_df):,} rows appended")
    lots_df.where(pd.notnull(lots_df), None).to_sql(
        "product_lots", eng, if_exists="append", index=False, method="multi", chunksize=2_000)
    print(f"  ✔ product_lots: {len(lots_df):,} rows appended")


def run(dry_run=False, do_load=False):
    cfg = CONFIG
    key, cid = load_env()
    if not key or not cid:
        sys.exit("  ✖ KAMIS_CERT_KEY / KAMIS_CERT_ID 미설정.\n"
                 f"    backend/.env 에 키를 넣은 뒤 재실행하세요. (확인 경로: {os.path.abspath(ENV_PATH)})")

    print("  · KAMIS dailySalesList 호출 …")
    items = parse_items(fetch_kamis(key, cid, cfg["base_url"]))
    print(f"  · 소매 품목 {len(items)}건 파싱 (카테고리: {sorted({i['category_name'] for i in items})})")
    if not items:
        sys.exit("  ✖ 파싱된 품목이 없습니다. 응답 형식/키를 확인하세요.")

    if dry_run:
        for it in items[:15]:
            print(f"    - [{CAT_MAP.get(it['category_name'],'?'):9}] {it['item_name']:<12} {it['price']:>8,}원 / {it['unit']}")
        n_lots = min(cfg["lots_per_item"], len(cfg["lot_exp_days"]))
        print(f"  (dry-run: DB·CSV 미변경. 적재 시 품목 {len(items):,}개 + lot {len(items)*n_lots:,}개 예정)")
        return

    eng, sellers, next_pid = get_db_context(cfg)
    products_df, lots_df = build_catalog(items, sellers, next_pid, cfg)
    os.makedirs(OUT_DIR, exist_ok=True)
    products_df.to_csv(f"{OUT_DIR}/products.csv", index=False)
    lots_df.to_csv(f"{OUT_DIR}/product_lots.csv", index=False)
    print(f"  · 품목 {len(products_df):,}개 (pid {next_pid}~{next_pid+len(products_df)-1}) "
          f"+ lot {len(lots_df):,}개 생성 → {OUT_DIR}/")
    if do_load:
        insert_catalog(products_df, lots_df, eng)


# ── 네트워크 없는 자체검증: 대표 KAMIS 응답 샘플로 파싱/매핑 확인 ──
SAMPLE = json.dumps({"price": [
    {"product_cls_code": "01", "category_name": "채소류", "item_name": "상추/청", "unit": "100g", "dpr1": "1,090"},
    {"product_cls_code": "01", "category_name": "과일류", "item_name": "사과/후지", "unit": "10개", "dpr1": "28,400"},
    {"product_cls_code": "02", "category_name": "과일류", "item_name": "사과/후지(도매)", "unit": "10kg", "dpr1": "55,000"},
    {"product_cls_code": "01", "category_name": "축산물", "item_name": "쇠고기/등심", "unit": "100g", "dpr1": "9,800"},
    {"product_cls_code": "01", "category_name": "수산물", "item_name": "고등어", "unit": "1마리", "dpr1": "3,500"},
    {"product_cls_code": "01", "category_name": "식량작물", "item_name": "쌀", "unit": "20kg", "dpr1": "58,200"},
    {"product_cls_code": "01", "category_name": "채소류", "item_name": "감자", "unit": "100g", "dpr1": "-"},  # 가격없음→제외
]}, ensure_ascii=False)


def selftest():
    items = parse_items(SAMPLE)
    assert len(items) == 5, f"소매+가격 품목 5개 기대, got {len(items)}"          # 도매1·무가격1 제외
    assert all(CAT_MAP[i["category_name"]] for i in items)
    prods, lots = build_catalog(items, seller_ids=[1, 2, 3], start_pid=100, cfg=CONFIG)
    n_lots = min(CONFIG["lots_per_item"], len(CONFIG["lot_exp_days"]))
    assert len(prods) == 5 and prods["product_id"].is_unique          # 품목 1행씩
    assert "#" not in "".join(prods["name"])                          # 목록 간결(중복 #pid 없음)
    assert len(lots) == 5 * n_lots                                    # 품목당 lot N개
    assert lots["product_id"].isin(prods["product_id"]).all()         # FK 정합
    assert set(prods["category"]) <= {"vegetable", "fruit", "meat", "seafood", "grain", "processed"}
    # 한 품목의 lot 들은 같은 정가, 다른 유통기한 → 떨이가는 엔진이 D-day로 차등
    g = lots[lots["product_id"] == 100]
    assert g["price"].nunique() == 1 and g["expiration_date"].nunique() == len(g)
    print("  ✔ selftest 통과: 소매필터·카테고리매핑·품목1행·lot N개·FK·동일정가/상이유통기한 OK")
    print(prods[["product_id", "name", "category", "price"]].to_string(index=False))


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--selftest" in args:
        selftest()
    else:
        run(dry_run="--dry-run" in args, do_load="--load" in args)
