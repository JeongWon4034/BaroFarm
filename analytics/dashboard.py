"""
BaroFarm 대시보드 (DB 직결)
=============================================
두 개의 화면을 한 파일에서 제공한다(사이드바 버튼으로 전환):

  🏡 농장 대시보드  — 농장(판매자) '한 곳'만 깊게 보는 셀러 애널리틱스.
  🛠 관리자 페이지  — 플랫폼 '전체'를 보는 기존 통계.
"""
import os
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.io as pio
import streamlit as st
from sqlalchemy import create_engine, text

# ── 차트 기본 테마 설정 (여백 최소화, 깔끔한 배경) ────────────────────────
pio.templates.default = "plotly_white"
PX = dict(color_discrete_sequence=px.colors.qualitative.Pastel) # 더 부드러운 색상 팔레트

st.set_page_config(page_title="BaroFarm 대시보드", page_icon="🌱", layout="wide")

# ── 디자인: 커스텀 CSS 주입 (폰트 및 Metric 카드 스타일링) ─────────────────
st.markdown("""
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
* {
    font-family: 'Pretendard', sans-serif;
}
div[data-testid="metric-container"] {
    background-color: #ffffff;
    border: 1px solid #e0e0e0;
    padding: 15px 20px;
    border-radius: 12px;
    box-shadow: 2px 2px 10px rgba(0,0,0,0.03);
}
hr {
    margin: 2em 0;
    border-color: #f0f0f0;
}
</style>
""", unsafe_allow_html=True)


# ── DB 연결 (도커 MySQL) ───────────────────────────────────────────
DB_URL = os.getenv("DB_URL", "mysql+pymysql://root:1234@127.0.0.1:3306/freshgrowth?charset=utf8mb4")

@st.cache_resource
def get_engine():
    return create_engine(DB_URL)

@st.cache_data(ttl=60)
def q(sql: str) -> pd.DataFrame:
    return pd.read_sql(text(sql), get_engine())

CAT_KR = {"vegetable": "채소", "fruit": "과일", "seafood": "해산물",
          "meat": "육류", "grain": "곡물", "processed": "가공"}

# ── 화면 전환 상태 ────────────────────────────────────────────────
if "view" not in st.session_state:
    st.session_state.view = "farm"

def won(x) -> str:
    return f"{x:,.0f}원"

