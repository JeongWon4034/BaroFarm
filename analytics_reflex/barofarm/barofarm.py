"""
BaroFarm 농장 분석 대시보드 (Reflex)
====================================
Figma '관리자 대시보드' 스타일:
  - 흰 사이드바 + 다크 상단 헤더
  - 주간 달력 뷰 (월~일, 이벤트 카드)
  - KPI: 소형 3 + 컬러 accent 3
  - AI 예측 5탭
"""
import reflex as rx
from .state import DashState

# ── 토큰 ────────────────────────────────────────────────────────
HEADER_BG   = "#1E2A3B"
SIDEBAR_BG  = "#FFFFFF"
BORDER_CLR  = "#E8EDF2"
BG          = "#F4F6FA"
CARD        = "#FFFFFF"
TEXT_PRI    = "#1A2332"
TEXT_SEC    = "#6B7B8D"
ACCENT      = "#1B5E3F"
ACCENT_L    = "#40916C"
BLUE        = "#3B82F6"
GREEN_CARD  = "#22C55E"
NAVY_CARD   = "#1E2A3B"
ORANGE      = "#F59E0B"
SIDEBAR_W   = "210px"


# ════════════════════════════════════════════════════════════════
#  상단 헤더 (다크 네이비)
# ════════════════════════════════════════════════════════════════
def top_header() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.hstack(
                rx.box(
                    rx.text("🌱", font_size="1.2rem"),
                    width="34px", height="34px", border_radius="8px",
                    bg="rgba(255,255,255,0.1)",
                    display="flex", align_items="center", justify_content="center",
                ),
                rx.vstack(
                    rx.text("BaroFarm", font_size="0.95rem", font_weight="700",
                            color="white", letter_spacing="-0.01em"),
                    rx.text("농장 판매자 관리", font_size="0.65rem",
                            color="rgba(255,255,255,0.5)"),
                    spacing="0", align="start",
                ),
                spacing="2", align="center",
            ),
            rx.spacer(),
            rx.hstack(
                rx.button(
                    rx.hstack(rx.text("📦"), rx.text("주문 접수"),
                              spacing="1", align="center"),
                    bg=ORANGE, color="white", size="2",
                    border_radius="8px", font_weight="600",
                    _hover={"bg": "#D97706"},
                    border="none", cursor="pointer",
                ),
                rx.button(
                    rx.hstack(rx.text("🏠"), rx.text("홈으로"),
                              spacing="1", align="center"),
                    bg="rgba(255,255,255,0.1)", color="rgba(255,255,255,0.85)",
                    size="2", border_radius="8px", font_weight="500",
                    border="1px solid rgba(255,255,255,0.15)", cursor="pointer",
                    _hover={"bg": "rgba(255,255,255,0.18)"},
                ),
                rx.button(
                    rx.hstack(rx.text("☰"), rx.text("전체메뉴"),
                              spacing="1", align="center"),
                    bg="rgba(255,255,255,0.1)", color="rgba(255,255,255,0.85)",
                    size="2", border_radius="8px", font_weight="500",
                    border="1px solid rgba(255,255,255,0.15)", cursor="pointer",
                    _hover={"bg": "rgba(255,255,255,0.18)"},
                ),
                spacing="2",
            ),
            width="100%", align="center",
        ),
        bg=HEADER_BG, padding="14px 24px",
        position="sticky", top="0", z_index="100",
        width="100%",
    )


