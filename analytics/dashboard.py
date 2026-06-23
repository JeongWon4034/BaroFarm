"""
BaroFarm 실시간 통계 대시보드 (DB 직결)
=============================================
SQL(baroFarm)에서 바로 읽어 소비자·판매자 통계를 띄운다.
이 파일을 저장(⌘S)하면 브라우저가 자동 새로고침 → 코드 고치며 실시간 확인.

실행:
    cd analytics
    streamlit run dashboard.py        # → http://localhost:8501

수정 포인트는 아래 [✏️ EDIT] 주석을 찾으면 된다.
"""
import os
import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine, text

# ── DB 연결 (도커 MySQL) ───────────────────────────────────────────
DB_URL = os.getenv("DB_URL", "mysql+pymysql://root:1234@127.0.0.1:3306/freshgrowth?charset=utf8mb4")


@st.cache_resource
def get_engine():
    return create_engine(DB_URL)


@st.cache_data(ttl=60)   # 60초 캐시 → DB가 바뀌면 사이드바 '데이터 새로고침'으로 즉시 반영
def q(sql: str) -> pd.DataFrame:
    """[✏️ EDIT] SQL 한 줄 바꾸면 통계가 바뀐다. 아무 쿼리나 넣어 써도 됨."""
    return pd.read_sql(text(sql), get_engine())


CAT_KR = {"vegetable": "채소", "fruit": "과일", "seafood": "해산물",
          "meat": "육류", "grain": "곡물", "processed": "가공"}

st.set_page_config(page_title="BaroFarm 통계", layout="wide")
st.title("🥬 BaroFarm 통계 대시보드 (SQL 직결)")

# ── 사이드바: 필터 ─────────────────────────────────────────────────
with st.sidebar:
    st.header("필터")
    if st.button("🔄 데이터 새로고침"):
        st.cache_data.clear()
        st.rerun()
    # [✏️ EDIT] 기간/카테고리 필터 — 기본값만 바꿔도 됨
    dmin, dmax = q("SELECT MIN(order_date) a, MAX(order_date) b FROM orders").iloc[0]
    date_range = st.date_input("주문 기간", value=(pd.to_datetime(dmin), pd.to_datetime(dmax)))
    cats = st.multiselect("카테고리", list(CAT_KR), default=list(CAT_KR),
                          format_func=lambda c: CAT_KR[c])

d0, d1 = (str(date_range[0]), str(date_range[1])) if len(date_range) == 2 else (str(dmin), str(dmax))
cat_in = "(" + ",".join(f"'{c}'" for c in cats) + ")" if cats else "('')"
WHERE = f"o.order_date BETWEEN '{d0} 00:00:00' AND '{d1} 23:59:59' AND p.category IN {cat_in}"

# 공통 주문 데이터 (필터 적용) — [✏️ EDIT] 컬럼 추가하면 모든 탭에서 사용 가능
orders = q(f"""
    SELECT o.order_id, o.buyer_id, o.order_date, o.quantity, o.total_price,
           o.original_unit_price, o.status, p.seller_id, p.category, u.name AS seller_name
    FROM orders o JOIN products p ON o.product_id=p.product_id
                  JOIN users u ON p.seller_id=u.user_id
    WHERE {WHERE}
""")
orders["order_date"] = pd.to_datetime(orders["order_date"])
orders["month"] = orders["order_date"].dt.strftime("%Y-%m")
orders["cat_kr"] = orders["category"].map(CAT_KR).fillna(orders["category"])
orders["saved"] = (orders["original_unit_price"].fillna(0) * orders["quantity"] - orders["total_price"]).clip(lower=0)

tab_c, tab_s, tab_sql = st.tabs(["🛒 소비자", "🏡 판매자", "🧪 커스텀 SQL"])

