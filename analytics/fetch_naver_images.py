"""
네이버 쇼핑 검색 → 상품 이미지 자체호스팅 매핑기
==================================================
DB의 상품마다 상품명을 네이버 쇼핑 검색에 넣고, 가장 잘 맞는 결과의 대표 이미지를
**다운로드**해서 frontend/public/seed-images/p<id>.jpg 에 저장한다(외부 핫링크 X).
그리고 products.thumbnail_url 을 '/seed-images/p<id>.jpg' 로 갱신하며,
배포 재현용 UPDATE SQL(backend/.../seed_product_images.sql)을 함께 생성한다.

핫링크(컬리/네이버 URL 노출)와 달리, 이미지를 우리 정적 폴더에 담아 배포에서도
절대 안 깨지고 외부 의존이 없다. 네이버 검색 API(라이선스)로만 후보를 찾는다.

환경변수: NAVER_CLIENT_ID / NAVER_CLIENT_SECRET, DB_URL(기본 로컬 docker mysql)

실행
  python3 fetch_naver_images.py --dry-run -n 5      # 매칭만 미리보기(다운로드·DB 미변경)
  python3 fetch_naver_images.py --load              # 다운로드 + DB 갱신 + SQL 생성
  python3 fetch_naver_images.py --load --stocked-only  # 재고>0(노출되는) 상품만
"""
import os
import re
import sys
import time
import json
import argparse
import urllib.parse
import urllib.request

API = "https://openapi.naver.com/v1/search/shop.json"
DB_URL = os.getenv("DB_URL", "mysql+pymysql://root:1234@127.0.0.1:3306/freshgrowth?charset=utf8mb4")
CID = os.getenv("NAVER_CLIENT_ID", "")
CSECRET = os.getenv("NAVER_CLIENT_SECRET", "")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
IMG_DIR = os.path.join(REPO, "frontend", "public", "seed-images")
SQL_OUT = os.path.join(REPO, "backend", "src", "main", "resources", "seed_product_images.sql")

MODIFIERS = {"무농약", "유기농", "친환경", "국산", "국내산", "산지직송", "산지", "직송", "당일수확",
             "수확", "프리미엄", "특", "특품", "명품", "햇", "손질", "세척", "냉장", "냉동",
             "생물", "선물", "선물용", "가정용", "못난이", "정품", "고당도", "꿀"}


def core_term(name):
    """'양파/양파 (1kg)' → '양파', '무농약 청상추' → '청상추' (수식어·단위 제거 후 핵심 명사)."""
    s = name.split("/")[0].split("(")[0].strip()
    toks = [t for t in re.split(r"\s+", s) if len(t) >= 2 and t not in MODIFIERS and not re.search(r"\d", t)]
    return max(toks, key=len) if toks else s


def search(name, retries=2, timeout=15):
    """상품명 → (이미지URL, 매칭제목). 핵심 명사 포함 결과 우선, 없으면 첫 결과."""
    q = urllib.parse.urlencode({"query": name.strip(), "display": 5, "sort": "sim"})
    req = urllib.request.Request(f"{API}?{q}",
                                 headers={"X-Naver-Client-Id": CID, "X-Naver-Client-Secret": CSECRET})
    term = core_term(name)
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                items = json.load(r).get("items", [])
            if not items:
                return None, None
            picked = next((it for it in items if term in re.sub(r"<[^>]+>", "", it.get("title", ""))), items[0])
            return picked.get("image"), re.sub(r"<[^>]+>", "", picked.get("title", ""))
        except Exception as e:  # noqa: BLE001
            time.sleep(0.6 * (attempt + 1))
            last = e
    print(f"    ! 검색 실패: {name!r} ({last})", file=sys.stderr)
    return None, None


def download(url, dest, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://shopping.naver.com"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = r.read()
    if len(data) < 800:  # 깨진/빈 이미지 방지
        raise ValueError("too small")
    with open(dest, "wb") as f:
        f.write(data)


def fetch_products(eng, stocked_only):
    from sqlalchemy import text
    where = "WHERE stock_qty > 0" if stocked_only else ""
    with eng.connect() as c:
        return [(int(r[0]), r[1]) for r in
                c.execute(text(f"SELECT product_id, name FROM products {where} ORDER BY product_id"))]


def run(dry_run, stocked_only, limit, sleep_sec):
    if not CID or not CSECRET:
        sys.exit("NAVER_CLIENT_ID / NAVER_CLIENT_SECRET 환경변수를 설정하세요.")
    from sqlalchemy import create_engine, text
    eng = create_engine(DB_URL)
    products = fetch_products(eng, stocked_only)
    if limit:
        products = products[:limit]
    if not products:
        print("  · 대상 상품이 없습니다."); return

    os.makedirs(IMG_DIR, exist_ok=True)
    print(f"  · 대상 {len(products):,}개 — 네이버 검색·다운로드{' (DRY-RUN)' if dry_run else ''}")
    updates, matched, missed = [], 0, 0
    for i, (pid, name) in enumerate(products, 1):
        img, hit = search(name)
        if not img:
            missed += 1
            print(f"  [{i}/{len(products)}] · {name}  →  (매칭 없음, 이모지 유지)")
            time.sleep(sleep_sec); continue
        rel = f"/seed-images/p{pid}.jpg"
        if not dry_run:
            try:
                download(img, os.path.join(IMG_DIR, f"p{pid}.jpg"))
            except Exception as e:  # noqa: BLE001
                missed += 1
                print(f"  [{i}/{len(products)}] ! {name}  →  다운로드 실패({e}), 이모지 유지", file=sys.stderr)
                time.sleep(sleep_sec); continue
        matched += 1
        updates.append((pid, rel))
        print(f"  [{i}/{len(products)}] ✓ {name}  →  {hit}")
        time.sleep(sleep_sec)

    print(f"\n  결과: 매칭 {matched:,} / 미매칭 {missed:,}")
    if dry_run:
        print("  (dry-run: 다운로드·DB 미변경. --load 로 실제 적용)"); return
    if not updates:
        return
    with eng.begin() as c:
        for pid, url in updates:
            c.execute(text("UPDATE products SET thumbnail_url=:u WHERE product_id=:p"), {"u": url, "p": pid})
    with open(SQL_OUT, "w", encoding="utf-8") as f:
        f.write("-- 자체호스팅 상품 이미지(네이버 검색 → frontend/public/seed-images 다운로드).\n")
        f.write("-- 배포 재현용: docker-entrypoint-initdb.d 04-images.sql 로 실행됨.\n")
        for pid, url in updates:
            f.write(f"UPDATE products SET thumbnail_url='{url}' WHERE product_id={pid};\n")
    print(f"  ✔ DB {len(updates):,}건 갱신 + 이미지 저장({IMG_DIR}) + SQL 생성({SQL_OUT})")


def main():
    ap = argparse.ArgumentParser(description="네이버 검색으로 상품 이미지 자체호스팅")
    ap.add_argument("--load", action="store_true", help="다운로드+DB 갱신(없으면 dry-run)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--stocked-only", action="store_true", help="재고>0 상품만")
    ap.add_argument("-n", "--limit", type=int, default=0)
    ap.add_argument("--sleep", type=float, default=0.2)
    a = ap.parse_args()
    run(not a.load or a.dry_run, a.stocked_only, a.limit, a.sleep)


if __name__ == "__main__":
    main()