# ════════════════════════════════════════════════════════════════
#  흰 사이드바
# ════════════════════════════════════════════════════════════════
def nav_item(icon: str, label: str, key: str, badge: str = "") -> rx.Component:
    active = DashState.active_nav == key
    return rx.box(
        rx.hstack(
            rx.text(icon, font_size="1rem", width="20px", text_align="center"),
            rx.text(label, font_size="0.83rem",
                    font_weight=rx.cond(active, "600", "400")),
            rx.spacer(),
            rx.cond(badge != "",
                    rx.badge(badge, color_scheme="red", size="1", radius="full"),
                    rx.fragment()),
            spacing="2", align="center", width="100%",
        ),
        on_click=DashState.set_nav(key),
        padding="9px 14px",
        border_radius="8px",
        cursor="pointer",
        color=rx.cond(active, ACCENT, TEXT_SEC),
        bg=rx.cond(active, "rgba(27,94,63,0.07)", "transparent"),
        border_left=rx.cond(active, f"3px solid {ACCENT}",
                            "3px solid transparent"),
        _hover={"bg": "#F1F5F9", "color": TEXT_PRI},
        transition="all .15s",
        width="100%",
    )


def sidebar_section(title: str) -> rx.Component:
    return rx.text(title, font_size="0.65rem", font_weight="700",
                   color="#94A3B8", letter_spacing="0.08em",
                   padding="10px 14px 4px")


def sidebar() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.box(
                rx.hstack(
                    rx.box(rx.text("🏡", font_size="1rem"),
                           width="34px", height="34px", border_radius="8px",
                           bg="rgba(27,94,63,0.08)",
                           display="flex", align_items="center",
                           justify_content="center"),
                    rx.vstack(
                        rx.text(DashState.seller_name, font_size="0.82rem",
                                font_weight="700", color=TEXT_PRI),
                        rx.text("판매자", font_size="0.65rem", color=TEXT_SEC),
                        spacing="0", align="start",
                    ),
                    spacing="2", align="center",
                ),
                bg="#F8FAF9", border_radius="10px",
                padding="10px 12px", margin="12px",
                border="1px solid rgba(27,94,63,0.12)",
            ),
            rx.divider(border_color=BORDER_CLR),
            rx.box(
                rx.vstack(
                    nav_item("🏠", "관리자홈",    "dashboard"),
                    nav_item("📞", "주문 알림",   "orders",  DashState.today_orders),
                    nav_item("🔔", "알림",        "alerts",  DashState.expiry_week),
                    spacing="0", width="100%", padding_x="6px",
                ),
            ),
            sidebar_section("주문·배송 관리"),
            rx.box(
                rx.vstack(
                    nav_item("🚚", "배송 현황",  "delivery"),
                    nav_item("📋", "주문 내역",  "history"),
                    nav_item("📦", "재고 관리",  "stock"),
                    spacing="0", width="100%", padding_x="6px",
                ),
            ),
            sidebar_section("AI 분석"),
            rx.box(
                rx.vstack(
                    nav_item("📈", "매출 예측",  "revenue"),
                    nav_item("🛒", "매입 추천",  "reco"),
                    nav_item("👥", "고객 분석",  "segment"),
                    spacing="0", width="100%", padding_x="6px",
                ),
            ),
            sidebar_section("설정"),
            rx.box(
                rx.vstack(
                    nav_item("⚙️", "농장 설정",  "settings"),
                    spacing="0", width="100%", padding_x="6px",
                ),
            ),
            rx.spacer(),
            rx.divider(border_color=BORDER_CLR),
            rx.text(DashState.period, font_size="0.68rem", color="#94A3B8",
                    text_align="center", padding="10px 8px"),
            spacing="0", align="stretch", width="100%",
        ),
        width=SIDEBAR_W, min_height="100%",
        bg=SIDEBAR_BG, border_right=f"1px solid {BORDER_CLR}",
        flex_shrink="0", overflow_y="auto",
    )


