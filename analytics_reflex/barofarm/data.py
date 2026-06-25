"""
BaroFarm 분석 코어 (프레임워크 비종속)
=========================================
DB 직결 + scikit-learn ML + plotly Figure 생성을 순수 함수로 제공한다.
Streamlit / Reflex 어느 쪽에서도 그대로 import 해서 쓸 수 있도록 UI 의존성이 전혀 없다.

- DB:   SQLAlchemy + pymysql (docker-compose 의 mysql 서비스)
- ML:   Ridge / LinearRegression / KMeans / MinMax·StandardScaler
- 차트: plotly.graph_objects Figure 반환 (Reflex 의 rx.plotly, Streamlit 의 st.plotly_chart 공용)
"""
import os
import warnings
from functools import lru_cache

warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine, text

# sklearn 은 무겁다(스키피 포함 ~150MB). 1GB EC2 백엔드 시작 메모리를 줄이려
# 모듈 최상단이 아니라 실제 ML 함수 안에서 지연 임포트한다.

# ── 설정 ──────────────────────────────────────────────────────────
# ANALYTICS_DB_URL 우선(Reflex 내부 db_url 환경변수 DB_URL 과 충돌 회피). 로컬 편의로 DB_URL 폴백.
DB_URL = (
    os.getenv("ANALYTICS_DB_URL")
    or os.getenv("DB_URL")
    or "mysql+pymysql://root:1234@127.0.0.1:3306/freshgrowth?charset=utf8mb4"
)

CAT_KR = {
    "vegetable": "채소", "fruit": "과일", "seafood": "해산물",
    "meat": "육류", "grain": "곡물", "etc": "기타", "processed": "가공",
}

# plotly 공통 테마
GREEN_SEQ = ["#2D6A4F", "#40916C", "#52B788", "#74C69D", "#95D5B2", "#B7E4C7"]
SEG_COLORS = {
    "VIP 👑": "#2D6A4F", "충성고객 ⭐": "#52B788",
    "잠재고객 🌱": "#95D5B2", "이탈위험 ⚠️": "#F4845F",
}


def _base_layout(fig: go.Figure, title: str = "") -> go.Figure:
    fig.update_layout(
        title=title,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Pretendard, sans-serif", size=13),
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(orientation="h", y=-0.18),
    )
    return fig


# ── DB 헬퍼 ───────────────────────────────────────────────────────
_engine = None


def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(DB_URL, pool_pre_ping=True, pool_recycle=3600)
    return _engine


def q(sql: str) -> pd.DataFrame:
    return pd.read_sql(text(sql), get_engine())


def won(x) -> str:
    return f"{x:,.0f}원"


