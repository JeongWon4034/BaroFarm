"""
BaroFarm Reflex State
=====================
URL 쿼리파라미터 ?seller_id=X 를 읽어 해당 농장의 KPI·ML 예측을 계산하고
plotly Figure / 표 데이터를 State 변수로 보관한다. (UI 는 barofarm.py)
"""
from datetime import date as _date
import reflex as rx
import plotly.graph_objects as go

from . import data


class DashState(rx.State):
    # ── 농장 컨텍스트 ──
    seller_id: int = 0
    seller_name: str = ""
    period: str = ""
    loaded: bool = False
    error: str = ""

    # ── KPI ──
    kpi_gmv: str = "-"
    kpi_orders: str = "-"
    kpi_aov: str = "-"
    kpi_buyers: str = "-"
    kpi_repurchase: str = "-"
    kpi_deal: str = "-"
    kpi_deal_share: str = "-"

    # ── 오늘 요약 ──
    today_orders: str = "0"
    expiry_week: str = "0"
    today_label: str = ""

    # ── 1. 매출 예측 ──
    has_revenue: bool = False
    revenue_fig: go.Figure = go.Figure()
    fc_total: str = "-"
    fc_daily: str = "-"
    fc_r2: str = "-"

    # ── 2. 매입 추천 ──
    has_reco: bool = False
    reco_fig: go.Figure = go.Figure()
    reco_table: list[list[str]] = []

    # ── 3. 수요 예측 ──
    has_demand: bool = False
    demand_fig: go.Figure = go.Figure()
    demand_table: list[list[str]] = []

    # ── 4. 고객 세그먼트 ──
    has_segment: bool = False
    segment_fig: go.Figure = go.Figure()
    segment_table: list[list[str]] = []

    # ── 5. 계절성 ──
    has_season: bool = False
    season_heat_fig: go.Figure = go.Figure()
    season_growth_fig: go.Figure = go.Figure()
    season_up: str = ""
    season_down: str = ""

    # ── 6. 공급망·수요 최적화 ──
    has_supply: bool = False
    supply_fig: go.Figure = go.Figure()
    supply_table: list[list[str]] = []
    sup_shortage: str = "0"
    sup_expiry: str = "0"
    sup_waste_won: str = "0원"
    sup_reorder: str = "0"

    # ── 📅 달력 (월간) ──
    cal_year: int = 0
    cal_month: int = 0
    cal_month_label: str = ""
    cal_key: str = ""                # 현재 보고있는 월 "Y-M"
    cal_grid: list[list[str]] = []   # 42셀: [day_str, count_str, type_str]

    # ── 📅 주간 뷰 ── 7일 × 주문 카드
    # weekly_days[i] = [weekday_kr, date_str, is_today_str, order_count_str, iso, revenue_str]
    weekly_days: list[list[str]] = []
    # weekly_orders[i][j] = [product, buyer, amount_str, status]
    weekly_orders: list[list[list[str]]] = []

    # ── 선택한 날짜 상세 (당일 매출) ──
    sel_date: str = ""               # "YYYY-MM-DD"
    sel_date_label: str = "날짜를 선택하세요"
    sel_revenue: str = "-"
    sel_orders: str = "0"
    sel_items: str = "0"
    sel_top: str = "-"
    sel_cal_key: str = ""            # 선택 날짜가 속한 월 "Y-M"
    sel_cal_day: str = ""            # 선택 날짜의 일(day) 문자열

    # ── nav active tab ──
    active_nav: str = "dashboard"

    def set_nav(self, tab: str):
        self.active_nav = tab

    def _resolve_seller(self) -> int:
        sid = None
        try:
            sid = self.router.page.params.get("seller_id")
        except Exception:
            sid = None
        if sid:
            try:
                return int(sid)
            except (TypeError, ValueError):
                pass
        sellers = data.list_sellers()
        return int(sellers.iloc[0]["user_id"]) if not sellers.empty else 0

    def load(self):
        self.loaded = False
        self.error = ""
        try:
            sid = self._resolve_seller()
            if not sid:
                self.error = "주문 데이터가 있는 판매자가 없습니다."
                self.loaded = True
                return

            d0, d1 = data.seller_date_range(sid)
            if not d0:
                self.error = "선택한 농장에 주문이 없습니다."
                self.loaded = True
                return

            sellers = data.list_sellers().set_index("user_id")
            self.seller_id = sid
            self.seller_name = str(sellers.loc[sid, "name"]) if sid in sellers.index else f"농장 {sid}"
            self.period = f"{d0} ~ {d1}"

            o = data.load_orders(sid, d0, d1)
            k = data.farm_kpis(o)
            self.kpi_gmv = k["gmv"]
            self.kpi_orders = k["orders"]
            self.kpi_aov = k["aov"]
            self.kpi_buyers = k["buyers"]
            self.kpi_repurchase = k["repurchase"]
            self.kpi_deal = k["deal_rev"]
            self.kpi_deal_share = k["deal_share"]

            # 기준일 = 가장 최근 주문일(데모 데이터가 과거일 수 있어서)
            ref = data.latest_order_date(sid)

            # 오늘 요약(최근 영업일 기준)
            td = data.today_delivery_summary(sid)
            self.today_orders = str(td["today_orders"])
            self.expiry_week = str(td["expiry_week"])
            self.today_label = f"{ref.year}.{ref.month:02d}.{ref.day:02d}"

            # 달력 (기준 월 + 주간 뷰), 기본 선택일 = 기준일
            self._load_calendar(sid, ref.year, ref.month, ref)
            self._load_weekly(sid, ref)
            self.select_date(str(ref))

            self._compute_ml(sid, d0, d1)
            self.loaded = True
        except Exception as e:  # noqa: BLE001
            self.error = f"데이터 로드 중 오류: {e}"
            self.loaded = True

    def _load_calendar(self, sid: int, year: int, month: int, ref=None):
        self.cal_year = year
        self.cal_month = month
        self.cal_month_label = f"{year}년 {month}월"
        self.cal_key = f"{year}-{month}"
        self.cal_grid = data.calendar_data(sid, year, month, ref)

    def _load_weekly(self, sid: int, ref=None):
        week_data = data.weekly_orders_data(sid, ref)
        days_flat = []
        orders_flat = []
        for d in week_data:
            days_flat.append([
                d["weekday"], d["date_str"],
                "true" if d["is_today"] else "false",
                str(len(d["orders"])),
                d["iso"], d["revenue_str"],
            ])
            orders_flat.append([[o["product"], o["buyer"], o["amount_str"], o["status"]]
                                 for o in d["orders"]])
        self.weekly_days = days_flat
        self.weekly_orders = orders_flat

    def select_date(self, date_str: str):
        """달력 날짜 클릭 → 당일 매출 상세 로드."""
        if not date_str:
            return
        self.sel_date = date_str
        try:
            y, m, d = (int(x) for x in date_str.split("-"))
            dow = ["월", "화", "수", "목", "금", "토", "일"][_date(y, m, d).weekday()]
            self.sel_date_label = f"{m}월 {d}일 ({dow})"
            self.sel_cal_key = f"{y}-{m}"
            self.sel_cal_day = str(d)
        except Exception:
            self.sel_date_label = date_str
            self.sel_cal_key = ""
            self.sel_cal_day = ""
        detail = data.daily_detail(self.seller_id, date_str)
        self.sel_revenue = detail["revenue"]
        self.sel_orders = detail["orders"]
        self.sel_items = detail["items"]
        self.sel_top = detail["top"]

    def select_cal_day(self, day_str: str):
        """월간 달력 셀 클릭 → 현재 보는 월 + 일 → select_date."""
        if not day_str:
            return
        self.select_date(f"{self.cal_year}-{self.cal_month:02d}-{int(day_str):02d}")

    def prev_month(self):
        m, y = self.cal_month - 1, self.cal_year
        if m < 1:
            m, y = 12, y - 1
        self._load_calendar(self.seller_id, y, m)

    def next_month(self):
        m, y = self.cal_month + 1, self.cal_year
        if m > 12:
            m, y = 1, y + 1
        self._load_calendar(self.seller_id, y, m)

    def _compute_ml(self, sid, d0, d1):
        import numpy as np

        # 1. 매출 예측
        res = data.ai_revenue_forecast(sid, d0, d1)
        if res:
            preds = np.array(res["preds"])
            self.revenue_fig = data.fig_revenue(res, self.seller_name)
            self.fc_total = data.won(preds.sum())
            self.fc_daily = data.won(preds.mean())
            self.fc_r2 = f"{res['score']:.3f}"
            self.has_revenue = True
        else:
            self.has_revenue = False

        # 2. 매입 추천
        reco = data.ai_purchase_reco(sid, d0, d1)
        if reco is not None:
            self.reco_fig = data.fig_reco(reco)
            self.reco_table = reco[[
                "product_name", "카테고리", "추천점수", "트렌드", "이유",
            ]].astype(str).values.tolist()
            self.has_reco = True
        else:
            self.has_reco = False

        # 3. 수요 예측
        dem = data.ai_demand_forecast(sid, d0, d1)
        if dem is not None and not dem.empty:
            dem = dem.copy()
            dem["카테고리"] = dem["category"].map(data.CAT_KR).fillna(dem["category"])
            dem["현재 주간수요"] = dem["avg_qty"].round(1)
            dem["예측 주간수요"] = dem["forecast_avg"].round(1)
            dem["트렌드"] = dem["trend_pct"].apply(
                lambda t: f"📈 +{t:.1f}%" if t > 3 else (f"📉 {t:.1f}%" if t < -3 else f"➡️ {t:.1f}%"))
            self.demand_fig = data.fig_demand(dem)
            self.demand_table = dem[[
                "product_name", "카테고리", "현재 주간수요", "예측 주간수요", "트렌드",
            ]].astype(str).values.tolist()
            self.has_demand = True
        else:
            self.has_demand = False

        # 4. 고객 세그먼트
        rfm = data.ai_customer_segments(sid, d0, d1)
        if rfm is not None:
            self.segment_fig = data.fig_segments(rfm)
            summary = rfm.groupby("segment").agg(
                고객수=("buyer_id", "count"),
                평균구매횟수=("frequency", "mean"),
                평균매출=("monetary", "mean"),
            ).reset_index().sort_values("평균매출", ascending=False)
            summary["평균구매횟수"] = summary["평균구매횟수"].round(1)
            summary["평균매출"] = summary["평균매출"].round(0).apply(data.won)
            summary["고객수"] = summary["고객수"].apply(lambda n: f"{int(n)}명")
            self.segment_table = summary[[
                "segment", "고객수", "평균구매횟수", "평균매출",
            ]].astype(str).values.tolist()
            self.has_segment = True
        else:
            self.has_segment = False

        # 5. 계절성
        pivot, growth = data.ai_seasonality(sid, d0, d1)
        if pivot is not None and not pivot.empty:
            self.season_heat_fig = data.fig_season_heat(pivot)
            if growth is not None and not growth.empty:
                self.season_growth_fig = data.fig_season_growth(growth)
                up = growth[growth > 5].index.tolist()
                down = growth[growth < -5].index.tolist()
                self.season_up = ", ".join(up)
                self.season_down = ", ".join(down)
            self.has_season = True
        else:
            self.has_season = False

        # 6. 공급망·수요 최적화
        sup = data.supply_demand_optimization(sid)
        if sup is not None and not sup.empty:
            self.supply_fig = data.fig_supply(sup)
            t = sup.copy()
            t["현재고"] = t["stock"].apply(lambda v: f"{int(v)}개")
            t["일수요"] = t["daily_demand"].apply(lambda v: f"{v:.1f}개")
            t["소진일수"] = t["days_supply"].apply(
                lambda v: "60일+" if v >= 60 else f"{v:.0f}일")
            t["최단만료"] = t["days_to_expiry"].apply(
                lambda v: "—" if v >= 999 else f"D-{int(v)}")
            self.supply_table = t[[
                "product_name", "category_kr", "현재고", "일수요",
                "소진일수", "최단만료", "status", "action",
            ]].astype(str).values.tolist()
            s = data.supply_summary(sid)
            self.sup_shortage = str(s["shortage"])
            self.sup_expiry = str(s["expiry"])
            self.sup_waste_won = s["waste_won"]
            self.sup_reorder = str(s["reorder"])
            self.has_supply = True
        else:
            self.has_supply = False