# ════════════════════════════════════════════════════════════════
#  🏡 농장(단일 판매자) 대시보드
# ════════════════════════════════════════════════════════════════
def render_farm():
    sellers = q("""
        SELECT u.user_id, u.name,
               COUNT(o.order_id) AS orders,
               COALESCE(SUM(o.total_price),0) AS gmv
        FROM users u
        LEFT JOIN products p ON p.seller_id = u.user_id
        LEFT JOIN orders   o ON o.product_id = p.product_id
        WHERE u.role = 'SELLER'
        GROUP BY u.user_id, u.name
        HAVING orders > 0
        ORDER BY gmv DESC
    """)
    if sellers.empty:
        st.warning("주문 데이터가 있는 판매자가 없습니다. 시드 스크립트를 먼저 실행하세요.")
        return

    with st.sidebar:
        st.header("🏡 농장 선택")
        labels = {int(r.user_id): f"{r.name}  ·  GMV {r.gmv/1e4:,.0f}만 · {int(r.orders)}건"
                  for r in sellers.itertuples()}
        sid = st.selectbox("농장", list(labels), format_func=lambda i: labels[i])
        sname = sellers.set_index("user_id").loc[sid, "name"]

        dmm = q(f"SELECT MIN(o.order_date) a, MAX(o.order_date) b FROM orders o "
                f"JOIN products p ON o.product_id=p.product_id WHERE p.seller_id={sid}")
        dmin, dmax = dmm.iloc[0]
        date_range = st.date_input("조회 기간", value=(pd.to_datetime(dmin), pd.to_datetime(dmax)))

    d0, d1 = (str(date_range[0]), str(date_range[1])) if len(date_range) == 2 else (str(dmin), str(dmax))

    o = q(f"""
        SELECT o.order_id, o.buyer_id, o.order_date, o.quantity, o.total_price,
               o.original_unit_price, o.status, o.lot_id,
               p.product_id, p.name AS product_name, p.category
        FROM orders o JOIN products p ON o.product_id = p.product_id
        WHERE p.seller_id = {sid}
          AND o.order_date BETWEEN '{d0} 00:00:00' AND '{d1} 23:59:59'
    """)
    if o.empty:
        st.info("선택한 기간에 주문이 없습니다. 기간을 넓혀보세요.")
        return
        
    o["order_date"] = pd.to_datetime(o["order_date"])
    o["date"] = o["order_date"].dt.normalize()
    o["month"] = o["order_date"].dt.to_period("M").astype(str)
    o["cat_kr"] = o["category"].map(CAT_KR).fillna(o["category"])
    o["saved"] = (o["original_unit_price"].fillna(0) * o["quantity"] - o["total_price"]).clip(lower=0)
    o["is_deal"] = o["saved"] > 0

    # ── 헤더 ──────────────────────────────────────────────────────
    st.markdown(f"## 🏡 {sname} 애널리틱스")
    st.markdown(f"<span style='color:gray; font-size:0.9em;'>기간: {d0} ~ {d1} &nbsp;|&nbsp; 단일 판매자 셀러 대시보드</span>", unsafe_allow_html=True)
    st.write("") # 여백 추가

    # ── KPI ───────────────────────────────────────────────────────
    maxd = o["order_date"].max()
    last = o[o["order_date"] > maxd - pd.Timedelta(days=30)]
    prev = o[(o["order_date"] <= maxd - pd.Timedelta(days=30)) & (o["order_date"] > maxd - pd.Timedelta(days=60))]

    def delta(cur, pre):
        if pre == 0: return None
        return f"{(cur - pre) / pre * 100:+.0f}% vs 이전 30일"

    n_buyers = o["buyer_id"].nunique()
    per_buyer = o.groupby("buyer_id").size()
    gmv = o["total_price"].sum()
    followers = int(q(f"SELECT COUNT(*) c FROM follows WHERE following_id={sid}").iloc[0, 0])
    avg_rating = q(f"""SELECT AVG(r.rating) v FROM reviews r JOIN orders o ON r.order_id=o.order_id
                       JOIN products p ON o.product_id=p.product_id WHERE p.seller_id={sid}""").iloc[0, 0]

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("총 매출 (GMV)", won(gmv), delta(last["total_price"].sum(), prev["total_price"].sum()))
    k2.metric("주문 수", f"{len(o):,}건", delta(len(last), len(prev)))
    k3.metric("객단가 (AOV)", won(o["total_price"].mean()), 
              delta(last["total_price"].mean() if len(last) else 0, prev["total_price"].mean() if len(prev) else 0))
    k4.metric("구매 고객", f"{n_buyers:,}명")

    st.write("")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("재구매율", f"{(per_buyer >= 2).mean() * 100:.1f}%")
    k2.metric("할인 회수 매출", won(o.loc[o["is_deal"], "total_price"].sum()), 
              f"전체 매출의 {o.loc[o['is_deal'],'total_price'].sum()/gmv*100:.0f}% 비중")
    k3.metric("고객 절약액", won(o["saved"].sum()), "정가 대비 할인분")
    k4.metric("평균 별점", f"{avg_rating:.2f} ★" if pd.notnull(avg_rating) else "—", f"팔로워 {followers:,}명")

    st.markdown("<hr/>", unsafe_allow_html=True)

    # ── 1. 매출 추이 ──────────────────────────────────────────────
    st.markdown("### 📈 매출 추이")
    c1, c2 = st.columns([2, 1])
    
    daily = o.groupby("date")["total_price"].sum().reset_index(name="매출")
    full_idx = pd.date_range(daily["date"].min(), daily["date"].max(), freq="D")
    daily = daily.set_index("date").reindex(full_idx, fill_value=0).rename_axis("date").reset_index()
    daily["7일 이동평균"] = daily["매출"].rolling(7, min_periods=1).mean()
    
    fig1 = px.bar(daily, x="date", y="매출", title="일별 매출 및 추세", **PX)
    fig1.add_scatter(x=daily["date"], y=daily["7일 이동평균"], mode="lines", name="7일 이동평균", line=dict(color="#FF7F50", width=3))
    fig1.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    c1.plotly_chart(fig1, use_container_width=True)

    mon = o.groupby("month").agg(매출=("total_price", "sum"), 주문=("order_id", "size")).reset_index()
    fig2 = px.bar(mon, x="month", y="매출", title="월별 누적 매출", text_auto=".2s", **PX)
    fig2.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
    c2.plotly_chart(fig2, use_container_width=True)

    st.markdown("<hr/>", unsafe_allow_html=True)

    # ── 2. 마감임박 할인 효과 ────────────────────────────────────────
    st.markdown("### ⏰ 마감임박 할인 세일 효과")
    st.caption("폐기 직전 재고를 할인 판매해 '버릴 매출'을 회수한 규모입니다.")
    c1, c2, c3 = st.columns(3)
    
    deal_mix = pd.DataFrame({"구분": ["할인 주문", "정가 주문"], "주문": [int(o["is_deal"].sum()), int((~o["is_deal"]).sum())]})
    fig_pie = px.pie(deal_mix, names="구분", values="주문", hole=.5, title="할인 vs 정가 주문 비중", color="구분", 
                     color_discrete_map={"할인 주문":"#FF9F43", "정가 주문":"#1DD1A1"})
    c1.plotly_chart(fig_pie, use_container_width=True)

    by_cat = o.groupby("cat_kr").agg(매출=("total_price", "sum"),
                                     할인매출=("total_price", lambda s: o.loc[s.index].query("is_deal")["total_price"].sum())).reset_index()
    by_cat["할인비중%"] = (by_cat["할인매출"] / by_cat["매출"] * 100).round(1)
    fig_cat = px.bar(by_cat.sort_values("매출"), x="매출", y="cat_kr", orientation="h", color="할인비중%", 
                     title="카테고리별 매출 및 할인 의존도", color_continuous_scale="Oranges")
    c2.plotly_chart(fig_cat, use_container_width=True)

    monthly_saved = o.groupby("month").agg(회수매출=("total_price", lambda s: o.loc[s.index].query("is_deal")["total_price"].sum()),
                                           고객절약=("saved", "sum")).reset_index()
    fig_saved = px.bar(monthly_saved, x="month", y=["회수매출", "고객절약"], barmode="group", title="월별 회수 매출 및 절약액", **PX)
    fig_saved.update_layout(legend_title_text='')
    c3.plotly_chart(fig_saved, use_container_width=True)

    st.markdown("<hr/>", unsafe_allow_html=True)

    # ── 나머지 섹션들 (상품, 고객, 운영, 리뷰) ─────────────────────────
    # 기존과 로직은 동일하나 레이아웃만 다듬음
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("### 👥 고객 리텐션 분석")
        cohort = o.copy()
        first_m = cohort.groupby("buyer_id")["order_date"].transform("min").dt.to_period("M")
        order_m = cohort["order_date"].dt.to_period("M")
        cohort["코호트"] = first_m.astype(str)
        cohort["차수"] = (order_m - first_m).apply(lambda x: x.n)
        size = cohort.groupby("코호트")["buyer_id"].nunique()
        ret = (cohort.groupby(["코호트", "차수"])["buyer_id"].nunique().unstack().divide(size, axis=0) * 100).round(0)
        
        if ret.shape[1] > 1:
            ret.columns = [f"+{c}M" for c in ret.columns]
            fig_cohort = px.imshow(ret, text_auto=".0f", aspect="auto", color_continuous_scale="Blues", title="코호트 리텐션 (%)")
            st.plotly_chart(fig_cohort, use_container_width=True)
            
    with c2:
        st.markdown("### ⚙️ 요일/시간대별 주문 피크")
        hm = o.copy()
        hm["요일"] = hm["order_date"].dt.dayofweek.map(dict(enumerate(["월", "화", "수", "목", "금", "토", "일"])))
        hm["시간대"] = hm["order_date"].dt.hour
        pivot = hm.pivot_table(index="요일", columns="시간대", values="order_id", aggfunc="count", fill_value=0)
        pivot = pivot.reindex(["월", "화", "수", "목", "금", "토", "일"])
        fig_hm = px.imshow(pivot, aspect="auto", color_continuous_scale="Purples", title="주문 발생 히트맵")
        st.plotly_chart(fig_hm, use_container_width=True)

    # 표 데이터는 디자인을 깔끔하게 유지하기 위해 Expander로 감춤
    st.markdown("### 📦 재고 현황 (마감 임박순)")
    lots = q(f"""
        SELECT p.name, p.category, l.stock_qty, l.price, DATEDIFF(l.expiration_date, CURDATE()) AS dday
        FROM product_lots l JOIN products p ON l.product_id=p.product_id
        WHERE p.seller_id={sid} AND l.stock_qty > 0
    """)
    if not lots.empty:
        lots["긴급도"] = lots["dday"].apply(lambda d: "🔴 임박" if d <= 3 else "🟡 주의" if d <= 7 else "🟢 여유")
        with st.expander("현재 판매 가능한 재고 목록 자세히 보기", expanded=True):
            st.dataframe(lots.sort_values("dday")[["name", "긴급도", "dday", "stock_qty", "price"]], use_container_width=True, hide_index=True)


