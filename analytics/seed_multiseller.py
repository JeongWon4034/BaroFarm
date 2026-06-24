"""
멀티 판매처 시드 — 같은 품목을 여러 판매처가 서로 다른 D-day·가격으로 팔도록 추가.
바로팜 안에서 '상품 가격 비교'가 가능해지게 만든다(같은 name = 같은 품목으로 묶임).

각 주요 상품(id<=13)마다 2개 판매처 버전을 추가:
  - 판매처: 원 판매자와 다른 셀러 풀에서 선택(이름 있는 농장 우선)
  - 가격: 원가 ±  (비교가 의미 있도록 차등)
  - D-day: 다양하게(폐기임박~여유 골고루) — expiration은 DATE_ADD(CURDATE(), INTERVAL n DAY)
  - 이미지: 같은 품목이라 원본 thumbnail 공유(/seed-images/p<id>.jpg)

배포 재현용 seed_multiseller.sql 생성(05-multiseller.sql 로 마운트). 재실행 시 '[멀티판매처]' 마커로 멱등.

실행: NAVER 키 불필요. DB_URL만 필요.
  python3 seed_multiseller.py
"""
import os
from sqlalchemy import create_engine, text

DB_URL = os.getenv("DB_URL", "mysql+pymysql://root:1234@127.0.0.1:3306/freshgrowth?charset=utf8mb4")
HERE = os.path.dirname(os.path.abspath(__file__))
SQL_OUT = os.path.join(os.path.dirname(HERE), "backend", "src", "main", "resources", "seed_multiseller.sql")
MARK = "[멀티판매처]"

# 판매처 풀(이름 있는 농장 우선). (seller_id, 표시명) — 실제 users 행 기준.
POOL = [1, 1001, 1002, 1003, 11, 26, 27, 12]

# 상품별 2개 버전의 (D-day, 가격배수) — D-day가 폐기임박~여유 골고루 퍼지게
DDAY_A = [2, 5, 9, 12, 3, 8, 11, 4, 7, 13, 6, 10, 2]
DDAY_B = [10, 8, 3, 6, 13, 4, 9, 12, 2, 7, 11, 5, 8]
PF_A = 0.90  # 더 싼 판매처
PF_B = 1.08  # 더 비싼 판매처


def round100(v):
    return max(int(round(v / 100.0) * 100), 100)


def main():
    eng = create_engine(DB_URL)
    with eng.connect() as c:
        mains = [(int(r[0]), r[1], r[2], int(r[3]), int(r[4])) for r in c.execute(text(
            "SELECT product_id, name, category, price, seller_id FROM products WHERE product_id<=13 ORDER BY product_id"))]
        names = {int(r[0]): r[1] for r in c.execute(text(
            "SELECT user_id, name FROM users WHERE role='SELLER'"))}

    stmts = []
    for idx, (pid, name, cat, price, orig_seller) in enumerate(mains):
        sellers = [s for s in POOL if s != orig_seller]
        for j, (seller, dday, pf, stock) in enumerate([
                (sellers[(2 * idx) % len(sellers)], DDAY_A[idx], PF_A, 12 + (idx % 5) * 6),
                (sellers[(2 * idx + 1) % len(sellers)], DDAY_B[idx], PF_B, 8 + (idx % 4) * 5)]):
            sname = names.get(seller, "산지농장")
            nm = name.replace("'", "''")
            desc = f"{MARK} {sname} 산지직송".replace("'", "''")
            p = round100(price * pf)
            stmts.append(
                "INSERT INTO products (seller_id,name,description,category,price,stock_qty,thumbnail_url,expiration_date) "
                f"VALUES ({seller},'{nm}','{desc}','{cat}',{p},{stock},'/seed-images/p{pid}.jpg',"
                f"DATE_ADD(CURDATE(),INTERVAL {dday} DAY));")

    with eng.begin() as c:
        c.execute(text(f"DELETE FROM products WHERE description LIKE '{MARK}%'"))  # 멱등
        for s in stmts:
            c.execute(text(s))
    with open(SQL_OUT, "w", encoding="utf-8") as f:
        f.write("-- 멀티 판매처 시드: 같은 품목을 여러 판매처가 다른 D-day·가격으로 판매(가격 비교용).\n")
        f.write("-- 배포 재현용: docker-entrypoint-initdb.d 05-multiseller.sql 로 실행됨.\n")
        f.write(f"DELETE FROM products WHERE description LIKE '{MARK}%';\n")
        for s in stmts:
            f.write(s + "\n")
    print(f"✔ 멀티 판매처 {len(stmts)}건 추가(주요 {len(mains)}품목 × 2판매처) + SQL 생성({SQL_OUT})")


if __name__ == "__main__":
    main()
