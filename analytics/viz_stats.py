"""
FreshGrowth 소비자·판매자 통계 시각화 (확인용)
================================================
MySQL(freshgrowth)에서 직접 읽어 소비자·판매자 KPI를 계산하고 차트로 저장한다.
  소비자: 주문수 분포 / 카테고리 비중 / 월별 추이 / 후기 별점 분포
  판매자: 매출 Top / 받은주문 Top / 평균별점 분포 / 폐기회수 절약 Top
산출물: analytics/data/charts/consumers.png, sellers.png  (+ 콘솔 요약)
실행: python3 viz_stats.py
"""
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sqlalchemy import create_engine

# 한글 폰트 (macOS)
plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

DB_URL = os.getenv("DB_URL", "mysql+pymysql://root:1234@127.0.0.1:3306/freshgrowth?charset=utf8mb4")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "charts")
CAT_KR = {"vegetable": "채소", "fruit": "과일", "seafood": "해산물",
          "meat": "육류", "grain": "곡물", "processed": "가공"}


def load():
    eng = create_engine(DB_URL)
    # 주문 + 상품(판매자·카테고리) + 정가/절약
    orders = pd.read_sql("""
        SELECT o.order_id, o.buyer_id, o.order_date, o.quantity, o.total_price,
               o.original_unit_price, o.status,
               p.seller_id, p.category, u.name AS seller_name
        FROM orders o JOIN products p ON o.product_id=p.product_id
                      JOIN users u    ON p.seller_id=u.user_id
    """, eng)
    reviews = pd.read_sql("""
        SELECT r.rating, p.seller_id
        FROM reviews r JOIN orders o ON r.order_id=o.order_id
                       JOIN products p ON o.product_id=p.product_id
    """, eng)
    orders["order_date"] = pd.to_datetime(orders["order_date"])
    orders["month"] = orders["order_date"].dt.strftime("%Y-%m")
    orders["saved"] = (orders["original_unit_price"].fillna(0) * orders["quantity"]
                       - orders["total_price"]).clip(lower=0)
    return orders, reviews


def consumers_fig(orders, reviews):
    fig, ax = plt.subplots(2, 2, figsize=(13, 9))
    fig.suptitle("소비자 통계 (FreshGrowth)", fontsize=16, fontweight="bold")

    # ① 구매자별 주문수 분포
    per_buyer = orders.groupby("buyer_id").size()
    ax[0, 0].hist(per_buyer, bins=range(1, per_buyer.max() + 2), color="#5b8c3e", edgecolor="white")
    ax[0, 0].set_title(f"구매자별 주문 수 분포 (구매자 {per_buyer.size:,}명, 평균 {per_buyer.mean():.1f}건)")
    ax[0, 0].set_xlabel("주문 수"); ax[0, 0].set_ylabel("구매자 수")

    # ② 카테고리별 주문 비중
    cat = orders["category"].map(lambda c: CAT_KR.get(c, c)).value_counts()
    ax[0, 1].bar(cat.index, cat.values, color="#e08a3c")
    ax[0, 1].set_title("카테고리별 주문 건수"); ax[0, 1].set_ylabel("주문")

    # ③ 월별 주문 추이
    mon = orders.groupby("month").size()
    ax[1, 0].plot(mon.index, mon.values, marker="o", color="#2f6f4f", linewidth=2)
    ax[1, 0].set_title("월별 주문 추이"); ax[1, 0].set_ylabel("주문"); ax[1, 0].grid(alpha=.3)

    # ④ 후기 별점 분포
    rt = reviews["rating"].value_counts().sort_index()
    ax[1, 1].bar(rt.index.astype(str), rt.values, color="#c9a227")
    ax[1, 1].set_title(f"후기 별점 분포 (후기 {len(reviews):,}건, 평균 {reviews['rating'].mean():.2f}★)")
    ax[1, 1].set_xlabel("별점"); ax[1, 1].set_ylabel("후기 수")

    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(f"{OUT}/consumers.png", dpi=110)
    return per_buyer


def sellers_fig(orders, reviews):
    fig, ax = plt.subplots(2, 2, figsize=(13, 9))
    fig.suptitle("판매자 통계 (FreshGrowth)", fontsize=16, fontweight="bold")

    by_seller = orders.groupby("seller_name").agg(
        revenue=("total_price", "sum"), n_orders=("order_id", "size"), saved=("saved", "sum"))

    # ① 매출 Top10
    top_rev = by_seller["revenue"].sort_values(ascending=False).head(10)[::-1]
    ax[0, 0].barh(top_rev.index, top_rev.values / 1e6, color="#5b8c3e")
    ax[0, 0].set_title("판매자별 매출 Top10 (백만원)"); ax[0, 0].set_xlabel("백만원")

    # ② 받은 주문 Top10
    top_ord = by_seller["n_orders"].sort_values(ascending=False).head(10)[::-1]
    ax[0, 1].barh(top_ord.index, top_ord.values, color="#e08a3c")
    ax[0, 1].set_title("판매자별 받은 주문 Top10")

    # ③ 판매자 평균 별점 분포
    avg = reviews.groupby("seller_id")["rating"].mean()
    ax[1, 0].hist(avg, bins=12, color="#c9a227", edgecolor="white")
    ax[1, 0].set_title(f"판매자 평균 별점 분포 (판매자 {avg.size}명)")
    ax[1, 0].set_xlabel("평균 별점"); ax[1, 0].set_ylabel("판매자 수")

    # ④ 폐기회수 절약 Top10
    top_sav = by_seller["saved"].sort_values(ascending=False).head(10)[::-1]
    ax[1, 1].barh(top_sav.index, top_sav.values / 1e6, color="#2f6f4f")
    ax[1, 1].set_title("판매자별 폐기회수 절약 Top10 (백만원)"); ax[1, 1].set_xlabel("백만원")

    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(f"{OUT}/sellers.png", dpi=110)
    return by_seller


def main():
    os.makedirs(OUT, exist_ok=True)
    orders, reviews = load()
    per_buyer = consumers_fig(orders, reviews)
    by_seller = sellers_fig(orders, reviews)

    print("=" * 58)
    print("  소비자 통계")
    print("=" * 58)
    print(f"  구매자            {per_buyer.size:>8,} 명")
    print(f"  총 주문           {len(orders):>8,} 건  (1인당 평균 {per_buyer.mean():.1f})")
    print(f"  재구매자 비율      {(per_buyer >= 2).mean()*100:>7.1f} %")
    print(f"  객단가(AOV)       {orders['total_price'].mean():>8,.0f} 원")
    print(f"  후기              {len(reviews):>8,} 건  (평균 {reviews['rating'].mean():.2f}★)")
    print("=" * 58)
    print("  판매자 통계")
    print("=" * 58)
    print(f"  판매자            {by_seller.shape[0]:>8,} 명")
    print(f"  총 매출(GMV)      {by_seller['revenue'].sum():>13,.0f} 원")
    print(f"  폐기회수 절약      {by_seller['saved'].sum():>13,.0f} 원")
    top = by_seller['revenue'].sort_values(ascending=False).head(3)
    print("  매출 Top3:")
    for name, rev in top.items():
        print(f"    - {name:<18} {rev:>12,.0f} 원")
    print("=" * 58)
    print(f"  차트 저장: {OUT}/consumers.png, sellers.png")


if __name__ == "__main__":
    main()
