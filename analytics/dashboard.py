"""
BaroFarm 대시보드 (DB 직결)
=============================================
두 개의 화면을 한 파일에서 제공한다(사이드바 버튼으로 전환):

  🏡 농장 대시보드  — 농장(판매자) '한 곳'만 깊게 보는 셀러 애널리틱스.
  🛠 관리자 페이지  — 플랫폼 '전체'를 보는 기존 통계.
"""
import os
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st
from sqlalchemy import create_engine, text

# ML 패키지 (scikit-learn · statsmodels)
from sklearn.linear_model import Ridge, LinearRegression
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.cluster import KMeans

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
    # URL 파라미터 ?seller_id=X 가 있으면 해당 농장에 고정 (셀러 전용 임베드용)
    locked_sid = None
    try:
        raw = st.query_params.get("seller_id")
        if raw:
            locked_sid = int(raw)
    except Exception:
        pass

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
        if locked_sid and locked_sid in labels:
            # seller_id 고정 — 셀러 전용 임베드 모드: selectbox 숨기고 고정
            sid = locked_sid
            sname = sellers.set_index("user_id").loc[sid, "name"]
            st.markdown(f"**🏡 {sname}**")
            st.caption("내 농장 전용 대시보드")
        else:
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

    # ── AI 예측 섹션 ─────────────────────────────────────────────
    render_ai_section(sid, o, d0, d1, sname)


# ════════════════════════════════════════════════════════════════
#  🤖 AI 예측 & 매입 추천  (scikit-learn · statsmodels 기반)
# ════════════════════════════════════════════════════════════════

@st.cache_data(ttl=300, show_spinner=False)
def _ai_revenue_forecast(sid: int, d0: str, d1: str):
    """Ridge Regression + 주간·월간 계절성 피처 → 30일 매출 예측."""
    df = q(f"""
        SELECT o.order_date, o.total_price
        FROM orders o JOIN products p ON o.product_id=p.product_id
        WHERE p.seller_id={sid} AND o.order_date BETWEEN '{d0} 00:00:00' AND '{d1} 23:59:59'
    """)
    if df.empty:
        return None
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["date"] = df["order_date"].dt.normalize()
    daily = df.groupby("date")["total_price"].sum().reset_index(name="revenue")
    daily = daily.set_index("date").asfreq("D", fill_value=0).reset_index()

    n = len(daily)
    if n < 14:
        return None

    idx = np.arange(n, dtype=float)
    X = np.column_stack([
        idx, idx**2,
        np.sin(2*np.pi*idx/7),  np.cos(2*np.pi*idx/7),   # 주간
        np.sin(2*np.pi*idx/30), np.cos(2*np.pi*idx/30),   # 월간
    ])
    y = daily["revenue"].values.astype(float)

    model = Ridge(alpha=100.0).fit(X, y)
    residual_std = float(np.std(y - model.predict(X)))

    fi = np.arange(n, n + 30, dtype=float)
    Xf = np.column_stack([
        fi, fi**2,
        np.sin(2*np.pi*fi/7),  np.cos(2*np.pi*fi/7),
        np.sin(2*np.pi*fi/30), np.cos(2*np.pi*fi/30),
    ])
    preds = model.predict(Xf).clip(0)
    future_dates = pd.date_range(daily["date"].max() + pd.Timedelta(days=1), periods=30)

    return {
        "daily": daily,
        "future_dates": future_dates.tolist(),
        "preds": preds.tolist(),
        "std": residual_std,
        "score": float(model.score(X, y)),
    }


