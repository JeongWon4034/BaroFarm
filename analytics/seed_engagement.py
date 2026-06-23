"""
FreshGrowth 참여(engagement) 더미 시드
========================================
유저·상품·주문이 적재된 뒤 실행. 그 위에 사용자 활동을 통계적으로 합성한다:
  reviews(후기) · wishlists(찜) · follows(팔로우) · posts/comments(게시판) · user_challenges(챌린지 참여)
마지막에 **확인용 테스트 계정**(소비자1·판매자1)을 기존 활동 많은 계정에 부여(이메일/비번 고정).

전제: seed_products_kamis.py --load → generate_dummy.py --load 가 먼저 실행됨.
실행: python3 seed_engagement.py            # CSV 미생성, DB에 바로 적재
      python3 seed_engagement.py --no-load  # 통계만 출력(미적재)
"""
import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

CONFIG = {
    "seed": 42,
    "review_rate": 0.5,          # COMPLETED 주문 중 후기 작성 비율
    "wishlist_lambda": 2.2,      # 구매자당 찜 수(Poisson)
    "follow_lambda": 1.6,        # 구매자당 팔로우 수(Poisson)
    "n_posts": 140,              # 추가 게시글 수(데모 시드와 별개)
    "comment_lambda": 2.4,       # 게시글당 댓글 수(Poisson)
    "reply_ratio": 0.3,          # 댓글 중 대댓글 비율
    "challenge_participants": 350,
    "pw_hash": "$2b$10$5I3GEXrJghnjSVepCQmjFucBk9jGYpPUDEAEQ5sOC.ltXkgnSSh4O",  # '1234'
    "db_url": os.getenv("DB_URL",
        "mysql+pymysql://root:1234@127.0.0.1:3306/freshgrowth?charset=utf8mb4"),
}

# 후기 문구 — 별점대별
REVIEW_TEXT = {
    "hi": ["신선하고 알차요. 또 살게요!", "배송도 빠르고 상태 최고예요.", "마감임박으로 싸게 샀는데 품질은 그대로네요.",
           "가족들이 다 좋아합니다. 재구매 확정.", "산지직송이라 그런지 확실히 신선해요.", "포장 꼼꼼하고 양도 넉넉합니다.",
           "이 가격에 이 퀄리티면 만족이에요.", "아이 간식으로 딱이에요. 당도 좋아요."],
    "mid": ["무난합니다. 가격대 생각하면 괜찮아요.", "보통이에요. 나쁘진 않습니다.",
            "배송은 좋았는데 신선도는 그냥 그래요.", "기대만큼은 아니지만 먹을 만해요."],
    "low": ["생각보다 좀 시들어서 왔어요.", "배송 중에 눌렸는지 상태가 아쉽네요.",
            "가격 대비 양이 적은 것 같아요.", "다음엔 다른 상품 살 것 같아요."],
}

