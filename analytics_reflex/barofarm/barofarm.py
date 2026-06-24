"""
BaroFarm 농장 분석 대시보드 (Reflex)
====================================
다크 사이드바 + 달력(주문일·만료일 표시) + KPI + AI 예측 5탭
"""
import reflex as rx
from .state import DashState

# ── 디자인 토큰 ──────────────────────────────────────────────────
SIDEBAR_BG   = "#111827"
SIDEBAR_W    = "220px"
ACCENT       = "#1B5E3F"
ACCENT_L     = "#40916C"
ACCENT_GRAD  = "linear-gradient(135deg, #1B5E3F 0%, #40916C 100%)"
BG           = "#F1F5F9"
CARD         = "#ffffff"
BORDER       = "#E2E8F0"
TEXT_PRI     = "#111827"
TEXT_SEC     = "#64748B"
ORANGE       = "#F59E0B"


# ════════════════════════════════════════════════════════════════
#  사이드바
# ════════════════════════════════════════════════════════════════
def nav_item(icon: str, label: str, key: str) -> rx.Component:
    active = DashState.active_nav == key
    return rx.box(
        rx.hstack(
            rx.text(icon, font_size="1.1rem"),
            rx.text(label, font_size="0.875rem", font_weight="500"),
            spacing="2", align="center",
        ),
        on_click=DashState.set_nav(key),
        padding="10px 16px",
        border_radius="10px",
        cursor="pointer",
        bg=rx.cond(active, "rgba(64,145,108,0.2)", "transparent"),
        color=rx.cond(active, "#74C69D", "rgba(255,255,255,0.65)"),
        border_left=rx.cond(active, f"3px solid {ACCENT_L}", "3px solid transparent"),
        transition="all .15s ease",
        _hover={"bg": "rgba(255,255,255,0.08)", "color": "white"},
        width="100%",
    )


def sidebar() -> rx.Component:
    return rx.box(
        rx.vstack(
            # 로고
            rx.box(
                rx.hstack(
                    rx.text("🌱", font_size="1.4rem"),
                    rx.vstack(
                        rx.text("BaroFarm", font_size="1rem", font_weight="800",
                                color="white", letter_spacing="-0.02em"),
                        rx.text("농장 애널리틱스", font_size="0.65rem",
                                color="rgba(255,255,255,0.45)", letter_spacing="0.05em"),
                        spacing="0", align="start",
                    ),
                    spacing="2", align="center",
                ),
                padding="20px 16px 16px",
            ),
            rx.divider(border_color="rgba(255,255,255,0.08)", margin_y="2px"),

            # 농장 배지
            rx.box(
                rx.vstack(
                    rx.text("현재 농장", font_size="0.65rem",
                            color="rgba(255,255,255,0.35)", letter_spacing="0.08em"),
                    rx.text(DashState.seller_name, font_size="0.82rem",
                            font_weight="600", color="white"),
                    spacing="0", align="start",
                ),
                bg="rgba(255,255,255,0.05)", border_radius="10px",
                padding="10px 14px", margin="8px 12px",
                border="1px solid rgba(255,255,255,0.07)",
            ),

            # 네비게이션
            rx.vstack(
                nav_item("🏠", "대시보드",   "dashboard"),
                nav_item("📈", "매출 분석",  "revenue"),
                nav_item("🛒", "매입 추천 AI","reco"),
                nav_item("📅", "일정 · 달력", "calendar"),
                nav_item("🚚", "배송 현황",  "delivery"),
                nav_item("👥", "고객 분석",  "segment"),
                spacing="1", width="100%", padding_x="8px",
            ),

            rx.spacer(),

            # 하단 요약
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.text("📦", font_size="0.9rem"),
                        rx.vstack(
                            rx.text("오늘 주문", font_size="0.65rem",
                                    color="rgba(255,255,255,0.4)"),
                            rx.text(DashState.today_orders, font_size="0.95rem",
                                    font_weight="700", color="white"),
                            spacing="0",
                        ),
                        rx.spacer(),
                        rx.hstack(
                            rx.text("⚠️", font_size="0.9rem"),
                            rx.vstack(
                                rx.text("7일내 만료", font_size="0.65rem",
                                        color="rgba(255,255,255,0.4)"),
                                rx.text(DashState.expiry_week, font_size="0.95rem",
                                        font_weight="700", color=ORANGE),
                                spacing="0",
                            ),
                            spacing="1",
                        ),
                        width="100%", align="start",
                    ),
                    spacing="1",
                ),
                bg="rgba(255,255,255,0.04)", border_radius="10px",
                padding="12px", margin="8px 12px 16px",
                border="1px solid rgba(255,255,255,0.07)",
            ),
        ),
        width=SIDEBAR_W,
        min_height="100vh",
        bg=SIDEBAR_BG,
        display="flex",
        flex_direction="column",
        flex_shrink="0",
        position="sticky",
        top="0",
        height="100vh",
        overflow_y="auto",
    )