# ════════════════════════════════════════════════════════════════
#  KPI 카드
# ════════════════════════════════════════════════════════════════
def kpi_small(icon: str, label: str, value) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.box(rx.text(icon, font_size="1rem"),
                   bg="#F1F5F9", border_radius="8px",
                   width="32px", height="32px",
                   display="flex", align_items="center",
                   justify_content="center"),
            rx.vstack(
                rx.text(label, font_size="0.7rem", color=TEXT_SEC),
                rx.text(value, font_size="1.3rem", font_weight="800",
                        color=TEXT_PRI),
                spacing="0",
            ),
            spacing="2", align="center",
        ),
        bg=CARD, border=f"1px solid {BORDER_CLR}", border_radius="12px",
        padding="14px 16px", flex="1",
        box_shadow="0 1px 3px rgba(0,0,0,0.04)",
    )


def kpi_accent(icon: str, label: str, value, sub: str,
               bg_color: str) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.box(rx.text(icon, font_size="1.1rem"),
                       bg="rgba(255,255,255,0.15)", border_radius="8px",
                       width="32px", height="32px",
                       display="flex", align_items="center",
                       justify_content="center"),
                rx.badge("이번 달", size="1",
                         style={"background": "rgba(255,255,255,0.2)",
                                "color": "rgba(255,255,255,0.85)"}),
                width="100%", justify="between", align="center",
            ),
            rx.text(label, font_size="0.78rem",
                    color="rgba(255,255,255,0.75)", font_weight="500"),
            rx.text(value, font_size="1.6rem", font_weight="800",
                    color="white"),
            rx.text(sub, font_size="0.7rem",
                    color="rgba(255,255,255,0.6)"),
            spacing="1", align="start",
        ),
        bg=bg_color, border_radius="14px",
        padding="16px", flex="1",
        box_shadow=f"0 4px 16px {bg_color}55",
    )


# ════════════════════════════════════════════════════════════════
#  주간 달력 (Figma 스타일)
# ════════════════════════════════════════════════════════════════
STATUS_BG = {
    "접수":  "#EBF8FF", "처리중": "#FEF3C7", "배송중": "#E0F2FE",
    "완료":  "#DCFCE7", "취소":   "#FEE2E2",
}
STATUS_BORDER = {
    "접수":  "#3B82F6", "처리중": "#F59E0B", "배송중": "#0EA5E9",
    "완료":  "#22C55E", "취소":   "#EF4444",
}
STATUS_TEXT = {
    "접수":  "#1D4ED8", "처리중": "#92400E", "배송중": "#075985",
    "완료":  "#166534", "취소":   "#991B1B",
}


def order_event_card(order_row) -> rx.Component:
    product = order_row[0]
    buyer   = order_row[1]
    amount  = order_row[2]
    status  = order_row[3]
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.box(
                    rx.text(status, font_size="0.6rem", font_weight="700",
                            color=TEXT_SEC),
                    bg="#F1F5F9", border="1px solid #E2E8F0",
                    border_radius="4px", padding="1px 5px",
                    border_left="2px solid #3B82F6",
                ),
                rx.spacer(),
            ),
            rx.text(product, font_size="0.75rem", font_weight="600",
                    color=TEXT_PRI),
            rx.text(buyer, font_size="0.68rem", color=TEXT_SEC),
            rx.text(amount, font_size="0.72rem", font_weight="700",
                    color=ACCENT),
            spacing="0",
        ),
        bg="#F8FFFE", border_radius="8px",
        padding="7px 8px", width="100%",
        border="1px solid #E0F2FE",
        border_left="3px solid #3B82F6",
        margin_bottom="4px",
    )


