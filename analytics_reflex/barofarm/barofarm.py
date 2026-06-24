"""
BaroFarm 농장 분석 대시보드 (Reflex)
====================================
Streamlit 대시보드(dashboard.py)의 농장 + AI 예측 화면을 Reflex 로 이식.
프론트(Vue)에서 iframe(?seller_id=X)으로 임베드한다. 데이터/ML 은 data.py, 상태는 state.py.
"""
import reflex as rx

from .state import DashState

GREEN = "#2D6A4F"
GREEN_L = "#52B788"
PAPER = "#ffffff"


# ── 작은 헬퍼 ─────────────────────────────────────────────────────
def kpi_card(label: str, value, sub: str = "", accent: bool = False) -> rx.Component:
    return rx.box(
        rx.text(label, font_size="0.8rem", color="#667085"),
        rx.text(value, font_size="1.5rem", font_weight="800",
                color=rx.cond(accent, GREEN, "#1a1a1a")),
        rx.cond(sub != "", rx.text(sub, font_size="0.72rem", color="#98a2b3"), rx.fragment()),
        bg=PAPER, border="1px solid #e7eae6", border_top=f"3px solid {GREEN_L}",
        border_radius="12px", padding="14px 18px",
        display="flex", flex_direction="column", gap="2px", flex="1",
        box_shadow="0 2px 8px rgba(0,0,0,0.03)",
    )


def info_box(msg: str) -> rx.Component:
    return rx.box(
        rx.text(msg, color="#667085"),
        bg="#f6f8f5", border="1px solid #e7eae6", border_radius="12px",
        padding="40px", text_align="center", width="100%",
    )


def chart(fig) -> rx.Component:
    return rx.box(rx.plotly(data=fig, width="100%", height="430px"),
                  width="100%", bg=PAPER, border_radius="12px", padding="6px")


def str_table(headers: list[str], rows) -> rx.Component:
    return rx.table.root(
        rx.table.header(
            rx.table.row(*[rx.table.column_header_cell(h) for h in headers])
        ),
        rx.table.body(
            rx.foreach(rows, lambda row: rx.table.row(
                rx.foreach(row, lambda cell: rx.table.cell(cell))
            ))
        ),
        variant="surface", size="1", width="100%",
    )


def section_caption(text: str) -> rx.Component:
    return rx.text(text, font_size="0.82rem", color="#667085", margin_bottom="10px")


# ── 탭별 콘텐츠 ───────────────────────────────────────────────────
def tab_revenue() -> rx.Component:
    return rx.cond(
        DashState.has_revenue,
        rx.vstack(
            rx.hstack(
                kpi_card("예측 30일 총매출", DashState.fc_total, accent=True),
                kpi_card("예측 일평균 매출", DashState.fc_daily),
                kpi_card("모델 설명력 (R²)", DashState.fc_r2),
                width="100%", spacing="3",
            ),
            chart(DashState.revenue_fig),
            section_caption("주간(7일)·월간(30일) 계절성 sin/cos 피처를 쓴 Ridge Regression. "
                            "주황 점선이 향후 30일 예측, 음영이 ±1σ 불확실성 구간입니다."),
            width="100%", spacing="3", align="stretch",
        ),
        info_box("예측에 필요한 데이터가 부족합니다. (최소 2주 이상의 주문 이력 필요)"),
    )


def tab_reco() -> rx.Component:
    return rx.cond(
        DashState.has_reco,
        rx.vstack(
            rx.heading("🛒 AI 매입 추천 — Top 10 상품", size="4"),
            section_caption("판매속도(30%)·최근 트렌드(35%)·매출비중(20%)·재구매율(15%)을 "
                            "MinMaxScaler 정규화 후 가중합한 종합 추천 점수입니다."),
            chart(DashState.reco_fig),
            str_table(["상품명", "카테고리", "추천점수", "트렌드", "추천 이유"], DashState.reco_table),
            width="100%", spacing="3", align="stretch",
        ),
        info_box("스코어 계산에 필요한 주문 데이터가 부족합니다."),
    )


def tab_demand() -> rx.Component:
    return rx.cond(
        DashState.has_demand,
        rx.vstack(
            rx.heading("🔮 상위 8개 상품 — 향후 4주 수요 예측", size="4"),
            section_caption("주간 판매량의 선형회귀(LinearRegression)로 다음 4주 평균 수요를 예측합니다."),
            chart(DashState.demand_fig),
            str_table(["상품명", "카테고리", "현재 주간수요", "예측 주간수요", "트렌드"], DashState.demand_table),
            width="100%", spacing="3", align="stretch",
        ),
        info_box("수요 예측에 필요한 데이터가 부족합니다. (상품당 최소 4주 이상)"),
    )


