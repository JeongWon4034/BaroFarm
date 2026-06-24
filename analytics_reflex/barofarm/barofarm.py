"""
BaroFarm 농장 분석 대시보드 (Reflex)
====================================
Figma '관리자 대시보드' 스타일 + 사이드바 라우팅
  - 흰 사이드바(클릭 시 본문 전환) + 다크 상단 헤더
  - 관리자홈: KPI + 주간 달력(날짜 클릭→당일 매출) + 당일 상세
  - 일정·배송: 월간 점 달력(날짜 클릭→당일 매출)
  - AI 예측·분석: 매출/매입/수요/고객/계절성 각각 별도 페이지
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
NAVY_CARD   = "#1E2A3B"
ORANGE      = "#F59E0B"
SIDEBAR_W   = "220px"


# ════════════════════════════════════════════════════════════════
#  상단 헤더
# ════════════════════════════════════════════════════════════════
def top_header() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.hstack(
                rx.box(rx.text("🌱", font_size="1.2rem"),
                       width="34px", height="34px", border_radius="8px",
                       bg="rgba(255,255,255,0.1)",
                       display="flex", align_items="center",
                       justify_content="center"),
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
                    bg=ORANGE, color="white", size="2", border_radius="8px",
                    font_weight="600", border="none", cursor="pointer",
                    _hover={"bg": "#D97706"},
                ),
                rx.button(
                    rx.hstack(rx.text("🏠"), rx.text("홈으로"),
                              spacing="1", align="center"),
                    bg="rgba(255,255,255,0.1)", color="rgba(255,255,255,0.85)",
                    size="2", border_radius="8px", font_weight="500",
                    border="1px solid rgba(255,255,255,0.15)", cursor="pointer",
                    on_click=DashState.set_nav("dashboard"),
                    _hover={"bg": "rgba(255,255,255,0.18)"},
                ),
                spacing="2",
            ),
            width="100%", align="center",
        ),
        bg=HEADER_BG, padding="14px 24px",
        position="sticky", top="0", z_index="100", width="100%",
    )


# ════════════════════════════════════════════════════════════════
#  흰 사이드바 (클릭 → 본문 전환)
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
        padding="9px 14px", border_radius="8px", cursor="pointer",
        color=rx.cond(active, ACCENT, TEXT_SEC),
        bg=rx.cond(active, "rgba(27,94,63,0.07)", "transparent"),
        border_left=rx.cond(active, f"3px solid {ACCENT}",
                            "3px solid transparent"),
        _hover={"bg": "#F1F5F9", "color": TEXT_PRI},
        transition="all .15s", width="100%",
    )


def sidebar_section(title: str) -> rx.Component:
    return rx.text(title, font_size="0.65rem", font_weight="700",
                   color="#94A3B8", letter_spacing="0.08em",
                   padding="12px 14px 4px")


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
                    nav_item("🏠", "관리자 홈", "dashboard"),
                    nav_item("📞", "핫라인", "hotline", DashState.ord_pending),
                    nav_item("🔔", "알림", "alerts", DashState.alert_count),
                    spacing="0", width="100%", padding_x="6px",
                ),
                padding_top="6px",
            ),
            sidebar_section("주문·배송 관리"),
            rx.box(
                rx.vstack(
                    nav_item("🚚", "배송 내역", "delivery", DashState.ord_shipping),
                    nav_item("🧾", "청구 관리", "billing"),
                    nav_item("📦", "보관상품 관리", "inventory", DashState.sup_expiry),
                    nav_item("🗓️", "일정·배송 달력", "calendar"),
                    spacing="0", width="100%", padding_x="6px",
                ),
            ),
            sidebar_section("AI 분석·예측"),
            rx.box(
                rx.vstack(
                    nav_item("🚀", "공급망 최적화", "supply", DashState.sup_expiry),
                    nav_item("📈", "매출 예측", "revenue"),
                    nav_item("🛒", "매입 추천", "reco"),
                    nav_item("🔮", "수요 예측", "demand"),
                    nav_item("👥", "고객 분석", "segment"),
                    nav_item("📅", "계절성 분석", "season"),
                    spacing="0", width="100%", padding_x="6px",
                ),
            ),
            sidebar_section("콘텐츠 관리"),
            rx.box(
                rx.vstack(
                    nav_item("📢", "공지사항 관리", "notices"),
                    nav_item("🪟", "팝업창 관리", "popups"),
                    spacing="0", width="100%", padding_x="6px",
                ),
            ),
            sidebar_section("설정"),
            rx.box(
                rx.vstack(
                    nav_item("🔒", "보안 설정", "security"),
                    nav_item("👤", "담당자 관리", "staff"),
                    spacing="0", width="100%", padding_x="6px",
                ),
            ),
            sidebar_section("추가 설정 기능 (예정)"),
            rx.box(
                rx.vstack(
                    nav_item("🧑‍🤝‍🧑", "회원 관리", "members"),
                    nav_item("💬", "문자 관리", "sms"),
                    nav_item("💰", "예산 관리", "budget"),
                    nav_item("🎁", "포인트·기부적립", "points"),
                    spacing="0", width="100%", padding_x="6px",
                ),
            ),
            rx.divider(border_color=BORDER_CLR, margin_top="8px"),
            rx.text(DashState.period, font_size="0.68rem", color="#94A3B8",
                    text_align="center", padding="10px 8px"),
            spacing="0", align="stretch", width="100%",
        ),
        width=SIDEBAR_W, min_height="100%",
        bg=SIDEBAR_BG, border_right=f"1px solid {BORDER_CLR}",
        flex_shrink="0", overflow_y="auto",
    )


# ════════════════════════════════════════════════════════════════
#  공통 요소
# ════════════════════════════════════════════════════════════════
def page_header(icon: str, title: str, subtitle: str) -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.text("□", font_size="0.72rem", color=TEXT_SEC),
            rx.text("›", font_size="0.72rem", color="#CBD5E1"),
            rx.text(subtitle, font_size="0.72rem", color=TEXT_SEC),
            spacing="1", align="center",
        ),
        rx.hstack(
            rx.text(icon, font_size="1.3rem"),
            rx.text(title, font_size="1.4rem", font_weight="800",
                    color=TEXT_PRI, letter_spacing="-0.02em"),
            spacing="2", align="center",
        ),
        spacing="1", align="start", width="100%",
    )


def section_box(*children) -> rx.Component:
    return rx.box(
        rx.vstack(*children, spacing="3", align="stretch"),
        bg=CARD, border=f"1px solid {BORDER_CLR}", border_radius="16px",
        padding="20px", width="100%",
        box_shadow="0 1px 4px rgba(0,0,0,0.04)",
    )


def section_title(icon_bg: str, icon: str, title: str) -> rx.Component:
    return rx.hstack(
        rx.box(rx.text(icon, font_size="0.9rem"),
               width="28px", height="28px", border_radius="6px", bg=icon_bg,
               display="flex", align_items="center", justify_content="center"),
        rx.text(title, font_size="0.9rem", font_weight="700", color=TEXT_PRI),
        spacing="2", align="center",
    )


def kpi_small(icon: str, label: str, value) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.box(rx.text(icon, font_size="1rem"),
                   bg="#F1F5F9", border_radius="8px", width="32px", height="32px",
                   display="flex", align_items="center", justify_content="center"),
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


def kpi_accent(icon: str, label: str, value, sub: str, bg_color: str) -> rx.Component:
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
            rx.text(value, font_size="1.6rem", font_weight="800", color="white"),
            rx.text(sub, font_size="0.7rem", color="rgba(255,255,255,0.6)"),
            spacing="1", align="start",
        ),
        bg=bg_color, border_radius="14px", padding="16px", flex="1",
        box_shadow=f"0 4px 16px {bg_color}55",
    )


# ════════════════════════════════════════════════════════════════
#  당일 매출 상세 카드 (날짜 클릭 시)
# ════════════════════════════════════════════════════════════════
def daily_detail_card() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.box(rx.text("💰", font_size="0.9rem"),
                       width="28px", height="28px", border_radius="6px",
                       bg="rgba(255,255,255,0.15)",
                       display="flex", align_items="center",
                       justify_content="center"),
                rx.vstack(
                    rx.text("선택일 매출", font_size="0.68rem",
                            color="rgba(255,255,255,0.7)"),
                    rx.text(DashState.sel_date_label, font_size="0.85rem",
                            font_weight="700", color="white"),
                    spacing="0", align="start",
                ),
                spacing="2", align="center",
            ),
            rx.text(DashState.sel_revenue, font_size="1.9rem",
                    font_weight="800", color="white"),
            rx.hstack(
                rx.vstack(
                    rx.text("주문", font_size="0.66rem",
                            color="rgba(255,255,255,0.6)"),
                    rx.text(DashState.sel_orders, font_size="0.95rem",
                            font_weight="700", color="white"),
                    spacing="0",
                ),
                rx.divider(orientation="vertical",
                           border_color="rgba(255,255,255,0.2)", height="28px"),
                rx.vstack(
                    rx.text("판매 수량", font_size="0.66rem",
                            color="rgba(255,255,255,0.6)"),
                    rx.text(DashState.sel_items, font_size="0.95rem",
                            font_weight="700", color="white"),
                    spacing="0",
                ),
                spacing="4", align="center",
            ),
            rx.box(
                rx.hstack(
                    rx.text("🏆", font_size="0.75rem"),
                    rx.text("대표 상품", font_size="0.66rem",
                            color="rgba(255,255,255,0.6)"),
                    rx.text(DashState.sel_top, font_size="0.75rem",
                            font_weight="600", color="white"),
                    spacing="1", align="center",
                ),
                bg="rgba(255,255,255,0.1)", border_radius="8px",
                padding="8px 10px", width="100%",
            ),
            spacing="3", align="start",
        ),
        bg=f"linear-gradient(135deg, {ACCENT} 0%, {ACCENT_L} 100%)",
        border_radius="16px", padding="20px", width="100%",
        box_shadow="0 4px 16px rgba(27,94,63,0.25)",
    )


# ════════════════════════════════════════════════════════════════
#  주간 달력 (날짜 클릭 가능)
# ════════════════════════════════════════════════════════════════
def order_event_card(order_row) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.box(rx.text(order_row[3], font_size="0.6rem", font_weight="700",
                           color=TEXT_SEC),
                   bg="#F1F5F9", border="1px solid #E2E8F0",
                   border_radius="4px", padding="1px 5px",
                   border_left="2px solid #3B82F6", width="fit-content"),
            rx.text(order_row[0], font_size="0.74rem", font_weight="600",
                    color=TEXT_PRI),
            rx.text(order_row[1], font_size="0.66rem", color=TEXT_SEC),
            rx.text(order_row[2], font_size="0.72rem", font_weight="700",
                    color=ACCENT),
            spacing="0",
        ),
        bg="#F8FFFE", border_radius="8px", padding="6px 8px", width="100%",
        border="1px solid #E0F2FE", border_left="3px solid #3B82F6",
        margin_bottom="4px",
    )


def weekly_calendar() -> rx.Component:
    return rx.box(
        rx.vstack(
            # 요일 헤더 (클릭 가능)
            rx.box(
                rx.foreach(
                    DashState.weekly_days,
                    lambda d: rx.box(
                        rx.vstack(
                            rx.text(d[0], font_size="0.72rem", font_weight="600",
                                    color=rx.cond(d[2] == "true", "white", TEXT_SEC)),
                            rx.box(
                                rx.text(d[1], font_size="0.8rem", font_weight="700",
                                        color=rx.cond(d[2] == "true", "white", TEXT_PRI)),
                                bg=rx.cond(d[2] == "true", ACCENT, "transparent"),
                                border_radius="6px", padding="2px 6px",
                            ),
                            rx.text(d[5], font_size="0.62rem", font_weight="600",
                                    color=rx.cond(d[2] == "true", "white", ACCENT)),
                            spacing="0", align="center",
                        ),
                        on_click=DashState.select_date(d[4]),
                        cursor="pointer",
                        bg=rx.cond(
                            DashState.sel_date == d[4], f"{ACCENT}14",
                            rx.cond(d[2] == "true", f"{ACCENT}0A", "#FAFBFC")),
                        border=rx.cond(
                            DashState.sel_date == d[4], f"2px solid {ACCENT}",
                            rx.cond(d[2] == "true", f"1px solid {ACCENT}30",
                                    f"1px solid {BORDER_CLR}")),
                        border_radius="10px", padding="8px 6px",
                        text_align="center", flex="1",
                        transition="all .12s", _hover={"bg": f"{ACCENT}10"},
                    ),
                ),
                display="flex", gap="6px", width="100%",
            ),
            # 자세히 보기 토글
            rx.hstack(
                rx.spacer(),
                rx.button(
                    rx.cond(DashState.weekly_expanded,
                            "주문 상세 접기 ▲", "주문 상세 자세히 보기 ▼"),
                    on_click=DashState.toggle_weekly,
                    bg="transparent", color=ACCENT, size="1",
                    border=f"1px solid {ACCENT}40", border_radius="8px",
                    cursor="pointer", _hover={"bg": f"{ACCENT}0A"},
                ),
                width="100%",
            ),
            # 이벤트 열 (펼쳤을 때만)
            rx.cond(
                DashState.weekly_expanded,
                rx.box(
                    rx.foreach(
                        DashState.weekly_orders,
                        lambda day_orders: rx.box(
                            rx.cond(
                                day_orders.length() == 0,
                                rx.box(rx.text("—", font_size="0.7rem",
                                               color="#CBD5E1", text_align="center"),
                                       padding="14px 6px"),
                                rx.vstack(rx.foreach(day_orders, order_event_card),
                                          spacing="0", align="stretch", padding="4px"),
                            ),
                            flex="1", min_height="80px",
                            border_right=f"1px solid {BORDER_CLR}",
                        ),
                    ),
                    display="flex", gap="0px", width="100%",
                    border=f"1px solid {BORDER_CLR}", border_radius="10px",
                    overflow="hidden", min_height="80px",
                ),
                rx.fragment(),
            ),
            spacing="2",
        ),
        width="100%",
    )


# ════════════════════════════════════════════════════════════════
#  월간 점 달력 (날짜 클릭 가능)
# ════════════════════════════════════════════════════════════════
DOW = ["일", "월", "화", "수", "목", "금", "토"]


def month_cell(cell) -> rx.Component:
    day, cnt, ctype = cell[0], cell[1], cell[2]
    is_ref    = ctype == "today"
    is_expiry = ctype == "expiry"
    is_order  = ctype == "order"
    is_empty  = ctype == "empty"
    selected = (DashState.cal_key == DashState.sel_cal_key) & \
               (DashState.sel_cal_day == day) & (day != "")
    return rx.box(
        rx.cond(
            day != "",
            rx.vstack(
                rx.text(day, font_size="0.78rem",
                        font_weight=rx.cond(is_ref | selected, "700", "400"),
                        color=rx.cond(is_ref, "white",
                              rx.cond(is_expiry, "#92400E", TEXT_PRI))),
                rx.cond(
                    ~is_empty & (cnt != "0"),
                    rx.box(width="5px", height="5px", border_radius="50%",
                           bg=rx.cond(is_expiry, ORANGE, ACCENT_L)),
                    rx.box(width="5px", height="5px"),
                ),
                spacing="0", align="center",
            ),
            rx.fragment(),
        ),
        on_click=DashState.select_cal_day(day),
        cursor=rx.cond(day != "", "pointer", "default"),
        width="40px", height="40px", border_radius="8px",
        display="flex", align_items="center", justify_content="center",
        bg=rx.cond(is_ref, ACCENT,
           rx.cond(selected, f"{ACCENT}1F",
           rx.cond(is_expiry, "#FEF3C7",
           rx.cond(is_order, "rgba(64,145,108,0.08)", "transparent")))),
        border=rx.cond(selected & ~is_ref, f"2px solid {ACCENT}",
               rx.cond(is_expiry, f"1px solid {ORANGE}", "1px solid transparent")),
        transition="all .12s",
        _hover=rx.cond(day != "", {"bg": f"{ACCENT}12"}, {}),
    )


def monthly_calendar() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.text(DashState.cal_month_label, font_size="0.95rem",
                        font_weight="700", color=TEXT_PRI),
                rx.spacer(),
                rx.hstack(
                    rx.box(rx.text("‹", font_size="1.1rem", color=TEXT_SEC),
                           on_click=DashState.prev_month, cursor="pointer",
                           padding="2px 10px", border_radius="6px",
                           border=f"1px solid {BORDER_CLR}",
                           _hover={"bg": "#F1F5F9"}),
                    rx.box(rx.text("›", font_size="1.1rem", color=TEXT_SEC),
                           on_click=DashState.next_month, cursor="pointer",
                           padding="2px 10px", border_radius="6px",
                           border=f"1px solid {BORDER_CLR}",
                           _hover={"bg": "#F1F5F9"}),
                    spacing="2",
                ),
                width="100%", align="center",
            ),
            rx.box(
                *[rx.box(rx.text(d, font_size="0.7rem", font_weight="600",
                                 color=rx.cond(d == "일", "#EF4444",
                                       rx.cond(d == "토", BLUE, TEXT_SEC)),
                                 text_align="center"),
                         width="40px", text_align="center")
                  for d in DOW],
                display="grid", grid_template_columns="repeat(7, 40px)",
                gap="2px", justify_content="center",
            ),
            rx.box(
                rx.foreach(DashState.cal_grid, month_cell),
                display="grid", grid_template_columns="repeat(7, 40px)",
                gap="2px", justify_content="center",
            ),
            rx.divider(border_color=BORDER_CLR),
            rx.hstack(
                rx.hstack(rx.box(width="8px", height="8px", border_radius="50%",
                                 bg=ACCENT_L),
                          rx.text("주문일", font_size="0.68rem", color=TEXT_SEC),
                          spacing="1", align="center"),
                rx.hstack(rx.box(width="8px", height="8px", border_radius="50%",
                                 bg=ORANGE),
                          rx.text("만료예정", font_size="0.68rem", color=TEXT_SEC),
                          spacing="1", align="center"),
                rx.hstack(rx.box(width="10px", height="10px", border_radius="3px",
                                 bg=ACCENT),
                          rx.text("최근 영업일", font_size="0.68rem", color=TEXT_SEC),
                          spacing="1", align="center"),
                spacing="4", justify="center",
            ),
            spacing="3", align="stretch",
        ),
        width="100%",
    )


# ════════════════════════════════════════════════════════════════
#  AI 탭/차트 헬퍼
# ════════════════════════════════════════════════════════════════
def info_box(msg: str) -> rx.Component:
    return rx.box(
        rx.vstack(rx.text("📭", font_size="2rem"),
                  rx.text(msg, color=TEXT_SEC, font_size="0.85rem"),
                  spacing="2", align="center"),
        bg="#F8FAFC", border=f"1px dashed {BORDER_CLR}",
        border_radius="12px", padding="36px", text_align="center", width="100%",
    )


def chart_box(fig, caption: str = "") -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.plotly(data=fig, width="100%", height="380px"),
            rx.cond(caption != "",
                    rx.text(caption, font_size="0.72rem", color=TEXT_SEC),
                    rx.fragment()),
            spacing="1",
        ),
        bg=CARD, border=f"1px solid {BORDER_CLR}", border_radius="14px",
        padding="16px", width="100%",
    )


def str_table(headers: list[str], rows) -> rx.Component:
    return rx.table.root(
        rx.table.header(rx.table.row(
            *[rx.table.column_header_cell(h, color=TEXT_SEC,
                                          font_size="0.73rem", font_weight="600")
              for h in headers])),
        rx.table.body(rx.foreach(rows, lambda row: rx.table.row(
            rx.foreach(row, lambda cell: rx.table.cell(
                cell, font_size="0.8rem", color=TEXT_PRI))))),
        variant="surface", size="1", width="100%",
    )


def mini_stat(label: str, value, color: str) -> rx.Component:
    return rx.box(
        rx.vstack(rx.text(label, font_size="0.72rem", color=TEXT_SEC),
                  rx.text(value, font_size="1.2rem", font_weight="800",
                          color=color),
                  spacing="0", align="start"),
        bg=CARD, border=f"1px solid {BORDER_CLR}", border_radius="10px",
        padding="12px 16px", flex="1",
    )


def table_box(headers, rows) -> rx.Component:
    return rx.box(str_table(headers, rows), bg=CARD,
                  border=f"1px solid {BORDER_CLR}", border_radius="12px",
                  padding="10px")


def tab_revenue() -> rx.Component:
    return rx.cond(
        DashState.has_revenue,
        rx.vstack(
            rx.hstack(
                mini_stat("예측 30일 총매출", DashState.fc_total, ACCENT),
                mini_stat("일평균 예측", DashState.fc_daily, BLUE),
                mini_stat("모델 R²", DashState.fc_r2, ORANGE),
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
            table_box(["상품명", "카테고리", "추천점수", "트렌드", "이유"],
                      DashState.reco_table),
            spacing="3", width="100%", align="stretch",
        ),
        info_box("매입 추천 스코어 계산에 필요한 주문 데이터가 부족합니다."),
    )


def tab_demand() -> rx.Component:
    return rx.cond(
        DashState.has_demand,
        rx.vstack(
            chart_box(DashState.demand_fig, "주간 판매량 LinearRegression 4주 예측"),
            table_box(["상품명", "카테고리", "현재 주간수요", "예측 주간수요", "트렌드"],
                      DashState.demand_table),
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
            table_box(["세그먼트", "고객수", "평균구매횟수", "평균매출"],
                      DashState.segment_table),
            spacing="3", width="100%", align="stretch",
        ),
        info_box("세그멘테이션 고객 수 부족"),
    )


def tab_season() -> rx.Component:
    return rx.cond(
        DashState.has_season,
        rx.vstack(
            chart_box(DashState.season_heat_fig, "카테고리 × 월별 매출 히트맵"),
            chart_box(DashState.season_growth_fig),
            rx.cond(DashState.season_up != "",
                    rx.box(rx.hstack(rx.text("📈", font_size="1rem"),
                            rx.vstack(rx.text("매입 확대 추천", font_size="0.76rem",
                                              font_weight="600", color="#065F46"),
                                      rx.text(DashState.season_up,
                                              font_size="0.8rem", color="#047857"),
                                      spacing="0"), spacing="2"),
                           bg="#ECFDF5", border="1px solid #6EE7B7",
                           border_radius="10px", padding="12px"),
                    rx.fragment()),
            rx.cond(DashState.season_down != "",
                    rx.box(rx.hstack(rx.text("📉", font_size="1rem"),
                            rx.vstack(rx.text("매입 축소 검토", font_size="0.76rem",
                                              font_weight="600", color="#92400E"),
                                      rx.text(DashState.season_down,
                                              font_size="0.8rem", color="#B45309"),
                                      spacing="0"), spacing="2"),
                           bg="#FFFBEB", border="1px solid #FCD34D",
                           border_radius="10px", padding="12px"),
                    rx.fragment()),
            spacing="3", width="100%", align="stretch",
        ),
        info_box("계절성 분석 데이터 부족"),
    )


def recent_item(icon: str, category: str, msg: str, color: str) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.box(rx.text(icon, font_size="0.8rem"),
                   width="26px", height="26px", border_radius="6px",
                   bg=color + "15", display="flex", align_items="center",
                   justify_content="center"),
            rx.vstack(
                rx.hstack(
                    rx.badge(category, size="1", variant="soft",
                             style={"background": color + "18", "color": color}),
                    rx.spacer(),
                    rx.text("방금 전", font_size="0.65rem", color="#94A3B8"),
                    width="100%"),
                rx.text(msg, font_size="0.78rem", color=TEXT_PRI),
                spacing="0"),
            spacing="2", align="start", width="100%"),
        border_bottom=f"1px solid {BORDER_CLR}", padding_y="8px",
    )


# ════════════════════════════════════════════════════════════════
#  페이지 뷰들
# ════════════════════════════════════════════════════════════════
def budget_card() -> rx.Component:
    return section_box(
        section_title("#EEF2FF", "💳", "매출 요약"),
        rx.hstack(
            rx.vstack(rx.text("총 매출", font_size="0.7rem", color=TEXT_SEC),
                      rx.text(DashState.kpi_gmv, font_size="1.05rem",
                              font_weight="700", color=TEXT_PRI), spacing="0"),
            rx.spacer(),
            rx.vstack(rx.text("재구매율", font_size="0.7rem", color=TEXT_SEC),
                      rx.text(DashState.kpi_repurchase, font_size="1.05rem",
                              font_weight="700", color=ACCENT), spacing="0"),
            width="100%"),
        rx.box(rx.box(height="8px", width="65%",
                      bg=f"linear-gradient(90deg,{ACCENT},{ACCENT_L})",
                      border_radius="4px"),
               bg="#E8F4EC", border_radius="4px", height="8px",
               width="100%", overflow="hidden"),
        rx.hstack(
            rx.box(rx.vstack(rx.text("구매 고객", font_size="0.7rem",
                                     color="white", opacity="0.75"),
                             rx.text(DashState.kpi_buyers, font_size="1rem",
                                     font_weight="700", color="white"),
                             spacing="0"),
                   bg=ACCENT, border_radius="10px", padding="10px 14px", flex="1"),
            rx.box(rx.vstack(rx.text("객단가", font_size="0.7rem",
                                     color="white", opacity="0.75"),
                             rx.text(DashState.kpi_aov, font_size="1rem",
                                     font_weight="700", color="white"),
                             spacing="0"),
                   bg=BLUE, border_radius="10px", padding="10px 14px", flex="1"),
            spacing="2", width="100%"),
    )


def hotline_card() -> rx.Component:
    return section_box(
        section_title("#FFF7ED", "📞", "핫라인 관리"),
        rx.hstack(
            rx.box(rx.vstack(rx.text("답변대기", font_size="0.66rem",
                                     color=ORANGE, font_weight="600"),
                             rx.text(DashState.expiry_week, font_size="1.3rem",
                                     font_weight="800", color=ORANGE),
                             spacing="0"),
                   bg="#FFFBEB", border_radius="10px", padding="12px",
                   flex="1", text_align="center"),
            rx.box(rx.vstack(rx.text("오늘 주문", font_size="0.66rem",
                                     color=ACCENT, font_weight="600"),
                             rx.text(DashState.today_orders, font_size="1.3rem",
                                     font_weight="800", color=ACCENT),
                             spacing="0"),
                   bg="#ECFDF5", border_radius="10px", padding="12px",
                   flex="1", text_align="center"),
            spacing="2", width="100%"),
        rx.text("최근 문의내역", font_size="0.75rem", font_weight="600",
                color=TEXT_SEC),
        rx.vstack(
            recent_item("🚚", "배송문의", "배송 가능 날짜가 언제인가요?", BLUE),
            recent_item("📦", "상품문의", "로트 만료 상품 교환 가능한가요?", ORANGE),
            recent_item("💬", "일반문의", "농장 직거래 연락처 알 수 있을까요?", ACCENT),
            spacing="0"),
    )


def dashboard_view() -> rx.Component:
    return rx.vstack(
        page_header("🏠", "관리자홈", "농장 분석 관리"),
        section_title("rgba(27,94,63,0.1)", "📊", "실시간 현황"),
        rx.hstack(
            kpi_small("📥", "최근일 주문", DashState.today_orders),
            kpi_small("⚠️", "7일내 만료", DashState.expiry_week),
            kpi_small("👥", "구매 고객", DashState.kpi_buyers),
            spacing="3", width="100%"),
        rx.hstack(
            kpi_accent("📦", "이번달 주문 수", DashState.kpi_orders,
                       "최근일 기준", "#3B7DD8"),
            kpi_accent("💰", "이번달 매출 (GMV)", DashState.kpi_gmv,
                       DashState.kpi_aov + " 객단가", "#22A55B"),
            kpi_accent("🏷️", "할인 매출", DashState.kpi_deal,
                       DashState.kpi_deal_share + " 비중", NAVY_CARD),
            spacing="3", width="100%"),
        # 공급망 알림 배너 (홈에서 바로 노출)
        rx.cond(
            DashState.has_supply & (DashState.sup_expiry != "0"),
            rx.box(
                rx.hstack(
                    rx.text("🚚", font_size="1.2rem"),
                    rx.vstack(
                        rx.text("공급망 알림", font_size="0.72rem",
                                font_weight="700", color="#92400E"),
                        rx.hstack(
                            rx.text(DashState.sup_expiry, font_weight="800",
                                    color="#B45309"),
                            rx.text("개 품목", font_size="0.82rem", color="#92400E"),
                            rx.text(DashState.sup_waste_won, font_weight="800",
                                    color="#B45309"),
                            rx.text("폐기 위험 · 할인 소진 권장", font_size="0.82rem",
                                    color="#92400E"),
                            spacing="1", align="center",
                        ),
                        spacing="0", align="start",
                    ),
                    rx.spacer(),
                    rx.button("자세히 보기 →", on_click=DashState.set_nav("supply"),
                              bg="#B45309", color="white", size="2",
                              border_radius="8px", cursor="pointer",
                              _hover={"bg": "#92400E"}),
                    width="100%", align="center",
                ),
                bg="#FFFBEB", border="1px solid #FCD34D",
                border_radius="12px", padding="14px 18px", width="100%",
            ),
            rx.fragment(),
        ),
        rx.divider(border_color=BORDER_CLR),
        # 주간 달력 + 당일 매출
        section_title("rgba(59,130,246,0.1)", "📅", "주간 예약·배송 현황 (날짜 클릭 시 당일 매출)"),
        rx.hstack(
            section_box(weekly_calendar()),
            rx.box(daily_detail_card(), width="280px", flex_shrink="0"),
            spacing="4", width="100%", align="start"),
        rx.divider(border_color=BORDER_CLR),
        rx.hstack(budget_card(), hotline_card(),
                  spacing="4", width="100%", align="start"),
        spacing="4", align="stretch", width="100%", padding_bottom="40px",
    )


def calendar_view() -> rx.Component:
    return rx.vstack(
        page_header("🗓️", "일정·배송 달력", "농장 분석 관리"),
        rx.hstack(
            section_box(
                section_title("rgba(59,130,246,0.1)", "📅", "월간 달력"),
                monthly_calendar(),
            ),
            rx.vstack(
                daily_detail_card(),
                section_box(
                    section_title("rgba(245,158,11,0.1)", "⚠️", "이번 주 알림"),
                    rx.hstack(
                        rx.box(rx.vstack(
                            rx.text(DashState.expiry_week, font_size="1.5rem",
                                    font_weight="800", color=ORANGE),
                            rx.text("건 만료 예정", font_size="0.7rem",
                                    color=TEXT_SEC), spacing="0", align="center"),
                            bg="#FFFBEB", border="1px solid #FCD34D",
                            border_radius="10px", padding="12px",
                            flex="1", text_align="center"),
                        rx.box(rx.vstack(
                            rx.text(DashState.today_orders, font_size="1.5rem",
                                    font_weight="800", color=ACCENT),
                            rx.text("최근일 주문", font_size="0.7rem",
                                    color=TEXT_SEC), spacing="0", align="center"),
                            bg="#ECFDF5", border="1px solid #6EE7B7",
                            border_radius="10px", padding="12px",
                            flex="1", text_align="center"),
                        spacing="2", width="100%"),
                ),
                spacing="4", width="320px", flex_shrink="0", align="stretch"),
            spacing="4", width="100%", align="start"),
        # 주간도 함께
        rx.divider(border_color=BORDER_CLR),
        section_box(
            section_title("rgba(27,94,63,0.1)", "🗓️", "주간 상세"),
            weekly_calendar()),
        spacing="4", align="stretch", width="100%", padding_bottom="40px",
    )


def supply_kpi(icon: str, label: str, value, sub: str, bg_color: str) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.box(rx.text(icon, font_size="1.1rem"),
                       bg="rgba(255,255,255,0.15)", border_radius="8px",
                       width="32px", height="32px",
                       display="flex", align_items="center",
                       justify_content="center"),
                rx.spacer(),
            ),
            rx.text(label, font_size="0.78rem",
                    color="rgba(255,255,255,0.8)", font_weight="500"),
            rx.text(value, font_size="1.7rem", font_weight="800", color="white"),
            rx.text(sub, font_size="0.7rem", color="rgba(255,255,255,0.65)"),
            spacing="1", align="start",
        ),
        bg=bg_color, border_radius="14px", padding="16px", flex="1",
        box_shadow=f"0 4px 16px {bg_color}55",
    )


def supply_view() -> rx.Component:
    return rx.vstack(
        page_header("🚚", "공급망·수요 최적화", "운영 최적화"),
        rx.cond(
            DashState.has_supply,
            rx.vstack(
                # 핵심 인사이트 배너
                rx.box(
                    rx.hstack(
                        rx.text("⚠️", font_size="1.3rem"),
                        rx.vstack(
                            rx.text("폐기 위험 재고 알림", font_size="0.82rem",
                                    font_weight="700", color="#92400E"),
                            rx.hstack(
                                rx.text(DashState.sup_expiry, font_weight="800",
                                        color="#B45309"),
                                rx.text("개 품목 ·", font_size="0.85rem",
                                        color="#92400E"),
                                rx.text(DashState.sup_waste_won, font_weight="800",
                                        color="#B45309"),
                                rx.text("규모의 재고가 만료 전 소진되지 못할 것으로 예측됩니다. "
                                        "할인·번들 판매로 손실을 줄이세요.",
                                        font_size="0.82rem", color="#92400E"),
                                spacing="1", align="center", wrap="wrap",
                            ),
                            spacing="0", align="start",
                        ),
                        spacing="3", align="center",
                    ),
                    bg="#FFFBEB", border="1px solid #FCD34D",
                    border_radius="12px", padding="16px", width="100%",
                ),
                # KPI 4종
                rx.hstack(
                    supply_kpi("🔴", "품절 위험", DashState.sup_shortage,
                               "리드타임 내 소진 우려", "#DC2626"),
                    supply_kpi("🟡", "폐기 위험", DashState.sup_expiry,
                               "만료 전 미소진 예상", "#D97706"),
                    supply_kpi("💸", "예상 폐기손실", DashState.sup_waste_won,
                               "할인 미적용 시", NAVY_CARD),
                    supply_kpi("📦", "발주 권장", DashState.sup_reorder,
                               f"목표 재고 2주 기준", BLUE),
                    spacing="3", width="100%",
                ),
                # 소진일수 차트
                section_box(
                    section_title("rgba(27,94,63,0.08)", "📊",
                                  "상품별 재고 소진 예상일수"),
                    chart_box(DashState.supply_fig,
                              "빨강 점선=매입 리드타임(3일), 초록 점선=목표 재고(14일). "
                              "막대가 짧으면 품절 위험, 길면 과잉재고."),
                ),
                # 조치 테이블
                section_box(
                    section_title("rgba(245,158,11,0.08)", "📋",
                                  "상품별 권장 조치"),
                    table_box(
                        ["상품명", "카테고리", "현재고", "일수요",
                         "소진일수", "최단만료", "상태", "권장 조치"],
                        DashState.supply_table),
                ),
                spacing="4", width="100%", align="stretch",
            ),
            info_box("재고(로트) 또는 판매 데이터가 부족해 공급망 분석을 할 수 없습니다."),
        ),
        spacing="4", align="stretch", width="100%", padding_bottom="40px",
    )


def ai_page(icon: str, title: str, badge: str, content) -> rx.Component:
    return rx.vstack(
        page_header(icon, title, "AI 분석·예측"),
        section_box(
            rx.hstack(
                section_title("rgba(27,94,63,0.08)", "🤖", title),
                rx.spacer(),
                rx.badge(badge, color_scheme="green", size="1", variant="surface"),
                width="100%", align="center"),
            content,
        ),
        spacing="4", align="stretch", width="100%", padding_bottom="40px",
    )


# ════════════════════════════════════════════════════════════════
#  📞 핫라인 (고객 응대 현황)
# ════════════════════════════════════════════════════════════════
def status_kpi(icon: str, label: str, value, color: str) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(rx.text(icon, font_size="1rem"),
                      rx.text(label, font_size="0.74rem", color=TEXT_SEC,
                              font_weight="500"),
                      spacing="1", align="center"),
            rx.text(value, font_size="1.6rem", font_weight="800", color=color),
            spacing="1", align="start",
        ),
        bg=CARD, border=f"1px solid {BORDER_CLR}", border_radius="12px",
        padding="16px", flex="1", box_shadow="0 1px 3px rgba(0,0,0,0.04)",
        border_top=f"3px solid {color}",
    )


def hotline_view() -> rx.Component:
    return rx.vstack(
        page_header("📞", "핫라인", "고객 응대 현황"),
        rx.hstack(
            status_kpi("🕐", "접수 대기", DashState.ord_pending, "#F59E0B"),
            status_kpi("✅", "주문 확정", DashState.ord_confirmed, "#3B82F6"),
            status_kpi("🚚", "배송 중", DashState.ord_shipping, "#0EA5E9"),
            status_kpi("📦", "배송 완료", DashState.ord_completed, ACCENT),
            spacing="3", width="100%"),
        rx.hstack(
            section_box(
                section_title("#FFF7ED", "📋", "최근 응대 대기 / 처리 주문"),
                rx.box(
                    str_table(["날짜", "상품", "고객", "수량", "금액", "상태"],
                              DashState.recent_orders_table),
                    max_height="420px", overflow_y="auto", width="100%"),
            ),
            rx.vstack(
                section_box(
                    section_title("#EFF6FF", "💬", "자주 묻는 문의"),
                    rx.vstack(
                        recent_item("🚚", "배송", "배송 예정일이 언제인가요?", BLUE),
                        recent_item("📦", "상품", "신선도/원산지가 궁금해요", ORANGE),
                        recent_item("💳", "결제", "정산은 언제 되나요?", ACCENT),
                        recent_item("🔄", "교환", "상품 교환·환불 절차는?", "#8B5CF6"),
                        spacing="0"),
                ),
                section_box(
                    section_title("#ECFDF5", "📨", "응대 채널"),
                    rx.vstack(
                        rx.hstack(rx.text("☎️ 전화 상담", font_size="0.8rem",
                                          color=TEXT_PRI), rx.spacer(),
                                  rx.badge("09–18시", color_scheme="green",
                                           size="1"), width="100%"),
                        rx.hstack(rx.text("💬 채팅 상담", font_size="0.8rem",
                                          color=TEXT_PRI), rx.spacer(),
                                  rx.badge("운영중", color_scheme="green",
                                           size="1"), width="100%"),
                        rx.hstack(rx.text("✉️ 이메일", font_size="0.8rem",
                                          color=TEXT_PRI), rx.spacer(),
                                  rx.badge("24h 내 회신", color_scheme="gray",
                                           size="1"), width="100%"),
                        spacing="2"),
                ),
                spacing="4", width="300px", flex_shrink="0", align="stretch"),
            spacing="4", width="100%", align="start"),
        spacing="4", align="stretch", width="100%", padding_bottom="40px",
    )


# ════════════════════════════════════════════════════════════════
#  🔔 알림
# ════════════════════════════════════════════════════════════════
def alert_row(a) -> rx.Component:
    sev = a[3]
    sev_color = rx.match(sev, ("긴급", "#DC2626"), ("주의", "#D97706"), "#3B82F6")
    sev_bg = rx.match(sev, ("긴급", "#FEF2F2"), ("주의", "#FFFBEB"), "#EFF6FF")
    return rx.box(
        rx.hstack(
            rx.text(a[0], font_size="1.1rem"),
            rx.vstack(
                rx.hstack(
                    rx.text(a[1], font_size="0.84rem", font_weight="700",
                            color=TEXT_PRI),
                    rx.badge(sev, size="1",
                             style={"background": sev_bg, "color": sev_color}),
                    spacing="2", align="center"),
                rx.text(a[2], font_size="0.76rem", color=TEXT_SEC),
                spacing="0", align="start"),
            spacing="3", align="center", width="100%"),
        bg=CARD, border=f"1px solid {BORDER_CLR}",
        border_left_width="3px", border_left_style="solid",
        border_left_color=sev_color, border_radius="10px",
        padding="12px 14px", width="100%",
    )


def alerts_view() -> rx.Component:
    return rx.vstack(
        page_header("🔔", "알림", "운영 알림 센터"),
        rx.hstack(
            status_kpi("🔔", "전체 알림", DashState.alert_count, ACCENT),
            status_kpi("🔴", "품절 위험", DashState.sup_shortage, "#DC2626"),
            status_kpi("🟡", "폐기 위험", DashState.sup_expiry, "#D97706"),
            status_kpi("💸", "예상 손실", DashState.sup_waste_won, NAVY_CARD),
            spacing="3", width="100%"),
        section_box(
            section_title("rgba(245,158,11,0.1)", "📢", "실시간 운영 알림"),
            rx.cond(
                DashState.alerts_table.length() > 0,
                rx.vstack(rx.foreach(DashState.alerts_table, alert_row),
                          spacing="2", width="100%"),
                info_box("현재 처리할 알림이 없습니다. 👍"),
            ),
        ),
        spacing="4", align="stretch", width="100%", padding_bottom="40px",
    )


# ════════════════════════════════════════════════════════════════
#  🚚 배송 내역
# ════════════════════════════════════════════════════════════════
def delivery_view() -> rx.Component:
    return rx.vstack(
        page_header("🚚", "배송 내역", "주문·배송 관리"),
        rx.hstack(
            status_kpi("🕐", "접수 대기", DashState.ord_pending, "#F59E0B"),
            status_kpi("✅", "주문 확정", DashState.ord_confirmed, "#3B82F6"),
            status_kpi("🚚", "배송 중", DashState.ord_shipping, "#0EA5E9"),
            status_kpi("📦", "배송 완료", DashState.ord_completed, ACCENT),
            spacing="3", width="100%"),
        section_box(
            rx.hstack(
                section_title("rgba(14,165,233,0.1)", "🚚", "전체 주문·배송 내역"),
                rx.spacer(),
                rx.badge(DashState.ord_total + "건", color_scheme="gray", size="1"),
                width="100%", align="center"),
            rx.box(
                str_table(["날짜", "상품", "고객", "수량", "금액", "배송 상태"],
                          DashState.recent_orders_table),
                max_height="540px", overflow_y="auto", width="100%"),
        ),
        spacing="4", align="stretch", width="100%", padding_bottom="40px",
    )


# ════════════════════════════════════════════════════════════════
#  🧾 청구 관리
# ════════════════════════════════════════════════════════════════
def billing_view() -> rx.Component:
    return rx.vstack(
        page_header("🧾", "청구 관리", "주문·배송 관리"),
        rx.hstack(
            kpi_accent("💰", "누적 매출", DashState.bill_total_rev,
                       "전체 기간", "#22A55B"),
            kpi_accent("🏷️", "할인 회수 매출", DashState.bill_total_disc,
                       "원가 대비 할인분", "#3B7DD8"),
            kpi_accent("💵", "정산 예정액", DashState.bill_total_net,
                       "수수료 3.3% 차감", NAVY_CARD),
            spacing="3", width="100%"),
        section_box(
            section_title("rgba(27,94,63,0.08)", "📊", "월별 매출·할인 추이"),
            chart_box(DashState.billing_fig,
                      "녹색=매출, 주황=할인 회수 매출(원가 대비 떨이로 회수한 금액)"),
        ),
        section_box(
            section_title("rgba(27,94,63,0.08)", "🧾", "월별 정산 내역"),
            table_box(["월", "주문", "매출", "할인", "수수료(3.3%)", "정산액"],
                      DashState.billing_table),
        ),
        spacing="4", align="stretch", width="100%", padding_bottom="40px",
    )


# ════════════════════════════════════════════════════════════════
#  📦 보관상품 관리
# ════════════════════════════════════════════════════════════════
def inventory_view() -> rx.Component:
    return rx.vstack(
        page_header("📦", "보관상품 관리", "주문·배송 관리"),
        rx.box(
            rx.hstack(
                rx.text("💡", font_size="1.1rem"),
                rx.text("로트(입고 단위)별 재고와 유통기한을 관리합니다. "
                        "만료 임박(D-3 이내) 상품은 ", font_size="0.82rem",
                        color=TEXT_SEC),
                rx.text("공급망 최적화", font_size="0.82rem", font_weight="700",
                        color=ACCENT, cursor="pointer",
                        on_click=DashState.set_nav("supply")),
                rx.text("에서 할인 소진 전략을 확인하세요.", font_size="0.82rem",
                        color=TEXT_SEC),
                spacing="1", align="center", wrap="wrap"),
            bg="#F0FDF4", border="1px solid #BBF7D0", border_radius="12px",
            padding="14px 18px", width="100%"),
        section_box(
            rx.hstack(
                section_title("rgba(27,94,63,0.08)", "📦", "보관 로트 재고 현황"),
                rx.spacer(),
                rx.badge("만료일 빠른 순", color_scheme="gray", size="1"),
                width="100%", align="center"),
            rx.box(
                str_table(["상품명", "재고", "유통기한", "로트 단가", "상태"],
                          DashState.inventory_table),
                max_height="540px", overflow_y="auto", width="100%"),
        ),
        spacing="4", align="stretch", width="100%", padding_bottom="40px",
    )


# ════════════════════════════════════════════════════════════════
#  📢 공지사항 / 🪟 팝업 / 🔒 보안 / 👤 담당자  (콘텐츠·설정)
# ════════════════════════════════════════════════════════════════
def _placeholder_note() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.text("ℹ️", font_size="0.9rem"),
            rx.text("아래는 예시 데이터입니다. 실제 등록·저장 기능은 전용 테이블"
                    "(공지/팝업/담당자)을 추가하면 연동됩니다.",
                    font_size="0.74rem", color=TEXT_SEC),
            spacing="2", align="center"),
        bg="#F8FAFC", border=f"1px dashed {BORDER_CLR}", border_radius="10px",
        padding="10px 14px", width="100%",
    )


def list_item(left, mid, right_badge, badge_color="gray") -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.vstack(
                rx.text(left, font_size="0.84rem", font_weight="600",
                        color=TEXT_PRI),
                rx.text(mid, font_size="0.72rem", color=TEXT_SEC),
                spacing="0", align="start"),
            rx.spacer(),
            rx.badge(right_badge, color_scheme=badge_color, size="1"),
            width="100%", align="center"),
        border_bottom=f"1px solid {BORDER_CLR}", padding="12px 4px",
    )


def notices_view() -> rx.Component:
    return rx.vstack(
        page_header("📢", "공지사항 관리", "콘텐츠 관리"),
        _placeholder_note(),
        section_box(
            rx.hstack(
                section_title("rgba(59,130,246,0.1)", "📢", "공지사항 목록"),
                rx.spacer(),
                rx.button("+ 새 공지 작성", bg=ACCENT, color="white", size="2",
                          border_radius="8px", cursor="pointer"),
                width="100%", align="center"),
            rx.vstack(
                list_item("[중요] 신선식품 배송 지연 안내 (폭염)",
                          "2026-06-20 · 조회 1,204", "게시중", "green"),
                list_item("여름철 농산물 신선도 보관 가이드",
                          "2026-06-15 · 조회 842", "게시중", "green"),
                list_item("정산 주기 변경 안내 (월 2회 → 주 1회)",
                          "2026-06-01 · 조회 2,310", "게시중", "green"),
                list_item("개인정보 처리방침 개정 안내",
                          "2026-05-20 · 조회 560", "예약", "orange"),
                list_item("[종료] 봄맞이 할인 기획전",
                          "2026-04-10 · 조회 3,120", "종료", "gray"),
                spacing="0"),
        ),
        spacing="4", align="stretch", width="100%", padding_bottom="40px",
    )


def popups_view() -> rx.Component:
    return rx.vstack(
        page_header("🪟", "팝업창 관리", "콘텐츠 관리"),
        _placeholder_note(),
        section_box(
            rx.hstack(
                section_title("rgba(139,92,246,0.1)", "🪟", "팝업 목록"),
                rx.spacer(),
                rx.button("+ 새 팝업 등록", bg=ACCENT, color="white", size="2",
                          border_radius="8px", cursor="pointer"),
                width="100%", align="center"),
            rx.vstack(
                list_item("🍑 제철 복숭아 사전예약 배너",
                          "노출기간 2026-06-18 ~ 06-30 · 메인 상단", "노출중", "green"),
                list_item("🚚 무료배송 프로모션 팝업",
                          "노출기간 2026-06-22 ~ 06-28 · 진입 시 1회", "노출중", "green"),
                list_item("⚠️ 폭염 배송지연 안내 팝업",
                          "노출기간 2026-06-20 ~ 06-25 · 전체", "노출중", "green"),
                list_item("🎁 신규가입 적립 안내",
                          "노출기간 2026-07-01 ~ · 비로그인", "예약", "orange"),
                spacing="0"),
        ),
        spacing="4", align="stretch", width="100%", padding_bottom="40px",
    )


def security_view() -> rx.Component:
    def toggle_row(label, desc, on):
        return rx.box(
            rx.hstack(
                rx.vstack(rx.text(label, font_size="0.84rem", font_weight="600",
                                  color=TEXT_PRI),
                          rx.text(desc, font_size="0.72rem", color=TEXT_SEC),
                          spacing="0", align="start"),
                rx.spacer(),
                rx.badge("ON" if on else "OFF",
                         color_scheme="green" if on else "gray", size="2"),
                width="100%", align="center"),
            border_bottom=f"1px solid {BORDER_CLR}", padding="14px 4px")
    return rx.vstack(
        page_header("🔒", "보안 설정", "설정"),
        _placeholder_note(),
        rx.hstack(
            section_box(
                section_title("rgba(220,38,38,0.08)", "🔐", "계정 보안"),
                toggle_row("2단계 인증 (OTP)", "로그인 시 추가 인증 요구", True),
                toggle_row("비밀번호 90일 변경", "주기적 비밀번호 변경 강제", True),
                toggle_row("접속 IP 제한", "허용된 IP에서만 관리자 접속", False),
            ),
            section_box(
                section_title("rgba(59,130,246,0.08)", "📜", "접속 기록"),
                rx.vstack(
                    list_item("관리자 로그인", "2026-06-22 15:51 · 192.168.0.12",
                              "정상", "green"),
                    list_item("판매 데이터 내보내기", "2026-06-21 10:22 · 본인",
                              "정상", "green"),
                    list_item("로그인 실패 2회", "2026-06-20 08:14 · 14.52.x.x",
                              "주의", "orange"),
                    spacing="0"),
            ),
            spacing="4", width="100%", align="start"),
        spacing="4", align="stretch", width="100%", padding_bottom="40px",
    )


def staff_view() -> rx.Component:
    return rx.vstack(
        page_header("👤", "담당자 관리", "설정"),
        _placeholder_note(),
        section_box(
            rx.hstack(
                section_title("rgba(27,94,63,0.08)", "👤", "담당자 목록"),
                rx.spacer(),
                rx.button("+ 담당자 초대", bg=ACCENT, color="white", size="2",
                          border_radius="8px", cursor="pointer"),
                width="100%", align="center"),
            rx.vstack(
                list_item("김농장 (대표)", "owner@barofarm.kr · 전체 권한",
                          "관리자", "green"),
                list_item("이배송 (배송담당)", "delivery@barofarm.kr · 주문/배송",
                          "운영자", "blue"),
                list_item("박정산 (정산담당)", "billing@barofarm.kr · 청구/정산",
                          "운영자", "blue"),
                list_item("최분석 (데이터)", "analyst@barofarm.kr · 분석 조회",
                          "뷰어", "gray"),
                spacing="0"),
        ),
        spacing="4", align="stretch", width="100%", padding_bottom="40px",
    )


# ════════════════════════════════════════════════════════════════
#  추가 설정 기능 (예정)
# ════════════════════════════════════════════════════════════════
def coming_soon_view(icon: str, title: str, desc: str,
                     features: list) -> rx.Component:
    return rx.vstack(
        page_header(icon, title, "추가 설정 기능 (예정)"),
        rx.box(
            rx.vstack(
                rx.box(rx.text(icon, font_size="2.6rem"),
                       bg="rgba(27,94,63,0.06)", border_radius="20px",
                       padding="18px", margin_bottom="6px"),
                rx.badge("오픈 예정", color_scheme="orange", size="2"),
                rx.text(title, font_size="1.2rem", font_weight="800",
                        color=TEXT_PRI),
                rx.text(desc, font_size="0.86rem", color=TEXT_SEC,
                        text_align="center", max_width="460px"),
                rx.divider(border_color=BORDER_CLR, width="60%"),
                rx.text("제공 예정 기능", font_size="0.74rem", font_weight="700",
                        color=TEXT_SEC),
                rx.vstack(
                    *[rx.hstack(rx.text("✓", color=ACCENT, font_weight="700"),
                                rx.text(f, font_size="0.82rem", color=TEXT_PRI),
                                spacing="2", align="center") for f in features],
                    spacing="2", align="start"),
                spacing="3", align="center",
            ),
            bg=CARD, border=f"1px solid {BORDER_CLR}", border_radius="16px",
            padding="48px", width="100%",
            display="flex", justify_content="center",
            box_shadow="0 1px 4px rgba(0,0,0,0.04)",
        ),
        spacing="4", align="stretch", width="100%", padding_bottom="40px",
    )


# ════════════════════════════════════════════════════════════════
#  메인 라우터
# ════════════════════════════════════════════════════════════════
def main_content() -> rx.Component:
    return rx.box(
        rx.match(
            DashState.active_nav,
            ("dashboard", dashboard_view()),
            ("hotline", hotline_view()),
            ("alerts", alerts_view()),
            ("delivery", delivery_view()),
            ("billing", billing_view()),
            ("inventory", inventory_view()),
            ("calendar", calendar_view()),
            ("supply", supply_view()),
            ("revenue", ai_page("📈", "매출 예측", "Ridge Regression", tab_revenue())),
            ("reco", ai_page("🛒", "매입 추천", "MinMax 가중합", tab_reco())),
            ("demand", ai_page("🔮", "수요 예측", "LinearRegression", tab_demand())),
            ("segment", ai_page("👥", "고객 분석", "RFM + KMeans", tab_segment())),
            ("season", ai_page("📅", "계절성 분석", "월별 집계", tab_season())),
            ("notices", notices_view()),
            ("popups", popups_view()),
            ("security", security_view()),
            ("staff", staff_view()),
            ("members", coming_soon_view("🧑‍🤝‍🧑", "회원 관리",
                "구매 고객을 등급·태그로 관리하고 맞춤 혜택을 운영합니다. "
                "현재 고객 분석(RFM)에서 세그먼트를 미리 확인할 수 있습니다.",
                ["고객 등급/태그 관리", "세그먼트별 타겟 메시지", "구매 이력 통합 조회"])),
            ("sms", coming_soon_view("💬", "문자 관리",
                "주문·배송 알림과 마케팅 문자를 발송하고 결과를 추적합니다.",
                ["주문/배송 자동 알림톡", "단골 대상 캠페인 발송", "발송/클릭 통계"])),
            ("budget", coming_soon_view("💰", "예산 관리",
                "매입·마케팅 예산을 계획하고 집행 현황을 추적합니다. "
                "공급망 최적화의 발주 권장량과 연동될 예정입니다.",
                ["매입 예산 계획/집행", "마케팅 ROI 추적", "월별 손익 시뮬레이션"])),
            ("points", coming_soon_view("🎁", "포인트·기부적립",
                "구매 적립 포인트와 농가 기부 적립을 운영합니다.",
                ["구매 적립/사용 관리", "기부 캠페인 운영", "적립 리포트"])),
            dashboard_view(),
        ),
        padding="20px 28px", flex="1", min_width="0",
        overflow_y="auto", bg=BG,
    )


# ════════════════════════════════════════════════════════════════
#  로딩 / 에러 / 루트
# ════════════════════════════════════════════════════════════════
def loading_screen() -> rx.Component:
    return rx.center(
        rx.vstack(rx.text("🌱", font_size="2.5rem"),
                  rx.spinner(size="3", style={"color": ACCENT}),
                  rx.text("농장 데이터를 불러오는 중…", color=TEXT_SEC,
                          font_size="0.9rem"),
                  spacing="3", align="center"),
        height="100vh", width="100%", bg=BG,
    )


def index() -> rx.Component:
    return rx.box(
        rx.cond(
            DashState.loaded,
            rx.cond(
                DashState.error != "",
                rx.center(
                    rx.box(rx.vstack(rx.text("⚠️", font_size="2rem"),
                                     rx.text(DashState.error, color=TEXT_SEC),
                                     spacing="2", align="center"),
                           bg=CARD, border=f"1px solid {BORDER_CLR}",
                           border_radius="16px", padding="40px"),
                    height="100vh", bg=BG),
                rx.vstack(
                    top_header(),
                    rx.hstack(sidebar(), main_content(),
                              spacing="0", align="start",
                              width="100%", flex="1"),
                    spacing="0", align="stretch",
                    width="100%", min_height="100vh"),
            ),
            loading_screen(),
        ),
        bg=BG, font_family="'Inter', 'Pretendard', sans-serif", width="100%",
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