def weekly_calendar() -> rx.Component:
    return rx.box(
        rx.vstack(
            # 7열 요일 헤더
            rx.box(
                rx.foreach(
                    DashState.weekly_days,
                    lambda d: rx.box(
                        rx.vstack(
                            rx.text(d[0], font_size="0.72rem", font_weight="600",
                                    color=rx.cond(d[2] == "true",
                                                  "white", TEXT_SEC),
                                    text_align="center"),
                            rx.box(
                                rx.text(d[1], font_size="0.8rem",
                                        font_weight="700",
                                        color=rx.cond(d[2] == "true",
                                                      "white", TEXT_PRI)),
                                bg=rx.cond(d[2] == "true",
                                           ACCENT, "transparent"),
                                border_radius="6px", padding="2px 6px",
                            ),
                            rx.cond(
                                d[3] != "0",
                                rx.badge(
                                    d[3],
                                    color_scheme="green", size="1",
                                    variant="soft",
                                ),
                                rx.fragment(),
                            ),
                            spacing="0", align="center",
                        ),
                        bg=rx.cond(d[2] == "true",
                                   f"{ACCENT}0A", "#FAFBFC"),
                        border=rx.cond(d[2] == "true",
                                       f"1px solid {ACCENT}30",
                                       f"1px solid {BORDER_CLR}"),
                        border_radius="10px",
                        padding="8px 6px", text_align="center",
                        flex="1",
                    ),
                ),
                display="flex", gap="6px", width="100%",
            ),
            # 이벤트 열
            rx.box(
                rx.foreach(
                    DashState.weekly_orders,
                    lambda day_orders: rx.box(
                        rx.cond(
                            day_orders.length() == 0,
                            rx.box(
                                rx.text("예약 없음", font_size="0.68rem",
                                        color="#CBD5E1",
                                        text_align="center"),
                                padding="14px 6px",
                            ),
                            rx.vstack(
                                rx.foreach(day_orders, order_event_card),
                                spacing="0", align="stretch", padding="4px",
                            ),
                        ),
                        flex="1", min_height="90px",
                        border_right=f"1px solid {BORDER_CLR}",
                    ),
                ),
                display="flex", gap="0px", width="100%",
                border=f"1px solid {BORDER_CLR}",
                border_radius="10px", overflow="hidden",
                min_height="90px",
            ),
            spacing="2",
        ),
        bg=CARD, border=f"1px solid {BORDER_CLR}", border_radius="16px",
        padding="20px", width="100%",
        box_shadow="0 1px 4px rgba(0,0,0,0.04)",
    )


# ════════════════════════════════════════════════════════════════
#  section wrapper
# ════════════════════════════════════════════════════════════════
def section_header(icon_bg: str, icon: str, title: str,
                   more: bool = True) -> rx.Component:
    return rx.hstack(
        rx.box(rx.text(icon, font_size="0.9rem"),
               width="28px", height="28px", border_radius="6px",
               bg=icon_bg,
               display="flex", align_items="center",
               justify_content="center"),
        rx.text(title, font_size="0.9rem", font_weight="700", color=TEXT_PRI),
        rx.spacer(),
        rx.cond(more,
                rx.text("더보기", font_size="0.78rem", color=TEXT_SEC,
                        cursor="pointer", _hover={"color": ACCENT}),
                rx.fragment()),
        spacing="2", align="center",
    )


def section_box(*children) -> rx.Component:
    return rx.box(
        rx.vstack(*children, spacing="3", align="stretch"),
        bg=CARD, border=f"1px solid {BORDER_CLR}", border_radius="16px",
        padding="20px", width="100%",
        box_shadow="0 1px 4px rgba(0,0,0,0.04)",
    )


# ════════════════════════════════════════════════════════════════
#  AI 탭
# ════════════════════════════════════════════════════════════════
def info_box(msg: str) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.text("📭", font_size="2rem"),
            rx.text(msg, color=TEXT_SEC, font_size="0.85rem"),
            spacing="2", align="center",
        ),
        bg="#F8FAFC", border=f"1px dashed {BORDER_CLR}",
        border_radius="12px", padding="36px",
        text_align="center", width="100%",
    )


def chart_box(fig, caption: str = "") -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.plotly(data=fig, width="100%", height="360px"),
            rx.cond(caption != "",
                    rx.text(caption, font_size="0.72rem", color=TEXT_SEC),
                    rx.fragment()),
            spacing="1",
        ),
        bg=CARD, border=f"1px solid {BORDER_CLR}",
        border_radius="14px", padding="16px", width="100%",
    )