@st.cache_data(ttl=300, show_spinner=False)
def _ai_purchase_reco(sid: int, d0: str, d1: str):
    """MinMaxScaler 멀티팩터 스코어링 → 매입 추천 Top-10."""
    df = q(f"""
        SELECT o.order_id, o.buyer_id, o.order_date, o.quantity, o.total_price,
               p.product_id, p.name AS product_name, p.category
        FROM orders o JOIN products p ON o.product_id=p.product_id
        WHERE p.seller_id={sid} AND o.order_date BETWEEN '{d0} 00:00:00' AND '{d1} 23:59:59'
    """)
    if df.empty or len(df) < 5:
        return None
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["date"]       = df["order_date"].dt.normalize()

    last = df["date"].max()
    df30  = df[df["date"] > last - pd.Timedelta(days=30)]
    df_30_60 = df[(df["date"] <= last - pd.Timedelta(days=30)) &
                  (df["date"] >  last - pd.Timedelta(days=60))]

    agg = df.groupby(["product_id","product_name","category"]).agg(
        total_qty = ("quantity",    "sum"),
        total_rev = ("total_price", "sum"),
        orders    = ("order_id",    "nunique"),
        buyers    = ("buyer_id",    "nunique"),
        active_days = ("date", lambda x: max((x.max()-x.min()).days+1, 1)),
    ).reset_index()

    recent  = df30.groupby("product_id")["total_price"].sum().rename("recent_rev")
    prev    = df_30_60.groupby("product_id")["total_price"].sum().rename("prev_rev")

    agg = agg.join(recent, on="product_id").join(prev, on="product_id").fillna(0)
    agg["velocity"]   = agg["total_qty"] / agg["active_days"]
    agg["trend"]      = (agg["recent_rev"]+1) / (agg["prev_rev"]+1)
    agg["rev_share"]  = agg["total_rev"] / agg["total_rev"].sum()
    agg["repurchase"] = (agg["orders"] / agg["buyers"].clip(lower=1)).clip(upper=5) / 5

    feats   = ["velocity","trend","rev_share","repurchase"]
    weights = np.array([0.30, 0.35, 0.20, 0.15])
    scaled  = MinMaxScaler().fit_transform(agg[feats])
    agg["score"] = (scaled * weights).sum(axis=1) * 100

    cat_kr = {"vegetable":"채소","fruit":"과일","seafood":"해산물","meat":"육류","grain":"곡물","etc":"기타"}
    agg["카테고리"] = agg["category"].map(cat_kr).fillna(agg["category"])
    agg["추천점수"] = agg["score"].round(1)
    agg["트렌드"]   = agg["trend"].apply(lambda t: "📈 상승" if t>1.1 else ("📉 하락" if t<0.9 else "➡️ 유지"))
    agg["이유"] = agg.apply(lambda r:
        "🔥 최근 급상승+고속도" if r.trend>1.2 and r.velocity>2 else
        "⭐ 안정적 재구매"      if r.repurchase>0.4 else
        "📦 매출 핵심 상품"     if r.rev_share>0.05 else
        "🌱 성장 잠재력", axis=1)

    return agg.sort_values("score", ascending=False).head(10)


@st.cache_data(ttl=300, show_spinner=False)
def _ai_demand_forecast(sid: int, d0: str, d1: str):
    """상위 8개 상품의 주간 수요 → LinearRegression → 4주 예측."""
    df = q(f"""
        SELECT o.order_date, o.quantity, p.product_id, p.name AS product_name, p.category
        FROM orders o JOIN products p ON o.product_id=p.product_id
        WHERE p.seller_id={sid} AND o.order_date BETWEEN '{d0} 00:00:00' AND '{d1} 23:59:59'
    """)
    if df.empty:
        return None
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["week"]       = df["order_date"].dt.to_period("W").astype(str)

    top_pids = df.groupby("product_id")["quantity"].sum().nlargest(8).index
    results  = []
    for pid in top_pids:
        sub = df[df["product_id"]==pid]
        weekly = sub.groupby("week")["quantity"].sum().reset_index(name="qty")
        if len(weekly) < 4:
            continue
        X = np.arange(len(weekly), dtype=float).reshape(-1, 1)
        y = weekly["qty"].values.astype(float)
        m = LinearRegression().fit(X, y)
        f4 = m.predict(np.arange(len(weekly), len(weekly)+4, dtype=float).reshape(-1,1)).clip(0)
        results.append({
            "product_id":   pid,
            "product_name": sub["product_name"].iloc[0],
            "category":     sub["category"].iloc[0],
            "avg_qty":      float(y.mean()),
            "forecast_avg": float(f4.mean()),
            "trend_pct":    float((f4[-1]-y[-1])/(y[-1]+1)*100),
            "history":      y[-8:].tolist(),
            "forecast":     f4.tolist(),
        })
    return pd.DataFrame(results) if results else None