# ════════════════════════════════════════════════════════════════
#  공통 컴포넌트
# ════════════════════════════════════════════════════════════════
def kpi_card(icon: str, label: str, value, sub: str = "",
             accent: bool = False, warn: bool = False) -> rx.Component:
    col = ACCENT if accent else (ORANGE if warn else TEXT_PRI)
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.box(rx.text(icon, font_size="1.1rem"),
                       bg=rx.cond(accent, "rgba(27,94,63,0.1)",
                                  rx.cond(warn, "rgba(245,158,11,0.1)", "#F1F5F9")),
                       border_radius="8px", padding="6px", width="34px", height="34px",
                       display="flex", align_items="center", justify_content="center"),
                rx.spacer(),
            ),
            rx.text(value, font_size="1.55rem", font_weight="800",
                    color=col, line_height="1.1"),
            rx.text(label, font_size="0.75rem", color=TEXT_SEC, font_weight="500"),
            rx.cond(sub != "",
                    rx.text(sub, font_size="0.7rem", color="#94A3B8"),
                    rx.fragment()),
            spacing="1", align="start",
        ),
        bg=CARD, border="1px solid " + BORDER, border_radius="14px",
        padding="16px", flex="1",
        box_shadow="0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.04)",
        transition="transform .18s, box-shadow .18s",
        _hover={"transform": "translateY(-2px)",
                "box_shadow": "0 6px 20px rgba(27,94,63,0.1)"},
    )


def section_heading(text: str, caption: str = "") -> rx.Component:
    return rx.vstack(
        rx.text(text, font_size="1rem", font_weight="700", color=TEXT_PRI),
        rx.cond(caption != "",
                rx.text(caption, font_size="0.78rem", color=TEXT_SEC),
                rx.fragment()),
        spacing="0", margin_bottom="12px",
    )


def chart_card(fig, title: str = "", caption: str = "") -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.cond(title != "", section_heading(title, caption), rx.fragment()),
            rx.plotly(data=fig, width="100%", height="380px"),
            spacing="0",
        ),
        bg=CARD, border="1px solid " + BORDER, border_radius="16px",
        padding="20px", width="100%",
        box_shadow="0 1px 3px rgba(0,0,0,0.04)",
    )


def info_box(msg: str) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.text("📭", font_size="2rem"),
            rx.text(msg, color=TEXT_SEC, font_size="0.88rem"),
            spacing="2", align="center",
        ),
        bg="#F8FAFC", border="1px dashed " + BORDER, border_radius="14px",
        padding="40px", text_align="center", width="100%",
    )


def str_table(headers: list[str], rows) -> rx.Component:
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                *[rx.table.column_header_cell(
                    h, color=TEXT_SEC, font_size="0.75rem",
                    font_weight="600", letter_spacing="0.03em",
                ) for h in headers]
            )
        ),
        rx.table.body(
            rx.foreach(rows, lambda row: rx.table.row(
                rx.foreach(row, lambda cell: rx.table.cell(
                    cell, font_size="0.82rem", color=TEXT_PRI,
                ))
            ))
        ),
        variant="surface", size="1", width="100%",
    )


# ════════════════════════════════════════════════════════════════
#  📅 달력 컴포넌트
# ════════════════════════════════════════════════════════════════
DOW = ["일", "월", "화", "수", "목", "금", "토"]