def str_table(headers: list[str], rows) -> rx.Component:
    return rx.table.root(
        rx.table.header(rx.table.row(
            *[rx.table.column_header_cell(
                h, color=TEXT_SEC, font_size="0.73rem", font_weight="600",
            ) for h in headers]
        )),
        rx.table.body(rx.foreach(rows, lambda row: rx.table.row(
            rx.foreach(row, lambda cell: rx.table.cell(
                cell, font_size="0.8rem", color=TEXT_PRI,
            ))
        ))),
        variant="surface", size="1", width="100%",
    )


def mini_stat(label: str, value, color: str) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.text(label, font_size="0.72rem", color=TEXT_SEC),
            rx.text(value, font_size="1.2rem", font_weight="800", color=color),
            spacing="0", align="start",
        ),
        bg=CARD, border=f"1px solid {BORDER_CLR}",
        border_radius="10px", padding="12px 16px", flex="1",
    )


def tab_revenue() -> rx.Component:
    return rx.cond(
        DashState.has_revenue,
        rx.vstack(
            rx.hstack(
                mini_stat("예측 30일 총매출", DashState.fc_total, ACCENT),
                mini_stat("일평균 예측",       DashState.fc_daily, BLUE),
                mini_stat("모델 R²",            DashState.fc_r2,   ORANGE),
                spacing="3", width="100%",
            ),
            chart_box(DashState.revenue_fig,
                      "Ridge Regression · 주간/월간 sin/cos 피처. 주황 점선=30일 예측"),
            spacing="3", width="100%", align="stretch",
        ),
        info_box("예측 데이터 부족 (최소 2주 이상 주문 이력 필요)"),
    )


def tab_reco() -> rx.Component:
    return rx.cond(
        DashState.has_reco,
        rx.vstack(
            chart_box(DashState.reco_fig,
                      "velocity·trend·rev_share·재구매율 MinMax 가중합 Top-10"),
            rx.box(
                str_table(["상품명", "카테고리", "추천점수", "트렌드", "이유"],
                          DashState.reco_table),
                bg=CARD, border=f"1px solid {BORDER_CLR}",
                border_radius="12px", padding="10px",
            ),
            spacing="3", width="100%", align="stretch",
        ),
        info_box("매입 추천 스코어 계산에 필요한 주문 데이터가 부족합니다."),
    )


def tab_demand() -> rx.Component:
    return rx.cond(
        DashState.has_demand,
        rx.vstack(
            chart_box(DashState.demand_fig,
                      "주간 판매량 LinearRegression 4주 예측"),
            rx.box(
                str_table(["상품명", "카테고리", "현재 주간수요", "예측 주간수요", "트렌드"],
                          DashState.demand_table),
                bg=CARD, border=f"1px solid {BORDER_CLR}",
                border_radius="12px", padding="10px",
            ),
            spacing="3", width="100%", align="stretch",
        ),
        info_box("수요 예측 데이터 부족 (상품당 최소 4주 이상)"),
    )


def tab_segment() -> rx.Component:
    return rx.cond(
        DashState.has_segment,
        rx.vstack(
            chart_box(DashState.segment_fig,
                      "RFM StandardScaler 정규화 → KMeans(k=4)"),
            rx.box(
                str_table(["세그먼트", "고객수", "평균구매횟수", "평균매출"],
                          DashState.segment_table),
                bg=CARD, border=f"1px solid {BORDER_CLR}",
                border_radius="12px", padding="10px",
            ),
            spacing="3", width="100%", align="stretch",
        ),
        info_box("세그멘테이션 고객 수 부족"),
    )