# ════════════════════════════════════════════════════════════════
#  🛠 관리자 페이지
# ════════════════════════════════════════════════════════════════
def render_admin():
    st.markdown("## 🛠 관리자 대시보드")
    st.caption("플랫폼 전체 주문 데이터를 기반으로 통합된 통계를 제공합니다.")
    st.write("")

    with st.sidebar:
        st.header("⚙️ 필터 옵션")
        dmin, dmax = q("SELECT MIN(order_date) a, MAX(order_date) b FROM orders").iloc[0]
        date_range = st.date_input("주문 기간", value=(pd.to_datetime(dmin), pd.to_datetime(dmax)))
        cats = st.multiselect("카테고리 선택", list(CAT_KR), default=list(CAT_KR), format_func=lambda c: CAT_KR[c])

    d0, d1 = (str(date_range[0]), str(date_range[1])) if len(date_range) == 2 else (str(dmin), str(dmax))
    cat_in = "(" + ",".join(f"'{c}'" for c in cats) + ")" if cats else "('')"
    WHERE = f"o.order_date BETWEEN '{d0} 00:00:00' AND '{d1} 23:59:59' AND p.category IN {cat_in}"

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

    # 탭 디자인
    tab_c, tab_s, tab_sql = st.tabs(["🛒 소비자 분석", "🏡 판매자 분석", "🧪 커스텀 SQL 탐색기"])

    with tab_c:
        per_buyer = orders.groupby("buyer_id").size()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("총 구매자 수", f"{per_buyer.size:,}명")
        c2.metric("총 주문 건수", f"{len(orders):,}건")
        c3.metric("평균 객단가 (AOV)", f"{orders['total_price'].mean():,.0f}원")
        c4.metric("플랫폼 재구매율", f"{(per_buyer>=2).mean()*100:.1f}%")
        
        st.write("")
        col1, col2 = st.columns(2)
        fig_cat_admin = px.pie(orders["cat_kr"].value_counts().reset_index(), names='cat_kr', values='count', hole=0.4, title="카테고리별 주문 비중", **PX)
        col1.plotly_chart(fig_cat_admin, use_container_width=True)
        
        mon = orders.groupby("month").size().reset_index(name="주문")
        fig_mon_admin = px.area(mon, x="month", y="주문", markers=True, title="플랫폼 월별 주문 추이", color_discrete_sequence=["#1DD1A1"])
        col2.plotly_chart(fig_mon_admin, use_container_width=True)

    with tab_s:
        bs = orders.groupby("seller_name").agg(매출=("total_price", "sum"), 받은주문=("order_id", "size"), 절약=("saved", "sum")).reset_index()
        s1, s2, s3 = st.columns(3)
        s1.metric("입점 판매자 수", f"{bs.shape[0]:,}곳")
        s2.metric("플랫폼 총 매출 (GMV)", f"{bs['매출'].sum():,.0f}원")
        s3.metric("총 폐기회수 절약액", f"{bs['절약'].sum():,.0f}원")

        st.write("")
        topn = st.slider("상위 판매자 순위 표시(Top N)", 5, 30, 10)
        
        fig_seller = px.bar(bs.nlargest(topn, "매출").sort_values("매출"), x="매출", y="seller_name", orientation="h", title=f"매출 기준 Top {topn} 판매자", color="매출", color_continuous_scale="Teal")
        st.plotly_chart(fig_seller, use_container_width=True)

    with tab_sql:
        st.info("💡 자유롭게 SELECT 쿼리를 실행해 즉석에서 표와 차트를 렌더링하세요.")
        default = "SELECT category, COUNT(*) 주문, SUM(total_price) 매출\nFROM orders o JOIN products p ON o.product_id=p.product_id\nGROUP BY category ORDER BY 매출 DESC"
        sql = st.text_area("SQL 입력", value=default, height=140)
        
        if st.button("실행하기 ▶", type="primary"):
            try:
                df = q(sql)
                st.dataframe(df, use_container_width=True, hide_index=True)
                num = df.select_dtypes("number").columns
                if len(df.columns) >= 2 and len(num):
                    st.plotly_chart(px.bar(df, x=df.columns[0], y=num[0]), use_container_width=True)
            except Exception as e:
                st.error(f"쿼리 오류가 발생했습니다: {e}")

# ════════════════════════════════════════════════════════════════
#  사이드바 네비게이션
# ════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.session_state.view == "farm":
        if st.button("🛠 관리자 모드로 전환", use_container_width=True):
            st.session_state.view = "admin"
            st.rerun()
    else:
        if st.button("← 🏡 셀러 모드로 복귀", use_container_width=True, type="primary"):
            st.session_state.view = "farm"
            st.rerun()
            
    if st.button("🔄 최신 데이터 불러오기", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.markdown("<hr/>", unsafe_allow_html=True)

if st.session_state.view == "farm":
    render_farm()
else:
    render_admin()