@st.cache_data(ttl=300, show_spinner=False)
def _ai_customer_segments(sid: int, d0: str, d1: str):
    """RFM + KMeans(4) → 고객 세그멘테이션."""
    df = q(f"""
        SELECT o.buyer_id, o.order_date, o.total_price, o.order_id
        FROM orders o JOIN products p ON o.product_id=p.product_id
        WHERE p.seller_id={sid} AND o.order_date BETWEEN '{d0} 00:00:00' AND '{d1} 23:59:59'
    """)
    if df.empty:
        return None
    df["order_date"] = pd.to_datetime(df["order_date"])
    last = df["order_date"].max()

    rfm = df.groupby("buyer_id").agg(
        recency   = ("order_date",  lambda x: (last-x.max()).days),
        frequency = ("order_id",    "nunique"),
        monetary  = ("total_price", "sum"),
    ).reset_index()

    n_clusters = min(4, len(rfm))
    if n_clusters < 2:
        return None

    scaled = StandardScaler().fit_transform(rfm[["recency","frequency","monetary"]])
    km     = KMeans(n_clusters=n_clusters, random_state=42, n_init=10).fit(scaled)
    rfm["cluster"] = km.labels_

    order = rfm.groupby("cluster")["monetary"].median().sort_values().index
    names = ["이탈위험 ⚠️","잠재고객 🌱","충성고객 ⭐","VIP 👑"][:n_clusters]
    label_map = {c: names[i] for i, c in enumerate(order)}
    rfm["segment"] = rfm["cluster"].map(label_map)
    return rfm


@st.cache_data(ttl=300, show_spinner=False)
def _ai_seasonality(sid: int, d0: str, d1: str):
    """카테고리×월별 매출 히트맵 + 성장률 분석."""
    df = q(f"""
        SELECT o.order_date, o.total_price, p.category
        FROM orders o JOIN products p ON o.product_id=p.product_id
        WHERE p.seller_id={sid} AND o.order_date BETWEEN '{d0} 00:00:00' AND '{d1} 23:59:59'
    """)
    if df.empty:
        return None, None
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["month"]      = df["order_date"].dt.strftime("%Y-%m")

    cat_kr = {"vegetable":"채소","fruit":"과일","seafood":"해산물","meat":"육류","grain":"곡물","etc":"기타"}
    df["cat_kr"] = df["category"].map(cat_kr).fillna(df["category"])

    pivot = df.groupby(["month","cat_kr"])["total_price"].sum().unstack(fill_value=0)

    # 월별 전체 추이 (statsmodels HP filter 대신 간단한 rolling)
    monthly_total = df.groupby("month")["total_price"].sum().reset_index(name="revenue")

    # 최근 달 vs 이전 달 카테고리별 성장률
    if len(monthly_total) >= 2:
        last_m  = monthly_total["month"].max()
        prev_m  = monthly_total.iloc[-2]["month"]
        last_df = df[df["month"]==last_m].groupby("cat_kr")["total_price"].sum()
        prev_df = df[df["month"]==prev_m].groupby("cat_kr")["total_price"].sum()
        growth  = ((last_df - prev_df) / (prev_df + 1) * 100).sort_values(ascending=False)
    else:
        growth = pd.Series(dtype=float)

    return pivot, growth