# 게시판 — 카테고리별 (제목, 본문) 템플릿
POST_TPL = {
    "tip": [("{} 오래 보관하는 법", "키친타월로 감싸 밀폐용기에 넣으면 훨씬 오래가요. 마감임박으로 산 것도 안 버립니다."),
            ("냉장고 채소칸 정리 노하우", "잎채소는 위, 뿌리채소는 아래. 습도 관리가 핵심이에요."),
            ("{} 손질 꿀팁", "흐르는 물에 살짝, 결 따라 다듬으면 손질이 쉬워요.")],
    "recipe": [("{}로 만드는 간단 반찬", "기름 두르고 마늘 향 낸 뒤 볶기만 하면 끝. 5분 레시피예요."),
               ("{} 활용 레시피 공유", "마감임박으로 산 재료로 만들면 알뜰합니다. 사진 첨부해요."),
               ("주말 집밥 메뉴 추천", "제철 재료로 차린 한 상. 다들 뭐 해드세요?")],
    "question": [("{} 후숙 어떻게 하나요?", "덜 익은 걸 받았는데 빨리 익히는 방법 아시는 분?"),
                 ("{} 보관 온도 질문", "냉장이 좋을까요 냉동이 좋을까요? 며칠 안에 먹을 거예요."),
                 ("요즘 제철 뭐가 좋아요?", "이맘때 맛있는 거 추천 부탁드려요.")],
    "review": [("마감임박 떨이 후기", "반값에 장 봤어요. 떨이 탭 자주 보게 되네요."),
               ("{} 사봤어요 후기", "신선하고 좋네요. 재구매 의사 있습니다."),
               ("산지직송 써보니", "중간 유통이 없어서 그런지 확실히 다릅니다.")],
    "general": [("폐기 줄이기 같이 해요", "마감임박 상품 챙겨 사면 환경에도 좋고 지갑에도 좋아요."),
                ("{} 시세 요즘 어때요", "작년보다 오른 느낌인데 다들 어떻게 보시나요."),
                ("이 동네 산지직거래 좋네요", "신선하고 가격도 합리적이라 만족합니다.")],
}
POST_CAT_W = {"tip": 3, "recipe": 3, "question": 4, "review": 3, "general": 2}
COMMENT_TEXT = ["오 꿀팁이네요. 해볼게요!", "저도 그렇게 합니다 ㅎㅎ", "정보 감사해요~", "공감합니다.",
                "좋은 글이네요!", "저는 좀 다르게 하는데 참고할게요.", "사진 보니 군침 도네요.",
                "마감임박 자주 노립니다 ㅋㅋ", "재구매 의사 1표.", "이거 진짜 유용해요."]

KEYWORDS = ["청상추", "토마토", "감귤", "오징어", "한우", "시금치", "사과", "고등어", "양파", "딸기"]


def rand_dt(rng, start, end_days, after=None):
    base = after or start
    span = max(1, (start + timedelta(days=end_days) - base).days)
    return base + timedelta(days=int(rng.integers(0, span)),
                            seconds=int(rng.integers(0, 86400)))