def tab_season() -> rx.Component:
    return rx.cond(
        DashState.has_season,
        rx.vstack(
            chart_box(DashState.season_heat_fig,
                      "카테고리 × 월별 매출 히트맵"),
            chart_box(DashState.season_growth_fig),
            rx.cond(DashState.season_up != "",
                    rx.box(
                        rx.hstack(
                            rx.text("📈", font_size="1rem"),
                            rx.vstack(
                                rx.text("매입 확대 추천",
                                        font_size="0.76rem", font_weight="600",
                                        color="#065F46"),
                                rx.text(DashState.season_up,
                                        font_size="0.8rem", color="#047857"),
                                spacing="0",
                            ),
                            spacing="2",
                        ),
                        bg="#ECFDF5", border="1px solid #6EE7B7",
                        border_radius="10px", padding="12px",
                    ),
                    rx.fragment()),
            rx.cond(DashState.season_down != "",
                    rx.box(
                        rx.hstack(
                            rx.text("📉", font_size="1rem"),
                            rx.vstack(
                                rx.text("매입 축소 검토",
                                        font_size="0.76rem", font_weight="600",
                                        color="#92400E"),
                                rx.text(DashState.season_down,
                                        font_size="0.8rem", color="#B45309"),
                                spacing="0",
                            ),
                            spacing="2",
                        ),
                        bg="#FFFBEB", border="1px solid #FCD34D",
                        border_radius="10px", padding="12px",
                    ),
                    rx.fragment()),
            spacing="3", width="100%", align="stretch",
        ),
        info_box("계절성 분석 데이터 부족"),
    )


# ════════════════════════════════════════════════════════════════
#  최근 알림 아이템
# ════════════════════════════════════════════════════════════════
def recent_item(icon: str, category: str, msg: str, color: str) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.box(rx.text(icon, font_size="0.8rem"),
                   width="26px", height="26px", border_radius="6px",
                   bg=color + "15",
                   display="flex", align_items="center",
                   justify_content="center"),
            rx.vstack(
                rx.hstack(
                    rx.badge(category, size="1", variant="soft",
                             style={"background": color + "18",
                                    "color": color}),
                    rx.spacer(),
                    rx.text("방금 전", font_size="0.65rem", color="#94A3B8"),
                    width="100%",
                ),
                rx.text(msg, font_size="0.78rem", color=TEXT_PRI),
                spacing="0",
            ),
            spacing="2", align="start", width="100%",
        ),
        border_bottom=f"1px solid {BORDER_CLR}",
        padding_y="8px",
    )