# ══════════ 소비자 ══════════
with tab_c:
    per_buyer = orders.groupby("buyer_id").size()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("구매자", f"{per_buyer.size:,}")
    c2.metric("주문", f"{len(orders):,}")
    c3.metric("객단가(AOV)", f"{orders['total_price'].mean():,.0f}원")
    c4.metric("재구매율", f"{(per_buyer>=2).mean()*100:.1f}%")

    col1, col2 = st.columns(2)
    # [✏️ EDIT] 차트 종류·컬럼 자유롭게 변경 (px.bar / px.line / px.histogram …)
    col1.plotly_chart(px.histogram(per_buyer, nbins=int(per_buyer.max()),
                      title="구매자별 주문 수 분포", labels={"value": "주문 수"}), use_container_width=True)
    col2.plotly_chart(px.bar(orders["cat_kr"].value_counts(),
                      title="카테고리별 주문 건수"), use_container_width=True)
    mon = orders.groupby("month").size().reset_index(name="주문")
    st.plotly_chart(px.line(mon, x="month", y="주문", markers=True, title="월별 주문 추이"),
                    use_container_width=True)

    # 후기 별점 — [✏️ EDIT] 다른 집계 쿼리로 교체 가능
    rev = q("SELECT rating FROM reviews")
    st.plotly_chart(px.histogram(rev, x="rating", title=f"후기 별점 분포 (평균 {rev['rating'].mean():.2f}★)"),
                    use_container_width=True)

# ══════════ 판매자 ══════════
with tab_s:
    bs = orders.groupby("seller_name").agg(매출=("total_price", "sum"),
            받은주문=("order_id", "size"), 절약=("saved", "sum")).reset_index()
    s1, s2, s3 = st.columns(3)
    s1.metric("판매자", f"{bs.shape[0]:,}")
    s2.metric("총 매출(GMV)", f"{bs['매출'].sum():,.0f}원")
    s3.metric("폐기회수 절약", f"{bs['절약'].sum():,.0f}원")

    topn = st.slider("Top N", 5, 30, 10)   # [✏️ EDIT] 위젯 추가해 인터랙티브하게
    col1, col2 = st.columns(2)
    col1.plotly_chart(px.bar(bs.nlargest(topn, "매출").sort_values("매출"),
                      x="매출", y="seller_name", orientation="h", title=f"매출 Top{topn}"),
                      use_container_width=True)
    col2.plotly_chart(px.bar(bs.nlargest(topn, "받은주문").sort_values("받은주문"),
                      x="받은주문", y="seller_name", orientation="h", title=f"받은 주문 Top{topn}"),
                      use_container_width=True)

    avg = q("""SELECT u.name 판매자, ROUND(AVG(r.rating),2) 평균별점, COUNT(*) 후기수
               FROM reviews r JOIN orders o ON r.order_id=o.order_id
               JOIN products p ON o.product_id=p.product_id
               JOIN users u ON p.seller_id=u.user_id
               GROUP BY u.user_id ORDER BY 평균별점 DESC""")
    st.subheader("판매자 평균 별점")
    st.dataframe(avg, use_container_width=True, hide_index=True)

# ══════════ 커스텀 SQL ══════════
with tab_sql:
    st.caption("아무 SELECT 쿼리나 실행해 표·차트로 확인 (읽기 전용 권장).")
    default = "SELECT category, COUNT(*) 주문, SUM(total_price) 매출\nFROM orders o JOIN products p ON o.product_id=p.product_id\nGROUP BY category ORDER BY 매출 DESC"
    sql = st.text_area("SQL", value=default, height=140)   # [✏️ EDIT] 여기 직접 쿼리 작성
    if st.button("실행 ▶"):
        try:
            df = q(sql)
            st.dataframe(df, use_container_width=True, hide_index=True)
            num = df.select_dtypes("number").columns
            if len(df.columns) >= 2 and len(num):
                st.plotly_chart(px.bar(df, x=df.columns[0], y=num[0]), use_container_width=True)
        except Exception as e:
            st.error(f"쿼리 오류: {e}")