def cal_cell(cell) -> rx.Component:
    day   = cell[0]
    cnt   = cell[1]
    ctype = cell[2]

    is_today  = ctype == "today"
    is_expiry = ctype == "expiry"
    is_order  = ctype == "order"
    is_empty  = ctype == "empty"

    return rx.box(
        rx.cond(
            day != "",
            rx.vstack(
                rx.text(
                    day,
                    font_size="0.8rem",
                    font_weight=rx.cond(is_today, "700", "400"),
                    color=rx.cond(is_today, "white",
                           rx.cond(is_expiry, "#92400E", TEXT_PRI)),
                    line_height="1",
                ),
                rx.cond(
                    ~is_empty & (cnt != "0"),
                    rx.box(
                        width="5px", height="5px", border_radius="50%",
                        bg=rx.cond(is_expiry, ORANGE, ACCENT_L),
                        margin_top="2px",
                    ),
                    rx.box(width="5px", height="5px", margin_top="2px"),
                ),
                spacing="0", align="center",
            ),
            rx.fragment(),
        ),
        width="32px", height="32px",
        border_radius="8px",
        display="flex", align_items="center", justify_content="center",
        bg=rx.cond(is_today, ACCENT,
           rx.cond(is_expiry, "#FEF3C7",
           rx.cond(is_order, "rgba(64,145,108,0.08)", "transparent"))),
        border=rx.cond(is_today, "none",
               rx.cond(is_expiry, f"1px solid {ORANGE}", "none")),
    )


def calendar_widget() -> rx.Component:
    return rx.box(
        rx.vstack(
            # 헤더: 월 이동
            rx.hstack(
                rx.text(DashState.cal_month_label, font_size="0.9rem",
                        font_weight="700", color=TEXT_PRI),
                rx.spacer(),
                rx.hstack(
                    rx.box(
                        rx.text("‹", font_size="1rem", color=TEXT_SEC),
                        on_click=DashState.prev_month,
                        cursor="pointer", padding="2px 8px",
                        border_radius="6px", border=f"1px solid {BORDER}",
                        _hover={"bg": "#F1F5F9"},
                    ),
                    rx.box(
                        rx.text("›", font_size="1rem", color=TEXT_SEC),
                        on_click=DashState.next_month,
                        cursor="pointer", padding="2px 8px",
                        border_radius="6px", border=f"1px solid {BORDER}",
                        _hover={"bg": "#F1F5F9"},
                    ),
                    spacing="1",
                ),
                width="100%", align="center",
            ),

            # 요일 헤더
            rx.box(
                *[rx.box(
                    rx.text(d, font_size="0.7rem", font_weight="600",
                            color=TEXT_SEC, text_align="center"),
                    width="32px", text_align="center",
                ) for d in DOW],
                display="grid",
                grid_template_columns="repeat(7, 32px)",
                gap="2px", margin_bottom="2px",
            ),

            # 날짜 그리드
            rx.box(
                rx.foreach(DashState.cal_grid, cal_cell),
                display="grid",
                grid_template_columns="repeat(7, 32px)",
                gap="2px",
            ),

            # 범례
            rx.hstack(
                rx.hstack(
                    rx.box(width="8px", height="8px", border_radius="50%",
                           bg=ACCENT_L),
                    rx.text("주문일", font_size="0.68rem", color=TEXT_SEC),
                    spacing="1", align="center",
                ),
                rx.hstack(
                    rx.box(width="8px", height="8px", border_radius="50%",
                           bg=ORANGE),
                    rx.text("만료예정", font_size="0.68rem", color=TEXT_SEC),
                    spacing="1", align="center",
                ),
                spacing="3", margin_top="6px",
            ),
            spacing="2", align="start",
        ),
        bg=CARD, border=f"1px solid {BORDER}", border_radius="16px",
        padding="18px", width="100%",
        box_shadow="0 1px 3px rgba(0,0,0,0.04)",
    )


# ════════════════════════════════════════════════════════════════
#  AI 탭 콘텐츠
# ════════════════════════════════════════════════════════════════
def tab_revenue() -> rx.Component:
    return rx.cond(
        DashState.has_revenue,
        rx.vstack(
            rx.hstack(
                kpi_card("📈", "예측 30일 총매출", DashState.fc_total, accent=True),
                kpi_card("📊", "예측 일평균 매출", DashState.fc_daily),
                kpi_card("🎯", "모델 설명력 (R²)",  DashState.fc_r2),
                width="100%", spacing="3",
            ),
            chart_card(
                DashState.revenue_fig,
                caption="Ridge Regression · 주간/월간 계절성 sin/cos 피처. 주황 점선=30일 예측, 음영=±1σ",
            ),
            width="100%", spacing="3", align="stretch",
        ),
        info_box("예측에 필요한 데이터가 부족합니다. (최소 2주 이상의 주문 이력 필요)"),
    )