# ════════════════════════════════════════════════════════════════
#  메인 콘텐츠
# ════════════════════════════════════════════════════════════════
def main_content() -> rx.Component:
    return rx.box(
        rx.vstack(
            # 브레드크럼
            rx.hstack(
                rx.text("□", font_size="0.75rem", color=TEXT_SEC),
                rx.text("›", font_size="0.75rem", color="#CBD5E1"),
                rx.text("농장 분석 관리", font_size="0.75rem", color=TEXT_SEC),
                spacing="1", align="center",
            ),

            # 페이지 제목
            rx.hstack(
                rx.text("관리자홈", font_size="1.4rem", font_weight="800",
                        color=TEXT_PRI, letter_spacing="-0.02em"),
                rx.spacer(),
                rx.button(
                    rx.hstack(rx.text("⚙️"), rx.text("위젯 편집"),
                              spacing="1", align="center"),
                    bg=CARD, color=TEXT_SEC, size="2",
                    border=f"1px solid {BORDER_CLR}", border_radius="8px",
                    font_weight="500", cursor="pointer",
                    _hover={"bg": "#F1F5F9"},
                ),
                width="100%", align="center",
            ),

            # ── 실시간 현황 ──
            section_header("rgba(27,94,63,0.1)", "📊", "실시간 현황"),

            # KPI 소형 3
            rx.hstack(
                kpi_small("📥", "금일 접수",  DashState.today_orders),
                kpi_small("⚠️", "7일내 만료", DashState.expiry_week),
                kpi_small("👥", "구매 고객",  DashState.kpi_buyers),
                spacing="3", width="100%",
            ),

            # KPI 컬러 3
            rx.hstack(
                kpi_accent("📦", "이번달 주문 수",    DashState.kpi_orders,
                           "오늘 기준",               "#3B7DD8"),
                kpi_accent("💰", "이번달 매출 (GMV)", DashState.kpi_gmv,
                           DashState.kpi_aov + " 객단가", "#22A55B"),
                kpi_accent("🏷️", "할인 매출",         DashState.kpi_deal,
                           DashState.kpi_deal_share + " 비중", NAVY_CARD),
                spacing="3", width="100%",
            ),

            rx.divider(border_color=BORDER_CLR),

            # ── 예약·배송 현황 (주간 달력) ──
            section_header("rgba(59,130,246,0.1)", "📅", "예약·배송 현황"),
            weekly_calendar(),

            rx.divider(border_color=BORDER_CLR),

            # ── 예산 사용 현황 + 핫라인 2단 ──
            rx.hstack(
                # 예산 사용
                section_box(
                    rx.hstack(
                        rx.box(rx.text("💳"), bg="#EEF2FF", border_radius="6px",
                               width="26px", height="26px",
                               display="flex", align_items="center",
                               justify_content="center"),
                        rx.text("예산 사용 현황", font_size="0.88rem",
                                font_weight="700", color=TEXT_PRI),
                        spacing="2", align="center",
                    ),
                    rx.hstack(
                        rx.vstack(
                            rx.text("총 매출", font_size="0.7rem", color=TEXT_SEC),
                            rx.text(DashState.kpi_gmv, font_size="1.05rem",
                                    font_weight="700", color=TEXT_PRI),
                            spacing="0",
                        ),
                        rx.spacer(),
                        rx.vstack(
                            rx.text("재구매율", font_size="0.7rem", color=TEXT_SEC),
                            rx.text(DashState.kpi_repurchase, font_size="1.05rem",
                                    font_weight="700", color=ACCENT),
                            spacing="0",
                        ),
                        width="100%",
                    ),
                    rx.box(
                        rx.box(
                            height="8px", width="65%",
                            bg=f"linear-gradient(90deg,{ACCENT},{ACCENT_L})",
                            border_radius="4px",
                        ),
                        bg="#E8F4EC", border_radius="4px",
                        height="8px", width="100%", overflow="hidden",
                    ),
                    rx.hstack(
                        rx.box(
                            rx.vstack(
                                rx.text("구매 고객", font_size="0.7rem",
                                        color="white", opacity="0.75"),
                                rx.text(DashState.kpi_buyers, font_size="1rem",
                                        font_weight="700", color="white"),
                                spacing="0",
                            ),
                            bg=ACCENT, border_radius="10px",
                            padding="10px 14px", flex="1",
                        ),
                        rx.box(
                            rx.vstack(
                                rx.text("객단가", font_size="0.7rem",
                                        color="white", opacity="0.75"),
                                rx.text(DashState.kpi_aov, font_size="1rem",
                                        font_weight="700", color="white"),
                                spacing="0",
                            ),
                            bg=BLUE, border_radius="10px",
                            padding="10px 14px", flex="1",
                        ),
                        spacing="2", width="100%",
                    ),
                ),

                # 핫라인(알림)
                section_box(
                    rx.hstack(
                        rx.box(rx.text("📞"), bg="#FFF7ED", border_radius="6px",
                               width="26px", height="26px",
                               display="flex", align_items="center",
                               justify_content="center"),
                        rx.text("핫라인 관리", font_size="0.88rem",
                                font_weight="700", color=TEXT_PRI),
                        spacing="2", align="center",
                    ),
                    rx.hstack(
                        rx.box(
                            rx.vstack(
                                rx.text("답변대기", font_size="0.66rem",
                                        color=ORANGE, font_weight="600"),
                                rx.text(DashState.expiry_week, font_size="1.3rem",
                                        font_weight="800", color=ORANGE),
                                spacing="0",
                            ),
                            bg="#FFFBEB", border_radius="10px",
                            padding="12px", flex="1", text_align="center",
                        ),
                        rx.box(
                            rx.vstack(
                                rx.text("오늘 주문", font_size="0.66rem",
                                        color=ACCENT, font_weight="600"),
                                rx.text(DashState.today_orders,
                                        font_size="1.3rem", font_weight="800",
                                        color=ACCENT),
                                spacing="0",
                            ),
                            bg="#ECFDF5", border_radius="10px",
                            padding="12px", flex="1", text_align="center",
                        ),
                        spacing="2", width="100%",
                    ),
                    rx.text("최근 문의내역", font_size="0.75rem",
                            font_weight="600", color=TEXT_SEC),
                    rx.vstack(
                        recent_item("🚚", "배송문의",
                                    "배송 가능 날짜가 언제인가요?", BLUE),
                        recent_item("📦", "상품문의",
                                    "로트 만료 상품 교환 가능한가요?", ORANGE),
                        recent_item("💬", "일반문의",
                                    "농장 직거래 연락처 알 수 있을까요?", ACCENT),
                        spacing="0",
                    ),
                ),
                spacing="4", width="100%", align="start",
            ),

            rx.divider(border_color=BORDER_CLR),

            # ── AI 분석 탭 ──
            section_box(
                rx.hstack(
                    rx.box(rx.text("🤖"), bg="rgba(27,94,63,0.08)",
                           border_radius="6px", width="26px", height="26px",
                           display="flex", align_items="center",
                           justify_content="center"),
                    rx.text("AI 예측 & 분석", font_size="0.88rem",
                            font_weight="700", color=TEXT_PRI),
                    rx.spacer(),
                    rx.badge("scikit-learn", color_scheme="green",
                             size="1", variant="surface"),
                    spacing="2", align="center",
                ),
                rx.tabs.root(
                    rx.tabs.list(
                        rx.tabs.trigger("📈 매출",     value="rev"),
                        rx.tabs.trigger("🛒 매입추천",  value="reco"),
                        rx.tabs.trigger("🔮 수요",     value="dem"),
                        rx.tabs.trigger("👥 고객",     value="seg"),
                        rx.tabs.trigger("📅 계절성",   value="season"),
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
            ),

            spacing="4", align="stretch", width="100%",
            padding_bottom="40px",
        ),
        padding="20px 28px",
        flex="1", min_width="0", overflow_y="auto",
        bg=BG,
    )


# ════════════════════════════════════════════════════════════════
#  로딩 / 에러
# ════════════════════════════════════════════════════════════════
def loading_screen() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.text("🌱", font_size="2.5rem"),
            rx.spinner(size="3", style={"color": ACCENT}),
            rx.text("농장 데이터를 불러오는 중…",
                    color=TEXT_SEC, font_size="0.9rem"),
            spacing="3", align="center",
        ),
        height="100vh", width="100%", bg=BG,
    )


# ════════════════════════════════════════════════════════════════
#  루트 페이지
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
                        bg=CARD, border=f"1px solid {BORDER_CLR}",
                        border_radius="16px", padding="40px",
                    ),
                    height="100vh", bg=BG,
                ),
                rx.vstack(
                    top_header(),
                    rx.hstack(
                        sidebar(),
                        main_content(),
                        spacing="0", align="start",
                        width="100%", flex="1",
                    ),
                    spacing="0", align="stretch",
                    width="100%", min_height="100vh",
                ),
            ),
            loading_screen(),
        ),
        bg=BG,
        font_family="'Inter', 'Pretendard', sans-serif",
        width="100%",
    )


app = rx.App(
    theme=rx.theme(appearance="light", accent_color="green", radius="large"),
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap",
        "https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css",
    ],
)
app.add_page(index, route="/", title="BaroFarm 농장 대시보드",
             on_load=DashState.load)
