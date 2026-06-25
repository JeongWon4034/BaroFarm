"""
data/dummy/{users,orders}.csv  →  analytics_reflex/deploy/seed_orders.sql
=====================================================================
generate_dummy.py 가 떨군 구매자(users)·주문(orders) CSV 를 analytics_reflex
단독 배포 전용 정적 시드로 박제한다.

설계 메모
  · 이 파일은 backend/src/main/resources 가 아니라 analytics_reflex/deploy 에
    둔다 → Java(Spring) 백엔드가 줍지 않도록 격리(양쪽 참조 충돌 방지).
  · docker-entrypoint-initdb.d 04 단계로 첫 기동 시 1회 실행.
    (01 schema → 02 seed_testdata → 03 seed_products_kamis → 04 이 파일)
  · order_id 는 02-seed 의 소수 주문과 PK 충돌을 피하려 +OFFSET 한다.
  · lot_id 일부 결번/buyer FK 등은 SET FOREIGN_KEY_CHECKS=0 로 무시(시드 관용).
  · SET NAMES utf8mb4 로 한글(구매자명) 이중 인코딩 방지.

실행:  python3 csv_to_orders_seed.py
"""
import os
import csv

BASE = os.path.dirname(os.path.abspath(__file__))
CSV_DIR = os.path.join(BASE, "data", "dummy")
OUT = os.path.join(BASE, "..", "analytics_reflex", "deploy", "seed_orders.sql")
ORDER_ID_OFFSET = 100_000      # 02-seed 의 기존 주문과 PK 충돌 회피
BATCH = 1_000                  # 멀티로우 INSERT 묶음 크기


def q(v):
    if v is None or v == "":
        return "NULL"
    return "'" + str(v).replace("\\", "\\\\").replace("'", "''") + "'"


def read(name):
    with open(os.path.join(CSV_DIR, f"{name}.csv"), encoding="utf-8") as f:
        return list(csv.DictReader(f))


def emit_batched(L, header, rows):
    """rows(=각 행 '(...)' 문자열 리스트)를 BATCH 단위 멀티로우 INSERT 로."""
    for i in range(0, len(rows), BATCH):
        chunk = rows[i:i + BATCH]
        L.append(header)
        L.append(",\n".join(chunk) + ";")
        L.append("")


def main():
    users, orders = read("users"), read("orders")
    L = []
    L.append("-- 자동 생성: analytics/csv_to_orders_seed.py (직접 수정 금지)")
    L.append(f"-- 구매자 {len(users)} · 주문 {len(orders)} · order_id +{ORDER_ID_OFFSET} 오프셋")
    L.append("-- analytics_reflex 단독 배포 전용 시드(initdb 04). Java 백엔드는 미참조.")
    L.append("SET NAMES utf8mb4;")
    L.append("SET FOREIGN_KEY_CHECKS=0;")
    L.append("")

    # 1) 구매자(users) — role=BUYER
    uhdr = ("INSERT INTO users (user_id, role, email, password, name, intro, phone, status, created_at) VALUES")
    urows = [f"  ({u['user_id']}, {q(u['role'])}, {q(u['email'])}, {q(u['password'])}, "
             f"{q(u['name'])}, {q(u['intro'])}, {q(u['phone'])}, {q(u['status'])}, {q(u['created_at'])})"
             for u in users]
    emit_batched(L, uhdr, urows)

    # 2) 주문(orders) — order_id 오프셋
    ohdr = ("INSERT INTO orders (order_id, buyer_id, product_id, lot_id, quantity, "
            "total_price, original_unit_price, status, order_date) VALUES")
    orows = [f"  ({int(o['order_id']) + ORDER_ID_OFFSET}, {o['buyer_id']}, {o['product_id']}, "
             f"{o['lot_id']}, {o['quantity']}, {o['total_price']}, {o['original_unit_price']}, "
             f"{q(o['status'])}, {q(o['order_date'])})"
             for o in orders]
    emit_batched(L, ohdr, orows)

    L.append("SET FOREIGN_KEY_CHECKS=1;")
    L.append("")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    print(f"  ✔ {os.path.abspath(OUT)}")
    print(f"    구매자 {len(users):,} · 주문 {len(orders):,}")


if __name__ == "__main__":
    main()
