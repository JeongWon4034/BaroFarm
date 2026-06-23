"""
data/dummy/*.csv  →  backend/src/main/resources/seed_products_kamis.sql
====================================================================
seed_products_kamis.py 가 떨군 CSV(sellers/products/product_lots)를
배포용 정적 SQL 시드로 박제한다. docker-entrypoint-initdb.d 가 첫 기동 때
01-schema → 02-seed → 03-products 순서로 실행하므로, 이 파일이 03 역할.

핵심 설계
  · product_lots.expiration_date 는 '절대 날짜' 대신 DATE_ADD(CURDATE(), INTERVAL n DAY)
    로 emit → 언제 배포해도 'D-n' 상대 거리가 유지돼 떨이가 엔진이 정상 동작.
  · ID(user_id/product_id)는 CSV 값을 그대로 사용. 이는 02-seed(seed_testdata.sql)가
    먼저 실행돼 users=10·products=13 상태를 만든다는 전제 위에서 충돌이 없다.

실행:  python3 csv_to_seed_sql.py
"""
import os
import csv
from datetime import date, datetime

BASE = os.path.dirname(os.path.abspath(__file__))
CSV_DIR = os.path.join(BASE, "data", "dummy")
OUT = os.path.join(BASE, "..", "backend", "src", "main", "resources", "seed_products_kamis.sql")
ANCHOR = date.today()   # lot 절대날짜 → 상대 offset 산출 기준(생성 당일)


def q(v):
    """SQL 문자열 리터럴: None/빈값→NULL, 작은따옴표 이스케이프."""
    if v is None or v == "":
        return "NULL"
    return "'" + str(v).replace("'", "''") + "'"


def read(name):
    with open(os.path.join(CSV_DIR, f"{name}.csv"), encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    sellers, products, lots = read("sellers"), read("products"), read("product_lots")
    L = []
    L.append("-- 자동 생성: analytics/csv_to_seed_sql.py (직접 수정 금지)")
    L.append("-- KAMIS 시세 기반 판매자/상품/lot 시드. initdb.d 03 단계로 첫 기동 시 1회 실행.")
    L.append(f"-- 생성일 {ANCHOR.isoformat()} · 판매자 {len(sellers)} · 상품 {len(products)} · lot {len(lots)}")
    L.append("")

    # 1) 판매자(users)
    L.append("INSERT INTO users (user_id, role, email, password, name, intro, phone, status, created_at) VALUES")
    rows = [f"  ({s['user_id']}, {q(s['role'])}, {q(s['email'])}, {q(s['password'])}, "
            f"{q(s['name'])}, {q(s['intro'])}, {q(s['phone'])}, {q(s['status'])}, {q(s['created_at'])})"
            for s in sellers]
    L.append(",\n".join(rows) + ";")
    L.append("")

    # 2) 상품(products)
    L.append("INSERT INTO products (product_id, seller_id, name, description, category, price, stock_qty, thumbnail_url, expiration_date) VALUES")
    rows = [f"  ({p['product_id']}, {p['seller_id']}, {q(p['name'])}, {q(p['description'])}, "
            f"{q(p['category'])}, {p['price']}, {p['stock_qty']}, {q(p['thumbnail_url'])}, {q(p['expiration_date'])})"
            for p in products]
    L.append(",\n".join(rows) + ";")
    L.append("")

    # 3) lot(product_lots) — 상대 날짜로 emit
    L.append("INSERT INTO product_lots (product_id, expiration_date, stock_qty, price) VALUES")
    rows = []
    for lt in lots:
        exp = datetime.strptime(lt["expiration_date"], "%Y-%m-%d").date()
        offset = (exp - ANCHOR).days
        rows.append(f"  ({lt['product_id']}, DATE_ADD(CURDATE(), INTERVAL {offset} DAY), "
                    f"{lt['stock_qty']}, {lt['price']})")
    L.append(",\n".join(rows) + ";")
    L.append("")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    offsets = sorted({(datetime.strptime(l["expiration_date"], "%Y-%m-%d").date() - ANCHOR).days for l in lots})
    print(f"  ✔ {os.path.abspath(OUT)}")
    print(f"    판매자 {len(sellers)} · 상품 {len(products)} · lot {len(lots)} · lot D-offset {offsets}")


if __name__ == "__main__":
    main()