def tab_reco() -> rx.Component:
    return rx.cond(
        DashState.has_reco,
        rx.vstack(
            chart_card(
                DashState.reco_fig,
                "🛒 AI 매입 추천 Top 10",
                "판매속도(30%)·트렌드(35%)·매출비중(20%)·재구매율(15%) MinMaxScaler 가중합",
            ),
            rx.box(
                str_table(["상품명", "카테고리", "추천점수", "트렌드", "추천 이유"],
                          DashState.reco_table),
                bg=CARD, border=f"1px solid {BORDER}", border_radius="14px",
                padding="12px", width="100%",
            ),
            width="100%", spacing="3", align="stretch",
        ),
        info_box("스코어 계산에 필요한 주문 데이터가 부족합니다."),
    )


def tab_demand() -> rx.Component:
    return rx.cond(
        DashState.has_demand,
        rx.vstack(
            chart_card(
                DashState.demand_fig,
                "🔮 상위 8개 상품 — 향후 4주 수요 예측",
                "주간 판매량 LinearRegression 4주 예측",
            ),
            rx.box(
                str_table(["상품명", "카테고리", "현재 주간수요", "예측 주간수요", "트렌드"],
                          DashState.demand_table),
                bg=CARD, border=f"1px solid {BORDER}", border_radius="14px",
                padding="12px", width="100%",
            ),
            width="100%", spacing="3", align="stretch",
        ),
        info_box("수요 예측에 필요한 데이터가 부족합니다. (상품당 최소 4주 이상)"),
    )


def tab_segment() -> rx.Component:
    return rx.cond(
        DashState.has_segment,
        rx.vstack(
            chart_card(
                DashState.segment_fig,
                "👥 RFM 기반 고객 세그멘테이션",
                "Recency·Frequency·Monetary StandardScaler 정규화 후 KMeans(k=4) 군집화",
            ),
            rx.box(
                str_table(["세그먼트", "고객수", "평균구매횟수", "평균매출"],
                          DashState.segment_table),
                bg=CARD, border=f"1px solid {BORDER}", border_radius="14px",
                padding="12px", width="100%",
            ),
            width="100%", spacing="3", align="stretch",
        ),
        info_box("세그멘테이션에 필요한 고객 수가 부족합니다."),
    )


def tab_season() -> rx.Component:
    return rx.cond(
        DashState.has_season,
        rx.vstack(
            chart_card(DashState.season_heat_fig,
                       "📅 카테고리 × 월별 매출 히트맵",
                       "어떤 달에 어떤 카테고리가 잘 팔렸는지 확인하세요."),
            chart_card(DashState.season_growth_fig),
            rx.cond(DashState.season_up != "",
                    rx.box(
                        rx.hstack(
                            rx.text("📈", font_size="1.1rem"),
                            rx.vstack(
                                rx.text("매입 확대 추천", font_size="0.78rem",
                                        font_weight="600", color="#065F46"),
                                rx.text(DashState.season_up, font_size="0.82rem",
                                        color="#047857"),
                                spacing="0",
                            ),
                            spacing="2", align="start",
                        ),
                        bg="#ECFDF5", border="1px solid #6EE7B7", border_radius="12px",
                        padding="14px", width="100%",
                    ),
                    rx.fragment()),
            rx.cond(DashState.season_down != "",
                    rx.box(
                        rx.hstack(
                            rx.text("📉", font_size="1.1rem"),
                            rx.vstack(
                                rx.text("매입 축소 검토", font_size="0.78rem",
                                        font_weight="600", color="#92400E"),
                                rx.text(DashState.season_down, font_size="0.82rem",
                                        color="#B45309"),
                                spacing="0",
                            ),
                            spacing="2", align="start",
                        ),
                        bg="#FFFBEB", border="1px solid #FCD34D", border_radius="12px",
                        padding="14px", width="100%",
                    ),
                    rx.fragment()),
            width="100%", spacing="3", align="stretch",
        ),
        info_box("계절성 분석에 필요한 데이터가 부족합니다."),
    )