def render_ai_section(sid: int, o: pd.DataFrame, d0: str, d1: str, sname: str):
    """5개 ML/AI 예측 모듈을 탭으로 구성해 농장 대시보드 하단에 표시."""
    st.markdown("<hr/>", unsafe_allow_html=True)
    st.markdown("## 🤖 AI 예측 & 매입 추천")
    st.caption(
        f"**{sname}** 농장의 실제 주문 데이터로 학습한 머신러닝 모델 · "
        "scikit-learn Ridge/LinearRegression/KMeans · 5분 캐시"
    )
    st.write("")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 매출 예측",
        "🛒 매입 추천 AI",
        "🔮 상품별 수요 예측",
        "👥 고객 세그먼트",
        "📅 계절성 분석",
    ])

    # ── Tab 1 : 매출 예측 ──────────────────────────────────────────
    with tab1:
        with st.spinner("Ridge Regression 모델 학습 중…"):
            res = _ai_revenue_forecast(sid, d0, d1)
        if res is None:
            st.info("예측에 필요한 데이터가 부족합니다. (최소 2주 이상의 주문 이력 필요)")
        else:
            daily = res["daily"]
            fdates = pd.DatetimeIndex(res["future_dates"])
            preds  = np.array(res["preds"])
            std    = res["std"]
            r2     = res["score"]

            c1, c2, c3 = st.columns(3)
            c1.metric("예측 30일 총 매출", f"{preds.sum():,.0f}원")
            c2.metric("예측 일평균 매출",  f"{preds.mean():,.0f}원")
            c3.metric("모델 설명력 (R²)",  f"{r2:.3f}")
            st.write("")

            fig = go.Figure()
            # 실제 매출
            fig.add_trace(go.Bar(
                x=daily["date"], y=daily["revenue"],
                name="실제 매출", marker_color="#74C69D", opacity=0.7,
            ))
            # 예측 라인
            fig.add_trace(go.Scatter(
                x=fdates, y=preds, mode="lines+markers",
                name="30일 예측", line=dict(color="#F4845F", width=2.5, dash="dot"),
            ))
            # 신뢰 구간 (±1σ)
            fig.add_trace(go.Scatter(
                x=list(fdates) + list(fdates[::-1]),
                y=list((preds+std).clip(0)) + list((preds-std).clip(0)[::-1]),
                fill="toself", fillcolor="rgba(244,132,95,0.15)",
                line=dict(color="rgba(255,255,255,0)"),
                name="±1σ 신뢰구간",
            ))
            fig.update_layout(
                title=f"{sname} — 일별 매출 및 30일 예측 (Ridge Regression)",
                xaxis_title="날짜", yaxis_title="매출(원)",
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                legend=dict(orientation="h", y=-0.2),
            )
            st.plotly_chart(fig, use_container_width=True)
            st.caption("주간(sin/cos 주기 7일)·월간(주기 30일) 계절성 피처를 사용한 Ridge Regression 모델. "
                       "주황 점선이 향후 30일 예측, 음영이 ±1σ 불확실성 구간입니다.")

    # ── Tab 2 : 매입 추천 AI ───────────────────────────────────────
    with tab2:
        with st.spinner("매입 추천 스코어 계산 중…"):
            reco = _ai_purchase_reco(sid, d0, d1)
        if reco is None:
            st.info("스코어 계산에 필요한 주문 데이터가 부족합니다.")
        else:
            st.markdown("### 🛒 AI 매입 추천 — Top 10 상품")
            st.caption(
                "판매 속도(velocity 30%) · 최근 트렌드(35%) · 매출 비중(20%) · 재구매율(15%)을 "
                "MinMaxScaler로 정규화 후 가중합한 **종합 추천 점수**입니다."
            )

            fig_reco = px.bar(
                reco.sort_values("score"),
                x="score", y="product_name", orientation="h",
                color="score", color_continuous_scale="YlGn",
                text="추천점수",
                title="매입 추천 점수 (100점 만점)",
            )
            fig_reco.update_traces(texttemplate="%{text}점", textposition="outside")
            fig_reco.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                yaxis_title="", xaxis_title="추천 점수",
                coloraxis_showscale=False,
            )
            st.plotly_chart(fig_reco, use_container_width=True)

            st.dataframe(
                reco[["product_name","카테고리","추천점수","트렌드","이유",
                      "velocity","repurchase"]].rename(columns={
                    "product_name":"상품명", "velocity":"일평균판매량",
                    "repurchase":"재구매지수",
                }).round({"일평균판매량":2, "재구매지수":2}),
                use_container_width=True, hide_index=True,
            )

    # ── Tab 3 : 상품별 수요 예측 ──────────────────────────────────
    with tab3:
        with st.spinner("주간 수요 예측 모델 학습 중…"):
            dem = _ai_demand_forecast(sid, d0, d1)
        if dem is None or dem.empty:
            st.info("수요 예측에 필요한 데이터가 부족합니다. (상품당 최소 4주 이상)")
        else:
            cat_kr = {"vegetable":"채소","fruit":"과일","seafood":"해산물",
                      "meat":"육류","grain":"곡물","etc":"기타"}
            dem["카테고리"] = dem["category"].map(cat_kr).fillna(dem["category"])
            dem["현재 주간 수요"] = dem["avg_qty"].round(1)
            dem["예측 주간 수요"] = dem["forecast_avg"].round(1)
            dem["트렌드"] = dem["trend_pct"].apply(
                lambda t: f"📈 +{t:.1f}%" if t>3 else (f"📉 {t:.1f}%" if t<-3 else f"➡️ {t:.1f}%")
            )

            st.markdown("### 🔮 상위 8개 상품 — 향후 4주 수요 예측")
            st.caption("주간 판매량의 선형 회귀(LinearRegression)로 다음 4주 평균 수요를 예측합니다.")

            # Bullet chart: 현재 vs 예측
            fig_dem = go.Figure()
            colors = px.colors.qualitative.Pastel
            for i, row in dem.iterrows():
                fig_dem.add_trace(go.Bar(
                    name=row["product_name"][:12],
                    x=[row["product_name"][:14]],
                    y=[row["avg_qty"]],
                    marker_color="#74C69D",
                    showlegend=i==0,
                    legendgroup="현재",
                ))
                fig_dem.add_trace(go.Bar(
                    name="예측",
                    x=[row["product_name"][:14]],
                    y=[row["forecast_avg"]],
                    marker_color="#F4845F",
                    marker_pattern_shape="/",
                    showlegend=i==0,
                    legendgroup="예측",
                ))
            fig_dem.update_layout(
                barmode="group",
                title="현재 주간 평균 수요 vs 4주 후 예측",
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                xaxis_tickangle=-30, legend=dict(orientation="h", y=-0.3),
            )
            st.plotly_chart(fig_dem, use_container_width=True)

            st.dataframe(
                dem[["product_name","카테고리","현재 주간 수요","예측 주간 수요","트렌드"]].rename(
                    columns={"product_name":"상품명"}),
                use_container_width=True, hide_index=True,
            )

    # ── Tab 4 : 고객 세그멘테이션 ─────────────────────────────────
    with tab4:
        with st.spinner("RFM KMeans 클러스터링 학습 중…"):
            rfm = _ai_customer_segments(sid, d0, d1)
        if rfm is None:
            st.info("세그멘테이션에 필요한 고객 수가 부족합니다. (최소 8명 이상)")
        else:
            st.markdown("### 👥 RFM 기반 고객 세그멘테이션 (KMeans 4-Cluster)")
            st.caption(
                "**R**ecency(최근 구매일) · **F**requency(구매 횟수) · **M**onetary(총 구매액)을 "
                "StandardScaler로 정규화 후 KMeans(k=4)로 군집화합니다."
            )

            seg_colors = {
                "VIP 👑": "#2D6A4F", "충성고객 ⭐": "#52B788",
                "잠재고객 🌱": "#95D5B2", "이탈위험 ⚠️": "#F4845F",
            }

            # 세그먼트 요약 KPI
            summary = rfm.groupby("segment").agg(
                고객수=("buyer_id","count"),
                평균구매횟수=("frequency","mean"),
                평균매출=("monetary","mean"),
                평균최근성=("recency","mean"),
            ).reset_index().sort_values("평균매출", ascending=False)

            cols = st.columns(len(summary))
            for col, (_, row) in zip(cols, summary.iterrows()):
                col.metric(
                    row["segment"],
                    f"{int(row['고객수'])}명",
                    f"평균 {row['평균매출']:,.0f}원",
                )

            st.write("")

            # Scatter: Frequency vs Monetary (size=recency_inv)
            rfm["recency_inv"] = 1 / (rfm["recency"] + 1)
            fig_rfm = px.scatter(
                rfm, x="frequency", y="monetary",
                color="segment", size="recency_inv",
                color_discrete_map=seg_colors,
                hover_data={"buyer_id": True, "recency": True},
                title="고객 분포 (x=구매횟수, y=총매출, 점크기=최근성)",
                labels={"frequency":"구매 횟수","monetary":"총 구매액(원)","segment":"세그먼트"},
            )
            fig_rfm.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig_rfm, use_container_width=True)

            # 세그먼트별 파이
            seg_count = rfm["segment"].value_counts().reset_index()
            seg_count.columns = ["segment","count"]
            fig_pie = px.pie(
                seg_count, names="segment", values="count",
                color="segment", color_discrete_map=seg_colors,
                title="세그먼트 구성 비율", hole=0.45,
            )
            fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)")
            c1, c2 = st.columns([1.6, 1])
            c1.dataframe(
                summary.round({"평균구매횟수":1,"평균매출":0,"평균최근성":0}).rename(
                    columns={"평균최근성":"최근구매(일전)"}),
                use_container_width=True, hide_index=True,
            )
            c2.plotly_chart(fig_pie, use_container_width=True)

    # ── Tab 5 : 계절성 분석 ───────────────────────────────────────
    with tab5:
        with st.spinner("계절성 패턴 분석 중…"):
            pivot, growth = _ai_seasonality(sid, d0, d1)
        if pivot is None or pivot.empty:
            st.info("계절성 분석에 필요한 데이터가 부족합니다.")
        else:
            st.markdown("### 📅 카테고리 × 월별 매출 히트맵")
            st.caption("어떤 달에 어떤 카테고리가 잘 팔렸는지 확인하고, 다음 달 매입 계획을 세우세요.")

            fig_heat = px.imshow(
                pivot.T, text_auto=".0f", aspect="auto",
                color_continuous_scale="Greens",
                title="카테고리 × 월별 매출 (원)",
                labels=dict(x="월", y="카테고리", color="매출"),
            )
            fig_heat.update_layout(paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_heat, use_container_width=True)

            if growth is not None and not growth.empty:
                st.markdown("### 이번 달 카테고리별 성장률 (전월 대비)")
                fig_growth = px.bar(
                    growth.reset_index(),
                    x="cat_kr", y=growth.name or 0,
                    color=growth.values,
                    color_continuous_scale=["#F4845F","#FFFFFF","#52B788"],
                    color_continuous_midpoint=0,
                    text_auto=".1f",
                    title="전월 대비 카테고리 매출 성장률 (%)",
                    labels={"cat_kr":"카테고리", growth.name or 0:"성장률(%)"},
                )
                fig_growth.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    coloraxis_showscale=False,
                )
                fig_growth.update_traces(texttemplate="%{text}%")
                st.plotly_chart(fig_growth, use_container_width=True)

                # 추천 멘트
                top_cats = growth[growth > 5].index.tolist()
                down_cats = growth[growth < -5].index.tolist()
                if top_cats:
                    st.success(f"📈 **매입 확대 추천**: {', '.join(top_cats)} — 전월 대비 성장 중")
                if down_cats:
                    st.warning(f"📉 **매입 축소 검토**: {', '.join(down_cats)} — 전월 대비 하락 중")


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