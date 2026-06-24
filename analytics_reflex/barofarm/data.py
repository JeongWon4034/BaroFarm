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

from sklearn.linear_model import Ridge, LinearRegression
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.cluster import KMeans

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
    df["cat_kr"] = df["category"].map(CAT_KR).fillna(df["category"])

    pivot = df.groupby(["month", "cat_kr"])["total_price"].sum().unstack(fill_value=0)
    monthly_total = df.groupby("month")["total_price"].sum().reset_index(name="revenue")

    if len(monthly_total) >= 2:
        last_m = monthly_total["month"].max()
        prev_m = monthly_total.iloc[-2]["month"]
        last_df = df[df["month"] == last_m].groupby("cat_kr")["total_price"].sum()
        prev_df = df[df["month"] == prev_m].groupby("cat_kr")["total_price"].sum()
        growth = ((last_df - prev_df) / (prev_df + 1) * 100).sort_values(ascending=False)
    else:
        growth = pd.Series(dtype=float)

    return pivot, growth


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
    fig = _base_layout(fig, "전월 대비 카테고리 매출 성장률 (%)")
    fig.update_layout(coloraxis_showscale=False, xaxis_title="카테고리", yaxis_title="성장률(%)")
    return fig


# ════════════════════════════════════════════════════════════════
#  📅 달력 데이터 (주문일 + 재고만료일)
# ════════════════════════════════════════════════════════════════
def calendar_data(sid: int, year: int, month: int) -> list:
    """해당 월의 달력 셀 목록(42셀 = 6주×7일) 반환.
    각 셀: [day_str, order_count_str, type_str]
    type_str: 'today' | 'expiry' | 'order' | 'normal' | 'empty'
    """
    import calendar as cal_lib
    from datetime import date as _date

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
            SELECT DAY(pl.expire_at) AS d
            FROM product_lots pl JOIN products p ON pl.product_id=p.product_id
            WHERE p.seller_id={sid}
              AND YEAR(pl.expire_at)={year} AND MONTH(pl.expire_at)={month}
              AND pl.stock_qty > 0
        """)
        expiry_set = set(int(r.d) for r in lot_df.itertuples()) if not lot_df.empty else set()
    except Exception:
        expiry_set = set()

    today = _date.today()
    cells = []
    for i in range(42):
        day_num = i - start_offset + 1
        if 1 <= day_num <= total_days:
            is_today = (year == today.year and month == today.month and day_num == today.day)
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
    """오늘 주문 건수, 이번 주 만료 예정 재고 건수."""
    from datetime import date as _date, timedelta
    today = _date.today()
    week_end = today + timedelta(days=7)
    try:
        ord_today = q(f"""
            SELECT COUNT(*) cnt FROM orders o
            JOIN products p ON o.product_id=p.product_id
            WHERE p.seller_id={sid} AND DATE(o.order_date)='{today}'
        """).iloc[0, 0]
    except Exception:
        ord_today = 0
    try:
        exp_week = q(f"""
            SELECT COUNT(*) cnt FROM product_lots pl
            JOIN products p ON pl.product_id=p.product_id
            WHERE p.seller_id={sid} AND pl.stock_qty>0
              AND pl.expire_at BETWEEN '{today}' AND '{week_end}'
        """).iloc[0, 0]
    except Exception:
        exp_week = 0
    return {"today_orders": int(ord_today), "expiry_week": int(exp_week)}


def weekly_orders_data(sid: int) -> list:
    """이번 주(월~일) 7일의 주문 이벤트 카드 목록 반환.
    반환: list[dict] 길이=7, 각 dict:
      {weekday: str, date_str: str, is_today: bool,
       orders: list[{product: str, buyer: str, amount_str: str, status: str}]}
    """
    from datetime import date as _date, timedelta

    today = _date.today()
    # 이번 주 월요일
    mon = today - timedelta(days=today.weekday())
    days = [mon + timedelta(days=i) for i in range(7)]
    dow_kr = ["월", "화", "수", "목", "금", "토", "일"]

    d0_str = str(days[0])
    d1_str = str(days[6])

    try:
        df = q(f"""
            SELECT
                DATE(o.order_date) AS od,
                p.product_name,
                o.buyer_id,
                o.total_price,
                o.status
            FROM orders o
            JOIN products p ON o.product_id = p.product_id
            WHERE p.seller_id = {sid}
              AND DATE(o.order_date) BETWEEN '{d0_str}' AND '{d1_str}'
            ORDER BY o.order_date
        """)
    except Exception:
        df = pd.DataFrame()

    result = []
    for i, d in enumerate(days):
        if df.empty:
            day_orders = []
        else:
            rows = df[df["od"] == d]
            day_orders = []
            for _, row in rows.iterrows():
                status = str(row.get("status", ""))
                status_label = {
                    "pending": "접수", "processing": "처리중",
                    "shipped": "배송중", "delivered": "완료",
                    "cancelled": "취소",
                }.get(status, status or "접수")
                day_orders.append({
                    "product": str(row["product_name"])[:10],
                    "buyer": f"고객{str(row['buyer_id'])[-3:]}",
                    "amount_str": won(float(row["total_price"])),
                    "status": status_label,
                })
        result.append({
            "weekday": dow_kr[i],
            "date_str": f"{d.month}/{d.day}",
            "is_today": (d == today),
            "orders": day_orders,
        })
    return result
