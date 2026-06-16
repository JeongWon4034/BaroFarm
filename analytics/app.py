"""
FreshGrowth Growth 분석 대시보드 (Streamlit)
================================================
kpi.py(단일 분석 엔진)를 직접 import해 시각화만 담당한다. 계산 로직은 여기 없다.
Vue 판매자 대시보드는 api.py(FastAPI)로 같은 엔진을 호출 → 단일 소스.

실행:  streamlit run app.py
데이터: analytics/data/ (합성, seed=42). simulate.py로 재생성 가능.
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import kpi

st.set_page_config(page_title="FreshGrowth Growth 대시보드", layout="wide")


@st.cache_data(ttl=300)
def load():
    """data/ 로드(5분 캐시). 라이브 DB 전환 시 kpi.load_data 내부만 교체."""
    return kpi.load_data()


try:
    data = load()
except FileNotFoundError as e:
    st.error(str(e))
    st.stop()

events, orders = data["events"], data["orders"]

st.title("🥬 FreshGrowth — Growth 분석 대시보드")
st.caption("합성 데이터(seed=42) 위에서 계산한 **실측 지표**. 데이터만 합성, 수치는 실측.")

# ── KPI 카드 ───────────────────────────────────────────────────────
rv = kpi.revenue(orders)
rp = kpi.repurchase_rate(orders)
de = kpi.deal_effect(events)
c1, c2, c3, c4 = st.columns(4)
c1.metric("GMV", f"{rv['gmv']/1e6:.1f}M원")
c2.metric("객단가 AOV", f"{rv['aov']:,}원")
c3.metric("재구매율", f"{rp['rate']}%")
c4.metric("딜 효과 lift", f"×{de['lift']}",
          "유의 ✅" if de["test"]["significant"] else "유의하지 않음")

st.divider()
left, right = st.columns(2)

# ── 1. 퍼널 ────────────────────────────────────────────────────────
with left:
    st.subheader("① 퍼널 전환율 (세션 기준)")
    f = kpi.funnel(events)
    fig = go.Figure(go.Funnel(
        y=f["stage"], x=f["sessions"],
        textinfo="value+percent initial",
        marker={"color": ["#74c69d", "#52b788", "#2d6a4f"]},
    ))
    fig.update_layout(height=320, margin=dict(t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

# ── 2. 마감임박 딜 효과 (시그니처) ─────────────────────────────────
with right:
    st.subheader("② 마감임박 딜 효과 ⭐")
    cmp = pd.DataFrame({
        "그룹": ["딜(마감임박)", "정상가"],
        "상세→구매 전환율(%)": [de["deal"]["cvr"], de["normal"]["cvr"]],
    })
    fig = px.bar(cmp, x="그룹", y="상세→구매 전환율(%)", color="그룹", text="상세→구매 전환율(%)",
                 color_discrete_sequence=["#e76f51", "#adb5bd"])
    fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
    fig.update_layout(height=320, showlegend=False, margin=dict(t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
    t = de["test"]
    verdict = "**H₀ 기각** — 딜이 전환율을 유의하게 높인다 ✅" if t["significant"] else "유의차 없음"
    st.info(f"2-비율 Z검정 · Z={t['z']} · p(단측)={t['p_value_one_sided']} → {verdict}")

st.divider()

# ── 3. 매출 시계열 ─────────────────────────────────────────────────
st.subheader("③ 일별 매출 추이")
daily = rv["daily"]
fig = px.area(daily, x="date", y="gmv", labels={"gmv": "GMV(원)", "date": "날짜"})
fig.update_traces(line_color="#2d6a4f")
fig.update_layout(height=300, margin=dict(t=10, b=10))
st.plotly_chart(fig, use_container_width=True)

# ── 4. 코호트 리텐션 ───────────────────────────────────────────────
st.subheader("④ 코호트 리텐션 (가입 주차 × N주 후 재구매, %)")
cr = kpi.cohort_retention(orders, data["users"])
cr_idx = cr.set_index(cr["cohort"].astype(str).str.slice(0, 10))
week_cols = [c for c in cr_idx.columns if c.startswith("week_")]
fig = px.imshow(cr_idx[week_cols], text_auto=".0f", aspect="auto",
                color_continuous_scale="Greens",
                labels=dict(x="가입 후 주차", y="코호트", color="리텐션%"))
fig.update_layout(height=360, margin=dict(t=10, b=10))
st.plotly_chart(fig, use_container_width=True)
st.caption("※ week_0 = 가입한 그 주에 실제 구매한 비율(획득 코호트 100% 정의와 다름, 의도된 것).")

st.divider()
lc, rc = st.columns(2)

# ── 5. 카테고리 성과 ───────────────────────────────────────────────
with lc:
    st.subheader("⑤ 카테고리별 성과")
    cp = kpi.category_performance(orders, data["products"])
    fig = px.bar(cp, x="category", y="gmv", text="orders",
                 labels={"gmv": "GMV(원)", "category": "카테고리"},
                 color="gmv", color_continuous_scale="Greens")
    fig.update_layout(height=320, margin=dict(t=10, b=10), coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

# ── 6. 상품 TOP ────────────────────────────────────────────────────
with rc:
    st.subheader("⑥ 상품 GMV TOP 10")
    pp = kpi.product_performance(events, orders, data["products"], top=10)
    st.dataframe(
        pp[["name", "category", "detail_view", "purchase", "detail_to_buy", "gmv"]],
        use_container_width=True, hide_index=True,
    )