def main(do_load=True):
    cfg = CONFIG
    rng = np.random.default_rng(cfg["seed"])
    from sqlalchemy import create_engine, text
    eng = create_engine(cfg["db_url"])
    start = datetime(2026, 1, 1)
    n_days = (datetime(2026, 6, 22) - start).days + 1

    with eng.connect() as c:
        buyers = [r[0] for r in c.execute(text("SELECT user_id FROM users WHERE role='BUYER'"))]
        sellers = [r[0] for r in c.execute(text("SELECT user_id FROM users WHERE role='SELLER'"))]
        products = [r[0] for r in c.execute(text("SELECT product_id FROM products"))]
        comp = pd.read_sql(text(
            "SELECT order_id, buyer_id, order_date FROM orders WHERE status='COMPLETED'"), c)
        challenges = [(r[0], r[1]) for r in c.execute(text("SELECT challenge_id, goal_count FROM challenges"))]
        max_post = c.execute(text("SELECT COALESCE(MAX(post_id),0) FROM posts")).scalar()
        max_comment = c.execute(text("SELECT COALESCE(MAX(comment_id),0) FROM comments")).scalar()
    buyers_arr, sellers_arr, products_arr = np.array(buyers), np.array(sellers), np.array(products)
    all_users = buyers + sellers

    # ── ① reviews: COMPLETED 주문의 일부 ──────────────────────────
    rev = comp.sample(frac=cfg["review_rate"], random_state=cfg["seed"]).copy()
    ratings = rng.choice([5, 4, 3, 2, 1], size=len(rev), p=[0.5, 0.28, 0.13, 0.06, 0.03])
    def _rtext(rt):
        pool = REVIEW_TEXT["hi"] if rt >= 4 else REVIEW_TEXT["mid"] if rt == 3 else REVIEW_TEXT["low"]
        return pool[rng.integers(0, len(pool))]
    reviews_df = pd.DataFrame({
        "order_id": rev["order_id"].values,
        "rating": ratings,
        "content": [_rtext(rt) for rt in ratings],
        "created_at": [(_d := pd.to_datetime(od)) and (_d + timedelta(days=int(rng.integers(1, 9)))).strftime("%Y-%m-%d %H:%M:%S")
                       for od in rev["order_date"].values],
    })

    # ── ② wishlists: 구매자당 찜 (user,product UNIQUE 보장) ───────
    w_rows = set()
    for b in buyers:
        for _ in range(int(rng.poisson(cfg["wishlist_lambda"]))):
            w_rows.add((b, int(rng.choice(products_arr))))
    wish_df = pd.DataFrame(list(w_rows), columns=["user_id", "product_id"])
    wish_df["created_at"] = [rand_dt(rng, start, n_days).strftime("%Y-%m-%d %H:%M:%S") for _ in range(len(wish_df))]

    # ── ③ follows: 구매자 → 판매자 (follower,following UNIQUE) ────
    f_rows = set()
    for b in buyers:
        for _ in range(int(rng.poisson(cfg["follow_lambda"]))):
            f_rows.add((b, int(rng.choice(sellers_arr))))
    follow_df = pd.DataFrame(list(f_rows), columns=["follower_id", "following_id"])
    follow_df["created_at"] = [rand_dt(rng, start, n_days).strftime("%Y-%m-%d %H:%M:%S") for _ in range(len(follow_df))]

    # ── ④ posts + comments (parent_id 연결 위해 명시 id) ──────────
    cats = list(POST_CAT_W); cw = np.array([POST_CAT_W[c] for c in cats], float); cw /= cw.sum()
    posts, comments = [], []
    pid, cid = max_post + 1, max_comment + 1
    for _ in range(cfg["n_posts"]):
        cat = cats[rng.choice(len(cats), p=cw)]
        title_t, body = POST_TPL[cat][rng.integers(0, len(POST_TPL[cat]))]
        kw = KEYWORDS[rng.integers(0, len(KEYWORDS))]
        created = rand_dt(rng, start, n_days)
        posts.append({"post_id": pid, "author_id": int(rng.choice(all_users)), "category": cat,
                      "title": title_t.format(kw), "content": body,
                      "view_count": int(rng.lognormal(3.5, 1.0)),
                      "created_at": created.strftime("%Y-%m-%d %H:%M:%S")})
        post_comment_ids = []
        for _ in range(int(rng.poisson(cfg["comment_lambda"]))):
            parent = None
            if post_comment_ids and rng.random() < cfg["reply_ratio"]:
                parent = int(rng.choice(post_comment_ids))
            comments.append({"comment_id": cid, "post_id": pid, "parent_id": parent,
                             "author_id": int(rng.choice(all_users)),
                             "content": COMMENT_TEXT[rng.integers(0, len(COMMENT_TEXT))],
                             "created_at": rand_dt(rng, start, n_days, after=created).strftime("%Y-%m-%d %H:%M:%S")})
            post_comment_ids.append(cid); cid += 1
        pid += 1
    posts_df = pd.DataFrame(posts)
    comments_df = pd.DataFrame(comments)

    # ── ⑤ user_challenges: 일부 구매자 참여 (user,challenge UNIQUE) ─
    uc_rows = set()
    uc = []
    parts = rng.choice(buyers_arr, size=min(cfg["challenge_participants"], len(buyers)), replace=False)
    for b in parts:
        for ch_id, goal in challenges:
            if rng.random() < 0.5 and (int(b), ch_id) not in uc_rows:
                uc_rows.add((int(b), ch_id))
                prog = int(rng.integers(0, goal + 2))
                done = prog >= goal
                joined = rand_dt(rng, start, n_days)
                uc.append({"user_id": int(b), "challenge_id": ch_id,
                           "status": "COMPLETED" if done else "ONGOING",
                           "progress": min(prog, goal), "joined_at": joined.strftime("%Y-%m-%d %H:%M:%S"),
                           "completed_at": (joined + timedelta(days=int(rng.integers(1, 10)))).strftime("%Y-%m-%d %H:%M:%S") if done else None})
    uc_df = pd.DataFrame(uc)

    _summary(reviews_df, wish_df, follow_df, posts_df, comments_df, uc_df)
    if not do_load:
        print("  (--no-load: DB 미변경)"); return

    # ── 적재 (FK 순서: posts→comments) ───────────────────────────
    for df, table in [(reviews_df, "reviews"), (wish_df, "wishlists"), (follow_df, "follows"),
                      (posts_df, "posts"), (comments_df, "comments"), (uc_df, "user_challenges")]:
        if len(df):
            df.where(pd.notnull(df), None).to_sql(table, eng, if_exists="append", index=False,
                                                  method="multi", chunksize=1_000)
            print(f"  ✔ {table}: {len(df):,} rows")

    creds = assign_test_accounts(eng, cfg)
    print("\n" + "=" * 56)
    print("  확인용 테스트 계정 (비밀번호 모두 1234)")
    print("=" * 56)
    for role, em, name, extra in creds:
        print(f"  {role:<7} {em:<22} pw=1234   {name} · {extra}")
    print("=" * 56)