def tab_segment() -> rx.Component:
    return rx.cond(
        DashState.has_segment,
        rx.vstack(
            rx.heading("👥 RFM 기반 고객 세그멘테이션 (KMeans k=4)", size="4"),
            section_caption("Recency·Frequency·Monetary 를 StandardScaler 정규화 후 KMeans(k=4)로 군집화합니다."),
            chart(DashState.segment_fig),
            str_table(["세그먼트", "고객수", "평균구매횟수", "평균매출"], DashState.segment_table),
            width="100%", spacing="3", align="stretch",
        ),
        info_box("세그멘테이션에 필요한 고객 수가 부족합니다. (최소 8명 이상)"),
    )


def tab_season() -> rx.Component:
    return rx.cond(
        DashState.has_season,
        rx.vstack(
            rx.heading("📅 카테고리 × 월별 매출 히트맵", size="4"),
            section_caption("어떤 달에 어떤 카테고리가 잘 팔렸는지 확인하고 다음 달 매입 계획을 세우세요."),
            chart(DashState.season_heat_fig),
            chart(DashState.season_growth_fig),
            rx.cond(DashState.season_up != "",
                    rx.callout(f"📈 매입 확대 추천: {DashState.season_up} — 전월 대비 성장 중",
                               color_scheme="green", width="100%"),
                    rx.fragment()),
            rx.cond(DashState.season_down != "",
                    rx.callout(f"📉 매입 축소 검토: {DashState.season_down} — 전월 대비 하락 중",
                               color_scheme="orange", width="100%"),
                    rx.fragment()),
            width="100%", spacing="3", align="stretch",
        ),
        info_box("계절성 분석에 필요한 데이터가 부족합니다."),
    )


# ── 메인 대시보드 ─────────────────────────────────────────────────
def dashboard() -> rx.Component:
    return rx.vstack(
        # 헤더
        rx.hstack(
            rx.heading(rx.text("🏡 ", DashState.seller_name, " 애널리틱스"), size="6"),
            rx.spacer(),
            rx.badge("Reflex · ML", color_scheme="green", size="2"),
            width="100%", align="center",
        ),
        rx.text(DashState.period, " · 단일 판매자 셀러 대시보드", color="#98a2b3", font_size="0.85rem"),

        # KPI 2줄
        rx.hstack(
            kpi_card("총 매출 (GMV)", DashState.kpi_gmv, accent=True),
            kpi_card("주문 수", DashState.kpi_orders),
            kpi_card("객단가 (AOV)", DashState.kpi_aov),
            kpi_card("구매 고객", DashState.kpi_buyers),
            width="100%", spacing="3", margin_top="6px",
        ),
        rx.hstack(
            kpi_card("재구매율", DashState.kpi_repurchase),
            kpi_card("할인 회수 매출", DashState.kpi_deal, DashState.kpi_deal_share, accent=True),
            width="100%", spacing="3",
        ),

        rx.divider(margin_y="10px"),
        rx.heading("🤖 AI 예측 & 매입 추천", size="6"),
        rx.text("scikit-learn Ridge · LinearRegression · KMeans 모델로 실제 주문 데이터를 학습했습니다.",
                color="#667085", font_size="0.85rem"),

        # 탭
        rx.tabs.root(
            rx.tabs.list(
                rx.tabs.trigger("📈 매출 예측", value="rev"),
                rx.tabs.trigger("🛒 매입 추천", value="reco"),
                rx.tabs.trigger("🔮 수요 예측", value="dem"),
                rx.tabs.trigger("👥 고객 세그먼트", value="seg"),
                rx.tabs.trigger("📅 계절성", value="season"),
            ),
            rx.tabs.content(tab_revenue(), value="rev", padding_top="16px"),
            rx.tabs.content(tab_reco(), value="reco", padding_top="16px"),
            rx.tabs.content(tab_demand(), value="dem", padding_top="16px"),
            rx.tabs.content(tab_segment(), value="seg", padding_top="16px"),
            rx.tabs.content(tab_season(), value="season", padding_top="16px"),
            default_value="rev", width="100%",
        ),
        width="100%", max_width="1100px", spacing="3", align="stretch",
        padding="24px", margin="0 auto",
    )


def index() -> rx.Component:
    return rx.box(
        rx.cond(
            DashState.loaded,
            rx.cond(
                DashState.error != "",
                info_box(DashState.error),
                dashboard(),
            ),
            rx.center(
                rx.vstack(
                    rx.spinner(size="3"),
                    rx.text("농장 데이터를 불러오는 중…", color="#667085"),
                    spacing="3", align="center",
                ),
                height="80vh",
            ),
        ),
        bg="#fbfdfb", min_height="100vh", width="100%",
        font_family="Pretendard, sans-serif",
    )


app = rx.App(
    theme=rx.theme(appearance="light", accent_color="green", radius="large"),
    stylesheets=["https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css"],
)
app.add_page(index, route="/", title="BaroFarm 농장 대시보드", on_load=DashState.load)