# ════════════════════════════════════════════════════════════════
#  메인 콘텐츠
# ════════════════════════════════════════════════════════════════
def main_content() -> rx.Component:
    return rx.box(
        rx.vstack(
            # ── 상단 헤더 바 ─────────────────────────────────────────
            rx.box(
                rx.hstack(
                    rx.vstack(
                        rx.hstack(
                            rx.text("🏡", font_size="1.1rem"),
                            rx.text(DashState.seller_name, font_size="1.1rem",
                                    font_weight="700", color=TEXT_PRI),
                            rx.badge("SELLER", color_scheme="green", size="1",
                                     variant="soft"),
                            spacing="2", align="center",
                        ),
                        rx.text(DashState.period, font_size="0.78rem", color=TEXT_SEC),
                        spacing="0",
                    ),
                    rx.spacer(),
                    rx.vstack(
                        rx.text(DashState.today_label, font_size="0.78rem",
                                color=TEXT_SEC, text_align="right"),
                        rx.badge("Reflex · scikit-learn", color_scheme="green",
                                 size="1", variant="surface"),
                        spacing="1", align="end",
                    ),
                    width="100%", align="center",
                ),
                bg=CARD, border_bottom=f"1px solid {BORDER}",
                padding="16px 28px", width="100%",
                position="sticky", top="0", z_index="10",
            ),

            # ── 콘텐츠 영역 ──────────────────────────────────────────
            rx.box(
                rx.vstack(
                    # KPI 4칸
                    rx.hstack(
                        kpi_card("💰", "총 매출 (GMV)", DashState.kpi_gmv, accent=True),
                        kpi_card("🧾", "주문 수",        DashState.kpi_orders),
                        kpi_card("💳", "객단가 (AOV)",   DashState.kpi_aov),
                        kpi_card("👤", "구매 고객",      DashState.kpi_buyers),
                        width="100%", spacing="3",
                    ),
                    rx.hstack(
                        kpi_card("🔄", "재구매율",      DashState.kpi_repurchase),
                        kpi_card("🏷️", "할인 회수 매출", DashState.kpi_deal,
                                 DashState.kpi_deal_share, accent=True),
                        kpi_card("📦", "오늘 주문",     DashState.today_orders),
                        kpi_card("⚠️", "7일내 만료 재고", DashState.expiry_week, warn=True),
                        width="100%", spacing="3",
                    ),

                    rx.divider(border_color=BORDER, margin_y="4px"),

                    # ── 메인 2단 레이아웃: AI탭 + 달력 ──────────────
                    rx.hstack(
                        # 왼쪽: AI 탭 (65%)
                        rx.box(
                            rx.vstack(
                                rx.hstack(
                                    rx.text("🤖", font_size="1.1rem"),
                                    rx.text("AI 예측 & 매입 추천",
                                            font_size="1rem", font_weight="700",
                                            color=TEXT_PRI),
                                    spacing="2", align="center",
                                    margin_bottom="2px",
                                ),
                                rx.tabs.root(
                                    rx.tabs.list(
                                        rx.tabs.trigger("📈 매출",   value="rev"),
                                        rx.tabs.trigger("🛒 매입추천", value="reco"),
                                        rx.tabs.trigger("🔮 수요",   value="dem"),
                                        rx.tabs.trigger("👥 고객",   value="seg"),
                                        rx.tabs.trigger("📅 계절성", value="season"),
                                        size="1",
                                    ),
                                    rx.tabs.content(tab_revenue(), value="rev",
                                                    padding_top="14px"),
                                    rx.tabs.content(tab_reco(),    value="reco",
                                                    padding_top="14px"),
                                    rx.tabs.content(tab_demand(),  value="dem",
                                                    padding_top="14px"),
                                    rx.tabs.content(tab_segment(), value="seg",
                                                    padding_top="14px"),
                                    rx.tabs.content(tab_season(),  value="season",
                                                    padding_top="14px"),
                                    default_value="rev", width="100%",
                                ),
                                spacing="2", align="stretch",
                            ),
                            flex="1 1 0", min_width="0",
                        ),

                        # 오른쪽: 달력 + 오늘 요약 (35%)
                        rx.vstack(
                            # 달력
                            rx.box(
                                rx.vstack(
                                    rx.hstack(
                                        rx.text("📅", font_size="1rem"),
                                        rx.text("일정 · 배송 현황",
                                                font_size="0.9rem", font_weight="700",
                                                color=TEXT_PRI),
                                        spacing="2", align="center",
                                    ),
                                    calendar_widget(),
                                    spacing="2",
                                ),
                            ),

                            # 이번 주 알림 카드
                            rx.box(
                                rx.vstack(
                                    rx.hstack(
                                        rx.text("🔔", font_size="0.9rem"),
                                        rx.text("이번 주 알림",
                                                font_size="0.82rem", font_weight="700",
                                                color=TEXT_PRI),
                                        spacing="1", align="center",
                                    ),
                                    rx.hstack(
                                        rx.box(
                                            rx.vstack(
                                                rx.text(DashState.expiry_week,
                                                        font_size="1.4rem",
                                                        font_weight="800", color=ORANGE),
                                                rx.text("건 만료 예정",
                                                        font_size="0.72rem", color=TEXT_SEC),
                                                spacing="0", align="center",
                                            ),
                                            bg="#FFFBEB", border=f"1px solid #FCD34D",
                                            border_radius="10px", padding="10px 14px",
                                            flex="1", text_align="center",
                                        ),
                                        rx.box(
                                            rx.vstack(
                                                rx.text(DashState.today_orders,
                                                        font_size="1.4rem",
                                                        font_weight="800", color=ACCENT),
                                                rx.text("오늘 주문",
                                                        font_size="0.72rem", color=TEXT_SEC),
                                                spacing="0", align="center",
                                            ),
                                            bg="#ECFDF5", border="1px solid #6EE7B7",
                                            border_radius="10px", padding="10px 14px",
                                            flex="1", text_align="center",
                                        ),
                                        spacing="2", width="100%",
                                    ),
                                    spacing="2",
                                ),
                                bg=CARD, border=f"1px solid {BORDER}",
                                border_radius="16px", padding="16px", width="100%",
                            ),

                            width="300px", flex_shrink="0", spacing="3", align="stretch",
                        ),
                        spacing="4", align="start", width="100%",
                    ),
                    spacing="4", align="stretch", width="100%",
                ),
                padding="24px 28px",
                width="100%",
                overflow_y="auto",
            ),
            spacing="0", align="stretch", width="100%",
        ),
        flex="1",
        min_width="0",
        overflow="hidden",
        display="flex",
        flex_direction="column",
    )