# ── 농장 메타 ─────────────────────────────────────────────────────
def list_sellers() -> pd.DataFrame:
    """주문이 있는 판매자 목록 (GMV 내림차순)."""
    return q("""
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


def seller_date_range(sid: int):
    df = q(f"""
        SELECT MIN(o.order_date) a, MAX(o.order_date) b
        FROM orders o JOIN products p ON o.product_id=p.product_id
        WHERE p.seller_id={sid}
    """)
    a, b = df.iloc[0]
    if pd.isna(a):
        return None, None
    return str(pd.to_datetime(a).date()), str(pd.to_datetime(b).date())


def load_orders(sid: int, d0: str, d1: str) -> pd.DataFrame:
    o = q(f"""
        SELECT o.order_id, o.buyer_id, o.order_date, o.quantity, o.total_price,
               o.original_unit_price, o.status, o.lot_id,
               p.product_id, p.name AS product_name, p.category
        FROM orders o JOIN products p ON o.product_id = p.product_id
        WHERE p.seller_id = {sid}
          AND o.order_date BETWEEN '{d0} 00:00:00' AND '{d1} 23:59:59'
    """)
    if o.empty:
        return o
    o["order_date"] = pd.to_datetime(o["order_date"])
    o["date"] = o["order_date"].dt.normalize()
    o["saved"] = (o["original_unit_price"].fillna(0) * o["quantity"] - o["total_price"]).clip(lower=0)
    o["is_deal"] = o["saved"] > 0
    return o


def farm_kpis(o: pd.DataFrame) -> dict:
    """포맷된 KPI 문자열 dict."""
    gmv = o["total_price"].sum()
    per_buyer = o.groupby("buyer_id").size()
    deal_rev = o.loc[o["is_deal"], "total_price"].sum()
    return {
        "gmv": won(gmv),
        "orders": f"{len(o):,}건",
        "aov": won(o["total_price"].mean()),
        "buyers": f"{o['buyer_id'].nunique():,}명",
        "repurchase": f"{(per_buyer >= 2).mean() * 100:.1f}%",
        "deal_rev": won(deal_rev),
        "deal_share": f"전체의 {deal_rev / gmv * 100:.0f}%" if gmv else "-",
    }


# ════════════════════════════════════════════════════════════════
#  ML 모듈 (dashboard.py 와 동일 로직, st.cache → lru_cache)
# ════════════════════════════════════════════════════════════════
@lru_cache(maxsize=64)
def ai_revenue_forecast(sid: int, d0: str, d1: str):
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
        np.sin(2*np.pi*idx/7),  np.cos(2*np.pi*idx/7),
        np.sin(2*np.pi*idx/30), np.cos(2*np.pi*idx/30),
    ])
    y = daily["revenue"].values.astype(float)

    from sklearn.linear_model import Ridge
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
        "future_dates": future_dates,
        "preds": preds,
        "std": residual_std,
        "score": float(model.score(X, y)),
    }


@lru_cache(maxsize=64)
def ai_purchase_reco(sid: int, d0: str, d1: str):
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
    df["date"] = df["order_date"].dt.normalize()

    last = df["date"].max()
    df30 = df[df["date"] > last - pd.Timedelta(days=30)]
    df_30_60 = df[(df["date"] <= last - pd.Timedelta(days=30)) &
                  (df["date"] > last - pd.Timedelta(days=60))]

    agg = df.groupby(["product_id", "product_name", "category"]).agg(
        total_qty=("quantity", "sum"),
        total_rev=("total_price", "sum"),
        orders=("order_id", "nunique"),
        buyers=("buyer_id", "nunique"),
        active_days=("date", lambda x: max((x.max() - x.min()).days + 1, 1)),
    ).reset_index()

    recent = df30.groupby("product_id")["total_price"].sum().rename("recent_rev")
    prev = df_30_60.groupby("product_id")["total_price"].sum().rename("prev_rev")

    agg = agg.join(recent, on="product_id").join(prev, on="product_id").fillna(0)
    agg["velocity"] = agg["total_qty"] / agg["active_days"]
    agg["trend"] = (agg["recent_rev"] + 1) / (agg["prev_rev"] + 1)
    agg["rev_share"] = agg["total_rev"] / agg["total_rev"].sum()
    agg["repurchase"] = (agg["orders"] / agg["buyers"].clip(lower=1)).clip(upper=5) / 5

    feats = ["velocity", "trend", "rev_share", "repurchase"]
    weights = np.array([0.30, 0.35, 0.20, 0.15])
    from sklearn.preprocessing import MinMaxScaler
    scaled = MinMaxScaler().fit_transform(agg[feats])
    agg["score"] = (scaled * weights).sum(axis=1) * 100

    agg["카테고리"] = agg["category"].map(CAT_KR).fillna(agg["category"])
    agg["추천점수"] = agg["score"].round(1)
    agg["트렌드"] = agg["trend"].apply(lambda t: "📈 상승" if t > 1.1 else ("📉 하락" if t < 0.9 else "➡️ 유지"))
    agg["이유"] = agg.apply(lambda r:
        "🔥 최근 급상승+고속도" if r.trend > 1.2 and r.velocity > 2 else
        "⭐ 안정적 재구매" if r.repurchase > 0.4 else
        "📦 매출 핵심 상품" if r.rev_share > 0.05 else
        "🌱 성장 잠재력", axis=1)

    return agg.sort_values("score", ascending=False).head(10)


@lru_cache(maxsize=64)
def ai_demand_forecast(sid: int, d0: str, d1: str):
    """상위 8개 상품의 주간 수요 → LinearRegression → 4주 예측."""
    df = q(f"""
        SELECT o.order_date, o.quantity, p.product_id, p.name AS product_name, p.category
        FROM orders o JOIN products p ON o.product_id=p.product_id
        WHERE p.seller_id={sid} AND o.order_date BETWEEN '{d0} 00:00:00' AND '{d1} 23:59:59'
    """)
    if df.empty:
        return None
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["week"] = df["order_date"].dt.to_period("W").astype(str)

    top_pids = df.groupby("product_id")["quantity"].sum().nlargest(8).index
    from sklearn.linear_model import LinearRegression
    results = []
    for pid in top_pids:
        sub = df[df["product_id"] == pid]
        weekly = sub.groupby("week")["quantity"].sum().reset_index(name="qty")
        if len(weekly) < 4:
            continue
        X = np.arange(len(weekly), dtype=float).reshape(-1, 1)
        y = weekly["qty"].values.astype(float)
        m = LinearRegression().fit(X, y)
        f4 = m.predict(np.arange(len(weekly), len(weekly) + 4, dtype=float).reshape(-1, 1)).clip(0)
        results.append({
            "product_id": pid,
            "product_name": sub["product_name"].iloc[0],
            "category": sub["category"].iloc[0],
            "avg_qty": float(y.mean()),
            "forecast_avg": float(f4.mean()),
            "trend_pct": float((f4[-1] - y[-1]) / (y[-1] + 1) * 100),
        })
    return pd.DataFrame(results) if results else None


@lru_cache(maxsize=64)
def ai_customer_segments(sid: int, d0: str, d1: str):
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
        recency=("order_date", lambda x: (last - x.max()).days),
        frequency=("order_id", "nunique"),
        monetary=("total_price", "sum"),
    ).reset_index()

    n_clusters = min(4, len(rfm))
    if n_clusters < 2:
        return None

    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import KMeans
    scaled = StandardScaler().fit_transform(rfm[["recency", "frequency", "monetary"]])
    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10).fit(scaled)
    rfm["cluster"] = km.labels_

    order = rfm.groupby("cluster")["monetary"].median().sort_values().index
    names = ["이탈위험 ⚠️", "잠재고객 🌱", "충성고객 ⭐", "VIP 👑"][:n_clusters]
    label_map = {c: names[i] for i, c in enumerate(order)}
    rfm["segment"] = rfm["cluster"].map(label_map)
    rfm["recency_inv"] = 1 / (rfm["recency"] + 1)
    return rfm


@lru_cache(maxsize=64)
def ai_seasonality(sid: int, d0: str, d1: str):
    """카테고리×월별 매출 히트맵 + 성장률 분석."""
    df = q(f"""
        SELECT o.order_date, o.total_price, p.category
        FROM orders o JOIN products p ON o.product_id=p.product_id
        WHERE p.seller_id={sid} AND o.order_date BETWEEN '{d0} 00:00:00' AND '{d1} 23:59:59'
    """)
    if df.empty:
        return None, None
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["month"] = df["order_date"].dt.strftime("%Y-%m")
    df["day"] = df["order_date"].dt.normalize()
    df["cat_kr"] = df["category"].map(CAT_KR).fillna(df["category"])

    pivot = df.groupby(["month", "cat_kr"])["total_price"].sum().unstack(fill_value=0)
    months = sorted(df["month"].unique())

    # 전월 대비 카테고리 성장률 — '일평균 매출' 기준으로 정규화한다.
    # (당월이 부분월[예: 6월 22일까지]이면 전체월과 총액 비교 시 성장률이
    #  부당하게 낮게 나오므로, 각 월의 '주문 있었던 날 수'로 나눠 공정 비교)
    growth = pd.Series(dtype=float)
    growth_table = []   # [카테고리, 전월 일평균, 당월 일평균, 성장률표시]
    if len(months) >= 2:
        last_m, prev_m = months[-1], months[-2]
        days_last = max(df[df["month"] == last_m]["day"].nunique(), 1)
        days_prev = max(df[df["month"] == prev_m]["day"].nunique(), 1)
        last_avg = df[df["month"] == last_m].groupby("cat_kr")["total_price"].sum() / days_last
        prev_avg = df[df["month"] == prev_m].groupby("cat_kr")["total_price"].sum() / days_prev
        cats = sorted(set(last_avg.index) | set(prev_avg.index))
        la = last_avg.reindex(cats, fill_value=0.0)
        pa = prev_avg.reindex(cats, fill_value=0.0)
        growth = ((la - pa) / (pa + 1) * 100).sort_values(ascending=False)
        for c in growth.index:
            p = float(growth[c])
            arrow = "📈" if p > 3 else ("📉" if p < -3 else "➡️")
            growth_table.append([c, won(float(pa[c])), won(float(la[c])), f"{arrow} {p:+.1f}%"])

    return pivot, growth, growth_table


# ════════════════════════════════════════════════════════════════
#  Figure 빌더 (plotly go.Figure 반환)
# ════════════════════════════════════════════════════════════════
def fig_revenue(res, sname: str) -> go.Figure:
    daily = res["daily"]
    fdates = pd.DatetimeIndex(res["future_dates"])
    preds = np.array(res["preds"])
    std = res["std"]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=daily["date"], y=daily["revenue"],
                         name="실제 매출", marker_color="#74C69D", opacity=0.7))
    fig.add_trace(go.Scatter(x=fdates, y=preds, mode="lines+markers",
                             name="30일 예측", line=dict(color="#F4845F", width=2.5, dash="dot")))
    fig.add_trace(go.Scatter(
        x=list(fdates) + list(fdates[::-1]),
        y=list((preds + std).clip(0)) + list((preds - std).clip(0)[::-1]),
        fill="toself", fillcolor="rgba(244,132,95,0.15)",
        line=dict(color="rgba(255,255,255,0)"), name="±1σ 신뢰구간"))
    return _base_layout(fig, f"{sname} — 일별 매출 및 30일 예측 (Ridge Regression)")


def fig_reco(reco) -> go.Figure:
    d = reco.sort_values("score")
    fig = px.bar(d, x="score", y="product_name", orientation="h",
                 color="score", color_continuous_scale="YlGn", text="추천점수")
    fig.update_traces(texttemplate="%{text}점", textposition="outside")
    fig = _base_layout(fig, "매입 추천 점수 (100점 만점)")
    fig.update_layout(yaxis_title="", xaxis_title="추천 점수", coloraxis_showscale=False)
    return fig


def fig_demand(dem) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Bar(x=dem["product_name"].str.slice(0, 14), y=dem["avg_qty"],
                         name="현재 주간 수요", marker_color="#74C69D"))
    fig.add_trace(go.Bar(x=dem["product_name"].str.slice(0, 14), y=dem["forecast_avg"],
                         name="4주 후 예측", marker_color="#F4845F", marker_pattern_shape="/"))
    fig = _base_layout(fig, "현재 주간 평균 수요 vs 4주 후 예측")
    fig.update_layout(barmode="group", xaxis_tickangle=-30)
    return fig


def fig_segments(rfm) -> go.Figure:
    fig = px.scatter(rfm, x="frequency", y="monetary", color="segment",
                     size="recency_inv", color_discrete_map=SEG_COLORS,
                     labels={"frequency": "구매 횟수", "monetary": "총 구매액(원)", "segment": "세그먼트"})
    return _base_layout(fig, "고객 분포 (x=구매횟수, y=총매출, 점크기=최근성)")


def fig_season_heat(pivot) -> go.Figure:
    fig = px.imshow(pivot.T, text_auto=".0f", aspect="auto",
                    color_continuous_scale="Greens",
                    labels=dict(x="월", y="카테고리", color="매출"))
    return _base_layout(fig, "카테고리 × 월별 매출 (원)")


def fig_season_growth(growth) -> go.Figure:
    g = growth.reset_index()
    g.columns = ["cat", "pct"]
    fig = px.bar(g, x="cat", y="pct", color="pct",
                 color_continuous_scale=["#F4845F", "#FFFFFF", "#52B788"],
                 color_continuous_midpoint=0, text_auto=".1f")
    fig.update_traces(texttemplate="%{text}%")
    fig = _base_layout(fig, "전월 대비 카테고리 일평균 매출 성장률 (%)")
    fig.update_layout(coloraxis_showscale=False, xaxis_title="카테고리", yaxis_title="성장률(%)")
    return fig


# ════════════════════════════════════════════════════════════════
#  📅 달력 데이터 (주문일 + 재고만료일)
# ════════════════════════════════════════════════════════════════
def calendar_data(sid: int, year: int, month: int, ref=None) -> list:
    """해당 월의 달력 셀 목록(42셀 = 6주×7일) 반환.
    각 셀: [day_str, order_count_str, type_str]
    type_str: 'today' | 'expiry' | 'order' | 'normal' | 'empty'
    ref(date) 지정 시 그 날짜를 'today'(활성)로 강조. 미지정 시 시스템 오늘.
    """
    import calendar as cal_lib
    from datetime import date as _date

    if ref is None:
        ref = _date.today()

    first_weekday, total_days = cal_lib.monthrange(year, month)
    # Python Mon=0,Sun=6 → 일요일 시작(Sun=0)
    start_offset = (first_weekday + 1) % 7

    d0 = f"{year}-{month:02d}-01"
    d1 = f"{year}-{month:02d}-{total_days:02d}"

    try:
        ord_df = q(f"""
            SELECT DAY(o.order_date) AS d, COUNT(*) AS cnt
            FROM orders o JOIN products p ON o.product_id=p.product_id
            WHERE p.seller_id={sid}
              AND DATE(o.order_date) BETWEEN '{d0}' AND '{d1}'
            GROUP BY DAY(o.order_date)
        """)
        order_map = {int(r.d): int(r.cnt) for r in ord_df.itertuples()} if not ord_df.empty else {}
    except Exception:
        order_map = {}

    try:
        lot_df = q(f"""
            SELECT DAY(pl.expiration_date) AS d
            FROM product_lots pl JOIN products p ON pl.product_id=p.product_id
            WHERE p.seller_id={sid}
              AND YEAR(pl.expiration_date)={year} AND MONTH(pl.expiration_date)={month}
              AND pl.stock_qty > 0
        """)
        expiry_set = set(int(r.d) for r in lot_df.itertuples()) if not lot_df.empty else set()
    except Exception:
        expiry_set = set()

    cells = []
    for i in range(42):
        day_num = i - start_offset + 1
        if 1 <= day_num <= total_days:
            is_today = (year == ref.year and month == ref.month and day_num == ref.day)
            cnt = order_map.get(day_num, 0)
            has_expiry = day_num in expiry_set
            if is_today:
                ctype = "today"
            elif has_expiry:
                ctype = "expiry"
            elif cnt > 0:
                ctype = "order"
            else:
                ctype = "normal"
            cells.append([str(day_num), str(cnt), ctype])
        else:
            cells.append(["", "0", "empty"])

    return cells


def today_delivery_summary(sid: int) -> dict:
    """최근 영업일 주문 건수, 7일 내 만료 예정 재고(로트) 건수."""
    from datetime import timedelta
    ref = latest_order_date(sid)          # 데모 데이터 기준 최근 영업일
    week_end = ref + timedelta(days=7)
    try:
        ord_today = q(f"""
            SELECT COUNT(*) cnt FROM orders o
            JOIN products p ON o.product_id=p.product_id
            WHERE p.seller_id={sid} AND DATE(o.order_date)='{ref}'
        """).iloc[0, 0]
    except Exception:
        ord_today = 0
    try:
        exp_week = q(f"""
            SELECT COUNT(*) cnt FROM product_lots pl
            JOIN products p ON pl.product_id=p.product_id
            WHERE p.seller_id={sid} AND pl.stock_qty>0
              AND pl.expiration_date BETWEEN '{ref}' AND '{week_end}'
        """).iloc[0, 0]
    except Exception:
        exp_week = 0
    return {"today_orders": int(ord_today), "expiry_week": int(exp_week)}


_STATUS_KR = {
    "PENDING": "접수", "CONFIRMED": "확정", "SHIPPING": "배송중",
    "COMPLETED": "완료", "CANCELLED": "취소",
}


@lru_cache(maxsize=64)
def latest_order_date(sid: int):
    """판매자의 가장 최근 주문일(date). 없으면 시스템 오늘."""
    from datetime import date as _date
    try:
        r = q(f"""
            SELECT MAX(DATE(o.order_date)) md
            FROM orders o JOIN products p ON o.product_id=p.product_id
            WHERE p.seller_id={sid}
        """)
        v = r.iloc[0, 0]
        if v is None:
            return _date.today()
        return pd.to_datetime(str(v)).date()
    except Exception:
        return _date.today()


def weekly_orders_data(sid: int, ref=None) -> list:
    """기준일까지의 최근 7일(ref-6 ~ ref) 주문 이벤트 카드 목록 반환.
    기준일(ref) 미지정 시 가장 최근 주문일을 사용(데모 데이터가 과거일 수 있어서).
    반환: list[dict] 길이=7, 각 dict:
      {weekday, date_str, iso, is_today(bool), revenue_str, orders:[...]}
    """
    from datetime import timedelta

    if ref is None:
        ref = latest_order_date(sid)
    days = [ref - timedelta(days=6 - i) for i in range(7)]
    dow_full = ["월", "화", "수", "목", "금", "토", "일"]
    dow_kr = [dow_full[d.weekday()] for d in days]

    d0_str, d1_str = str(days[0]), str(days[6])

    try:
        df = q(f"""
            SELECT
                DATE(o.order_date) AS od,
                p.name AS product_name,
                o.buyer_id,
                o.total_price,
                o.status
            FROM orders o
            JOIN products p ON o.product_id = p.product_id
            WHERE p.seller_id = {sid}
              AND DATE(o.order_date) BETWEEN '{d0_str}' AND '{d1_str}'
            ORDER BY o.order_date
        """)
        if not df.empty:
            df["od"] = pd.to_datetime(df["od"]).dt.date
    except Exception:
        df = pd.DataFrame()

    result = []
    for i, d in enumerate(days):
        day_orders = []
        day_rev = 0.0
        if not df.empty:
            rows = df[df["od"] == d]
            day_rev = float(rows["total_price"].sum())
            for _, row in rows.iterrows():
                status = str(row.get("status", "")).upper()
                day_orders.append({
                    "product": str(row["product_name"])[:12],
                    "buyer": f"고객{str(row['buyer_id'])[-3:]}",
                    "amount_str": won(float(row["total_price"])),
                    "status": _STATUS_KR.get(status, "접수"),
                })
        result.append({
            "weekday": dow_kr[i],
            "date_str": f"{d.month}/{d.day}",
            "iso": str(d),
            "is_today": (d == ref),
            "revenue_str": won(day_rev),
            "orders": day_orders,
        })
    return result


def daily_detail(sid: int, date_str: str) -> dict:
    """특정 날짜의 매출/주문건수/판매수량/대표상품."""
    try:
        df = q(f"""
            SELECT o.total_price, o.quantity, p.name AS product_name
            FROM orders o JOIN products p ON o.product_id=p.product_id
            WHERE p.seller_id={sid} AND DATE(o.order_date)='{date_str}'
        """)
    except Exception:
        df = pd.DataFrame()
    if df.empty:
        return {"revenue": "0원", "orders": "0건", "items": "0개", "top": "주문 없음"}
    revenue = won(float(df["total_price"].sum()))
    orders = f"{len(df)}건"
    items = f"{int(df['quantity'].sum())}개"
    top = str(df.groupby("product_name")["total_price"].sum().idxmax())
    return {"revenue": revenue, "orders": orders, "items": items, "top": top}


# ════════════════════════════════════════════════════════════════
#  🚚 공급망 · 수요 최적화 (재고 × 판매속도 → 발주/폐기 의사결정)
# ════════════════════════════════════════════════════════════════
LEAD_TIME_DAYS = 3      # 매입 리드타임(발주→입고)
TARGET_DAYS    = 14     # 목표 보유 재고 일수(2주)
OVERSTOCK_DAYS = 30     # 과잉재고 판단 기준
DEMAND_WINDOW  = 30     # 판매속도 산정 기간(일)


@lru_cache(maxsize=64)
def supply_demand_optimization(sid: int):
    """상품별 현재고 × 최근 판매속도 → 재고 소진일수·발주권장량·폐기위험 산출.
    반환: DataFrame(우선순위 정렬). 비면 None.
    컬럼: product_name, category_kr, stock, daily_demand, days_supply,
          days_to_expiry, expiring_qty, waste_qty, waste_won,
          reorder_qty, status, action
    """
    from datetime import timedelta
    ref = latest_order_date(sid)
    win_start = ref - timedelta(days=DEMAND_WINDOW - 1)
    exp_horizon = ref + timedelta(days=7)

    # 최근 N일 판매속도
    sales = q(f"""
        SELECT p.product_id, p.name AS product_name, p.category,
               COALESCE(SUM(o.quantity),0) AS qty_win
        FROM products p
        LEFT JOIN orders o ON o.product_id=p.product_id
             AND o.order_date BETWEEN '{win_start} 00:00:00' AND '{ref} 23:59:59'
        WHERE p.seller_id={sid}
        GROUP BY p.product_id, p.name, p.category
    """)
    if sales.empty:
        return None

    # 유효 재고(미만료 로트) + 최단 만료일 + 7일내 만료 수량 + 가중 단가
    stock = q(f"""
        SELECT p.product_id,
               COALESCE(SUM(pl.stock_qty),0) AS stock,
               MIN(pl.expiration_date) AS earliest_expiry,
               COALESCE(SUM(CASE WHEN pl.expiration_date <= '{exp_horizon}'
                                 THEN pl.stock_qty ELSE 0 END),0) AS expiring_qty,
               COALESCE(SUM(pl.stock_qty * pl.price),0) AS stock_value
        FROM products p
        LEFT JOIN product_lots pl ON pl.product_id=p.product_id
             AND pl.stock_qty>0 AND pl.expiration_date >= '{ref}'
        WHERE p.seller_id={sid}
        GROUP BY p.product_id
    """)

    df = sales.merge(stock, on="product_id", how="left").fillna(
        {"stock": 0, "expiring_qty": 0, "stock_value": 0})
    df["category_kr"] = df["category"].map(CAT_KR).fillna(df["category"])
    df["daily_demand"] = (df["qty_win"] / DEMAND_WINDOW).round(2)

    def _days_supply(r):
        if r["daily_demand"] <= 0:
            return 999.0 if r["stock"] > 0 else 0.0
        return round(r["stock"] / r["daily_demand"], 1)
    df["days_supply"] = df.apply(_days_supply, axis=1)

    def _days_to_expiry(r):
        e = r["earliest_expiry"]
        if pd.isna(e):
            return 999
        return max((pd.to_datetime(e).date() - ref).days, 0)
    df["days_to_expiry"] = df.apply(_days_to_expiry, axis=1)

    df["unit_price"] = (df["stock_value"] / df["stock"].replace(0, pd.NA)).fillna(0)

    # 만료 전 예상 판매량 → 폐기 위험 수량/금액
    df["sellable_before_expiry"] = (df["daily_demand"] * df["days_to_expiry"]).round(0)
    df["waste_qty"] = (df["expiring_qty"] - df["sellable_before_expiry"]).clip(lower=0)
    df["waste_won"] = (df["waste_qty"] * df["unit_price"]).round(0)

    # 권장 발주량(목표 재고 - 현재고, 양수일 때)
    df["reorder_qty"] = (df["daily_demand"] * TARGET_DAYS - df["stock"]).clip(lower=0).round(0)

    def _status(r):
        if r["daily_demand"] <= 0 and r["stock"] > 0:
            return "💤 판매정체"
        if r["stock"] <= 0:
            return "⛔ 품절"
        if r["days_supply"] < LEAD_TIME_DAYS:
            return "🔴 품절임박"
        if r["waste_qty"] > 0:
            return "🟡 폐기위험"
        if r["days_supply"] > OVERSTOCK_DAYS:
            return "🔵 과잉재고"
        return "🟢 적정"
    df["status"] = df.apply(_status, axis=1)

    def _action(r):
        s = r["status"]
        if s == "⛔ 품절":
            return f"즉시 발주 {int(r['reorder_qty'])}개"
        if s == "🔴 품절임박":
            return f"발주 권장 {int(r['reorder_qty'])}개 ({r['days_supply']:.0f}일분)"
        if s == "🟡 폐기위험":
            return f"할인·번들로 {int(r['waste_qty'])}개 소진({won(r['waste_won'])})"
        if s == "🔵 과잉재고":
            return "매입 중단·프로모션 검토"
        if s == "💤 판매정체":
            return "노출 강화·할인 검토"
        return "현 수준 유지"
    df["action"] = df.apply(_action, axis=1)

    prio = {"⛔ 품절": 0, "🔴 품절임박": 1, "🟡 폐기위험": 2,
            "💤 판매정체": 3, "🔵 과잉재고": 4, "🟢 적정": 5}
    df["_p"] = df["status"].map(prio)
    return df.sort_values(["_p", "days_supply"]).reset_index(drop=True)


def supply_summary(sid: int) -> dict:
    """공급망 KPI: 품절위험·폐기위험 품목수, 예상 폐기손실, 발주권장 품목수."""
    df = supply_demand_optimization(sid)
    if df is None or df.empty:
        return {"shortage": 0, "expiry": 0, "waste_won": "0원", "reorder": 0}
    shortage = int(df["status"].isin(["⛔ 품절", "🔴 품절임박"]).sum())
    expiry = int((df["waste_qty"] > 0).sum())
    waste_won = won(float(df["waste_won"].sum()))
    reorder = int((df["reorder_qty"] > 0).sum())
    return {"shortage": shortage, "expiry": expiry,
            "waste_won": waste_won, "reorder": reorder}


# 성공한 LLM 응답만 캐시(실패=폴백은 캐시하지 않아 재시도 가능)
_supply_ai_cache: dict[int, str] = {}


def _supply_feedback_fallback(s: dict) -> str:
    """LLM 호출 불가 시 규칙 기반 요약(키 미설정/네트워크 오류 대비)."""
    return (
        f"• 품절 위험 {s['shortage']}개 품목 — 리드타임(3일) 내 소진이 우려되니 우선 발주하세요.\n"
        f"• 폐기 위험 {s['expiry']}개 품목, 예상 손실 {s['waste_won']} — 할인·번들로 만료 전 소진을 유도하세요.\n"
        f"• 발주 권장 {s['reorder']}개 품목 — 목표 재고(2주) 기준으로 보충이 필요합니다.\n"
        "※ AI 분석 키가 설정되지 않아 규칙 기반 요약을 표시합니다."
    )


def ai_supply_feedback(sid: int) -> str:
    """공급망 데이터를 요약해 SSAFY GMS(OpenAI 호환) LLM 으로 종합 분석을 생성.
    AI_BASE_URL / AI_API_KEY / AI_MODEL 환경변수 사용. 실패 시 규칙 기반 폴백."""
    if sid in _supply_ai_cache:
        return _supply_ai_cache[sid]

    df = supply_demand_optimization(sid)
    s = supply_summary(sid)
    if df is None or df.empty:
        return ""

    # 위험 품목(적정 제외) 상위 8개를 컨텍스트로
    risk = df[df["status"] != "🟢 적정"].head(8)
    lines = [
        f"- {r.product_name}({r.category_kr}): 현재고 {int(r.stock)}개, 일수요 {r.daily_demand}개, "
        f"소진 {r.days_supply}일, 최단만료 D-{int(r.days_to_expiry)}, 상태 {r.status}, 권장 {r.action}"
        for r in risk.itertuples()
    ]
    context = (
        f"[공급망 KPI] 품절위험 {s['shortage']}품목 · 폐기위험 {s['expiry']}품목 · "
        f"예상폐기손실 {s['waste_won']} · 발주권장 {s['reorder']}품목\n"
        f"[위험 품목]\n" + ("\n".join(lines) if lines else "- 특이 위험 품목 없음")
    )

    api_key = os.getenv("AI_API_KEY")
    base_url = os.getenv("AI_BASE_URL")
    model = os.getenv("AI_MODEL", "gpt-4o-mini")
    if not api_key or not base_url:
        return _supply_feedback_fallback(s)

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key, base_url=base_url, timeout=25, max_retries=1)
        resp = client.chat.completions.create(
            model=model,
            temperature=0.4,
            max_tokens=550,
            messages=[
                {"role": "system", "content":
                    "당신은 신선식품 농장의 공급망·재고 최적화를 돕는 데이터 애널리스트입니다. "
                    "주어진 KPI와 위험 품목 데이터만 근거로, 군더더기 없이 실행 가능한 한국어 조언을 작성하세요. "
                    "형식: 첫 줄에 한 문장 종합 진단, 이어서 '•'로 시작하는 핵심 인사이트 3~4개"
                    "(각 항목은 수치 근거 + 구체 조치). 마지막 줄에 '✅ 우선 조치:' 로 가장 시급한 1가지. "
                    "과장·일반론 금지, 데이터에 없는 내용 지어내지 말 것."},
                {"role": "user", "content":
                    f"다음 공급망 현황을 종합 분석해 주세요.\n\n{context}"},
            ],
        )
        text = (resp.choices[0].message.content or "").strip()
        if text:
            _supply_ai_cache[sid] = text
            return text
        return _supply_feedback_fallback(s)
    except Exception as e:  # noqa: BLE001
        return f"{_supply_feedback_fallback(s)}\n(분석 호출 오류: {type(e).__name__})"


def fig_supply(df) -> go.Figure:
    """상품별 재고 소진일수(가로 막대, 상태별 색)."""
    color_map = {
        "⛔ 품절": "#9CA3AF", "🔴 품절임박": "#EF4444", "🟡 폐기위험": "#F59E0B",
        "💤 판매정체": "#A78BFA", "🔵 과잉재고": "#3B82F6", "🟢 적정": "#22C55E",
    }
    d = df.copy()
    d["plot_days"] = d["days_supply"].clip(upper=60)  # 표시용 상한
    d["short"] = d["product_name"].str.slice(0, 16)
    d = d.iloc[::-1]  # 위에서부터 우선순위
    fig = go.Figure(go.Bar(
        x=d["plot_days"], y=d["short"], orientation="h",
        marker_color=[color_map.get(s, "#94A3B8") for s in d["status"]],
        text=[f"{v:.0f}일" if v < 60 else "60일+" for v in d["days_supply"]],
        textposition="outside",
        hovertext=[f"{s} · 현재고 {int(st)}개 · 발주권장 {int(r)}개"
                   for s, st, r in zip(d["status"], d["stock"], d["reorder_qty"])],
        hoverinfo="text",
    ))
    fig.add_vline(x=LEAD_TIME_DAYS, line_dash="dot", line_color="#EF4444",
                  annotation_text="리드타임", annotation_position="top")
    fig.add_vline(x=TARGET_DAYS, line_dash="dot", line_color="#22C55E",
                  annotation_text="목표재고", annotation_position="top")
    fig.update_xaxes(title="재고 소진 예상일수 (일)", gridcolor="#EEF2F6")
    fig.update_yaxes(title="")
    return _base_layout(fig, "")


# ════════════════════════════════════════════════════════════════
#  📞 핫라인 / 🚚 배송내역 / 🧾 청구 / 📦 보관상품 / 🔔 알림
# ════════════════════════════════════════════════════════════════
_ORDER_STATUS_KR = {
    "PENDING": "접수 대기", "CONFIRMED": "주문 확정", "SHIPPING": "배송 중",
    "COMPLETED": "배송 완료", "CANCELLED": "취소",
}


def order_status_summary(sid: int) -> dict:
    """주문 상태별 건수·매출. keys: pending/confirmed/shipping/completed/cancelled/total."""
    try:
        df = q(f"""
            SELECT o.status, COUNT(*) cnt, COALESCE(SUM(o.total_price),0) rev
            FROM orders o JOIN products p ON o.product_id=p.product_id
            WHERE p.seller_id={sid}
            GROUP BY o.status
        """)
    except Exception:
        df = pd.DataFrame()
    out = {k: 0 for k in ["pending", "confirmed", "shipping", "completed", "cancelled"]}
    rev = dict(out)
    keymap = {"PENDING": "pending", "CONFIRMED": "confirmed", "SHIPPING": "shipping",
              "COMPLETED": "completed", "CANCELLED": "cancelled"}
    for _, r in df.iterrows():
        k = keymap.get(str(r["status"]).upper())
        if k:
            out[k] = int(r["cnt"])
            rev[k] = float(r["rev"])
    out["total"] = sum(out.values())
    out["rev"] = rev
    return out


def recent_orders(sid: int, n: int = 40) -> list:
    """최근 주문 목록: [날짜, 상품, 고객, 수량, 금액, 상태]."""
    try:
        df = q(f"""
            SELECT DATE(o.order_date) od, p.name pname, o.buyer_id,
                   o.quantity, o.total_price, o.status
            FROM orders o JOIN products p ON o.product_id=p.product_id
            WHERE p.seller_id={sid}
            ORDER BY o.order_date DESC LIMIT {n}
        """)
    except Exception:
        df = pd.DataFrame()
    rows = []
    for _, r in df.iterrows():
        rows.append([
            str(r["od"]),
            str(r["pname"])[:18],
            f"고객{int(r['buyer_id']) % 1000:03d}",
            f"{int(r['quantity'])}개",
            won(float(r["total_price"])),
            _ORDER_STATUS_KR.get(str(r["status"]).upper(), str(r["status"])),
        ])
    return rows


def billing_monthly(sid: int):
    """월별 매출/할인/정산 요약 DataFrame(ym, orders, revenue, discount, net)."""
    try:
        df = q(f"""
            SELECT DATE_FORMAT(o.order_date,'%Y-%m') ym,
                   COUNT(*) orders,
                   COALESCE(SUM(o.total_price),0) revenue,
                   COALESCE(SUM(GREATEST(COALESCE(o.original_unit_price,0)*o.quantity
                                         - o.total_price,0)),0) discount
            FROM orders o JOIN products p ON o.product_id=p.product_id
            WHERE p.seller_id={sid}
            GROUP BY ym ORDER BY ym
        """)
    except Exception:
        df = pd.DataFrame()
    if df.empty:
        return None
    # 정산액(net) = 매출 - 수수료(가정 3.3%)
    df["fee"] = (df["revenue"] * 0.033).round(0)
    df["net"] = df["revenue"] - df["fee"]
    return df


def fig_billing(df) -> go.Figure:
    """월별 매출(막대) + 할인(막대) 비교."""
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["ym"], y=df["revenue"], name="매출",
                         marker_color="#1B5E3F"))
    fig.add_trace(go.Bar(x=df["ym"], y=df["discount"], name="할인 회수 매출",
                         marker_color="#F59E0B"))
    fig.update_layout(barmode="group")
    fig.update_xaxes(title="")
    fig.update_yaxes(title="원", gridcolor="#EEF2F6")
    return _base_layout(fig, "")


def inventory_lots(sid: int) -> list:
    """보관상품(로트) 목록: [상품, 재고, 만료(D-), 단가, 상태]."""
    from datetime import timedelta  # noqa: F401
    ref = latest_order_date(sid)
    try:
        df = q(f"""
            SELECT p.name pname, pl.stock_qty, pl.expiration_date exp, pl.price
            FROM product_lots pl JOIN products p ON pl.product_id=p.product_id
            WHERE p.seller_id={sid} AND pl.stock_qty>0
            ORDER BY pl.expiration_date ASC
        """)
    except Exception:
        df = pd.DataFrame()
    rows = []
    for _, r in df.iterrows():
        dleft = (pd.to_datetime(r["exp"]).date() - ref).days
        if dleft <= 3:
            status = "🔴 만료임박"
        elif dleft <= 7:
            status = "🟡 주의"
        else:
            status = "🟢 정상"
        rows.append([
            str(r["pname"])[:18],
            f"{int(r['stock_qty'])}개",
            f"D-{dleft}" if dleft >= 0 else "만료",
            won(float(r["price"])),
            status,
        ])
    return rows


def alerts_data(sid: int) -> list:
    """운영 알림 모음: [icon, 제목, 상세, 심각도]. 심각도 순 정렬."""
    df = supply_demand_optimization(sid)
    alerts = []
    if df is not None and not df.empty:
        for _, r in df.iterrows():
            if r["status"] in ("⛔ 품절", "🔴 품절임박"):
                alerts.append(["🔴", "품절 위험",
                               f"{r['product_name']} · 소진 {r['days_supply']:.0f}일분 · "
                               f"발주 {int(r['reorder_qty'])}개 권장", "긴급"])
            elif r["waste_qty"] > 0:
                alerts.append(["🟡", "만료 임박",
                               f"{r['product_name']} · {int(r['expiring_qty'])}개 "
                               f"D-{int(r['days_to_expiry'])} · 폐기위험 {int(r['waste_qty'])}개 "
                               f"({won(r['waste_won'])})", "주의"])
            elif r["status"] == "🔵 과잉재고":
                alerts.append(["🔵", "과잉 재고",
                               f"{r['product_name']} · 소진 {r['days_supply']:.0f}일분 · "
                               f"매입 축소 검토", "정보"])
            elif r["status"] == "💤 판매정체":
                alerts.append(["💤", "판매 정체",
                               f"{r['product_name']} · 최근 판매 없음 · 노출/할인 검토", "정보"])
    sev = {"긴급": 0, "주의": 1, "정보": 2}
    alerts.sort(key=lambda a: sev.get(a[3], 9))
    return alerts