def assign_test_accounts(eng, cfg):
    """활동 많은 기존 계정을 확인용 테스트 계정으로 지정(이메일·비번 고정)."""
    from sqlalchemy import text
    with eng.begin() as c:
        # 재실행 안전: 기존 테스트 이메일 원복(UNIQUE 충돌 방지)
        c.execute(text("UPDATE users SET email=CONCAT('buyer', user_id, '@fresh.test') WHERE email='buyer1@test.com'"))
        c.execute(text("UPDATE users SET email=CONCAT('kseller', user_id, '@fresh.test') WHERE email='seller1@test.com'"))
        top_buyer = c.execute(text("SELECT buyer_id FROM orders GROUP BY buyer_id ORDER BY COUNT(*) DESC LIMIT 1")).scalar()
        # 받은 주문이 가장 많은 판매자 → 판매자 대시보드에 처리할 주문이 실제로 보임
        top_seller = c.execute(text(
            "SELECT p.seller_id FROM orders o JOIN products p ON o.product_id=p.product_id "
            "GROUP BY p.seller_id ORDER BY COUNT(*) DESC LIMIT 1")).scalar()
        b_orders = c.execute(text("SELECT COUNT(*) FROM orders WHERE buyer_id=:i"), {"i": top_buyer}).scalar()
        b_rev = c.execute(text("SELECT COUNT(*) FROM reviews r JOIN orders o ON r.order_id=o.order_id WHERE o.buyer_id=:i"), {"i": top_buyer}).scalar()
        s_prod = c.execute(text("SELECT COUNT(*) FROM products WHERE seller_id=:i"), {"i": top_seller}).scalar()
        s_ord = c.execute(text("SELECT COUNT(*) FROM orders o JOIN products p ON o.product_id=p.product_id WHERE p.seller_id=:i"), {"i": top_seller}).scalar()
        c.execute(text("UPDATE users SET email='buyer1@test.com', name='테스트소비자', password=:pw, status='ACTIVE' WHERE user_id=:i"),
                  {"pw": cfg["pw_hash"], "i": top_buyer})
        c.execute(text("UPDATE users SET email='seller1@test.com', name='테스트농장', password=:pw, status='ACTIVE' WHERE user_id=:i"),
                  {"pw": cfg["pw_hash"], "i": top_seller})
    return [("소비자", "buyer1@test.com", "테스트소비자", f"주문 {b_orders}건·후기 {b_rev}건"),
            ("판매자", "seller1@test.com", "테스트농장", f"상품 {s_prod}개·받은주문 {s_ord}건")]


def _summary(reviews, wish, follow, posts, comments, uc):
    print("=" * 56)
    print("  참여 데이터 생성")
    print("=" * 56)
    print(f"  reviews          {len(reviews):>8,}  (평균 별점 {reviews['rating'].mean():.2f})")
    print(f"  wishlists        {len(wish):>8,}")
    print(f"  follows          {len(follow):>8,}")
    print(f"  posts            {len(posts):>8,}  + comments {len(comments):,}")
    print(f"  user_challenges  {len(uc):>8,}")
    print("=" * 56)


if __name__ == "__main__":
    main(do_load="--no-load" not in sys.argv)
