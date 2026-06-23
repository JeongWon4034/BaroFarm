"""
마켓컬리 검색 → products.thumbnail_url 자동 매핑기
====================================================
DB의 모든 상품에 대해, 상품명을 마켓컬리 검색에 넣고 첫 번째 검색 결과의
대표 이미지 URL 을 가져와 products.thumbnail_url 에 채운다.
(예: "유기농 양파 1.5kg" → 검색 1번 상품 "[바름팜] 유기농 양파 1.5kg" 의 사진)

매칭이 안 되면 thumbnail_url 을 건드리지 않는다(NULL 유지) → 프론트가 기존처럼
이모지 썸네일로 폴백한다.

검색 API (브라우저 검색페이지가 내부적으로 부르는 공개 JSON):
  https://api.kurly.com/search/v4/sites/market/normal-search
  ?keyword=...&sort_type=1&page=1&per_page=N
  data.listSections[ sectionCode=PRODUCT_LIST ].data.items[].listImageUrl

DB 연결은 seed_products_kamis.py 와 동일하게 DB_URL 환경변수(기본 로컬 docker mysql).

실행
  python3 fetch_kurly_images.py --dry-run        # 검색·매핑만 출력, DB 미변경 (검증용)
  python3 fetch_kurly_images.py --dry-run -n 20  # 앞 20개만 미리보기
  python3 fetch_kurly_images.py --load           # DB products.thumbnail_url 갱신
  python3 fetch_kurly_images.py --load --only-missing  # 아직 비어있는 것만 채움
"""
import os
import sys
import time
import json
import argparse
import urllib.parse
import urllib.request

SEARCH_URL = "https://api.kurly.com/search/v4/sites/market/normal-search"
DB_URL = os.getenv("DB_URL",
    "mysql+pymysql://root:1234@127.0.0.1:3306/freshgrowth?charset=utf8mb4")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept": "application/json",
    "Referer": "https://www.kurly.com/search",
}


def search_image(keyword, retries=2, timeout=15):
    """상품명으로 컬리 검색 → 첫 PRODUCT_LIST 상품의 (이미지URL, 매칭상품명).
    결과 없으면 (None, None)."""
    qs = urllib.parse.urlencode({
        "keyword": keyword, "sort_type": 1, "page": 1, "per_page": 3,
    })
    url = f"{SEARCH_URL}?{qs}"
    last_err = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                payload = json.load(r)
            for sec in payload.get("data", {}).get("listSections", []):
                if sec.get("view", {}).get("sectionCode") == "PRODUCT_LIST":
                    items = sec.get("data", {}).get("items", [])
                    if not items:
                        return None, None
                    top = items[0]
                    img = top.get("listImageUrl") or top.get("productVerticalMediumUrl")
                    return (img or None), top.get("name")
            return None, None
        except Exception as e:                         # noqa: BLE001 (네트워크/파싱 모두 재시도)
            last_err = e
            time.sleep(0.6 * (attempt + 1))
    print(f"    ! 검색 실패: {keyword!r} ({last_err})", file=sys.stderr)
    return None, None


def fetch_products(eng, only_missing):
    from sqlalchemy import text
    where = "WHERE thumbnail_url IS NULL OR thumbnail_url = ''" if only_missing else ""
    sql = f"SELECT product_id, name FROM products {where} ORDER BY product_id"
    with eng.connect() as c:
        return [(int(r[0]), r[1]) for r in c.execute(text(sql))]


def apply_updates(eng, updates):
    """updates = [(product_id, url), ...] → products.thumbnail_url 일괄 갱신."""
    from sqlalchemy import text
    stmt = text("UPDATE products SET thumbnail_url = :url WHERE product_id = :pid")
    with eng.begin() as c:
        for pid, url in updates:
            c.execute(stmt, {"url": url, "pid": pid})


def run(dry_run, only_missing, limit, sleep_sec):
    from sqlalchemy import create_engine
    eng = create_engine(DB_URL)
    products = fetch_products(eng, only_missing)
    if limit:
        products = products[:limit]
    if not products:
        print("  · 대상 상품이 없습니다."); return

    print(f"  · 대상 {len(products):,}개 상품 — 컬리 검색 시작"
          f"{' (DRY-RUN: DB 미변경)' if dry_run else ''}")
    updates, matched, missed = [], 0, 0
    for i, (pid, name) in enumerate(products, 1):
        img, hit_name = search_image(name)
        if img:
            matched += 1
            updates.append((pid, img))
            print(f"  [{i}/{len(products)}] ✓ {name}  →  {hit_name}")
        else:
            missed += 1
            print(f"  [{i}/{len(products)}] · {name}  →  (매칭 없음, 이모지 유지)")
        time.sleep(sleep_sec)

    print(f"\n  결과: 매칭 {matched:,} / 미매칭 {missed:,} (전체 {len(products):,})")
    if dry_run:
        print("  (dry-run: DB 미변경. --load 로 실제 갱신)")
        return
    if updates:
        apply_updates(eng, updates)
        print(f"  ✔ products.thumbnail_url {len(updates):,}건 갱신 완료")


def main():
    ap = argparse.ArgumentParser(description="마켓컬리 검색으로 products.thumbnail_url 채우기")
    ap.add_argument("--load", action="store_true", help="DB 실제 갱신 (없으면 dry-run)")
    ap.add_argument("--dry-run", action="store_true", help="검색·매핑만 출력")
    ap.add_argument("--only-missing", action="store_true",
                    help="thumbnail_url 이 비어있는 상품만 처리")
    ap.add_argument("-n", "--limit", type=int, default=0, help="앞 N개만 처리(검증용)")
    ap.add_argument("--sleep", type=float, default=0.25, help="요청 간 대기초(기본 0.25)")
    args = ap.parse_args()
    dry_run = not args.load or args.dry_run
    run(dry_run, args.only_missing, args.limit, args.sleep)


if __name__ == "__main__":
    main()