# ════════════════════════════════════════════════════════════════
#  로딩 / 에러 화면
# ════════════════════════════════════════════════════════════════
def loading_screen() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.box(
                rx.vstack(
                    rx.text("🌱", font_size="2.5rem"),
                    rx.text("BaroFarm", font_size="1.2rem", font_weight="800",
                            color=ACCENT, letter_spacing="-0.02em"),
                    spacing="1", align="center",
                ),
                margin_bottom="20px",
            ),
            rx.spinner(size="3", color=ACCENT),
            rx.text("농장 데이터를 불러오는 중…", color=TEXT_SEC, font_size="0.9rem"),
            spacing="3", align="center",
        ),
        height="100vh", width="100%", bg=BG,
    )


# ════════════════════════════════════════════════════════════════
#  페이지 루트
# ════════════════════════════════════════════════════════════════
def index() -> rx.Component:
    return rx.box(
        rx.cond(
            DashState.loaded,
            rx.cond(
                DashState.error != "",
                rx.center(
                    rx.box(
                        rx.vstack(
                            rx.text("⚠️", font_size="2rem"),
                            rx.text(DashState.error, color=TEXT_SEC),
                            spacing="2", align="center",
                        ),
                        bg=CARD, border=f"1px solid {BORDER}", border_radius="16px",
                        padding="40px",
                    ),
                    height="100vh", bg=BG,
                ),
                rx.hstack(
                    sidebar(),
                    main_content(),
                    spacing="0",
                    align="start",
                    width="100%",
                    min_height="100vh",
                ),
            ),
            loading_screen(),
        ),
        bg=BG,
        font_family="'Inter', 'Pretendard', sans-serif",
        width="100%",
        overflow_x="hidden",
    )


app = rx.App(
    theme=rx.theme(appearance="light", accent_color="green", radius="large"),
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap",
        "https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css",
    ],
)
app.add_page(index, route="/", title="BaroFarm 농장 대시보드", on_load=DashState.load)
