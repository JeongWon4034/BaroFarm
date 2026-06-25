import reflex as rx

# BaroFarm 분석 대시보드 (Reflex)
#   frontend 3001 / backend 8000.  프론트(Vue)에서 iframe 으로 :3001/?seller_id=X 임베드.
#   api_url 은 브라우저가 직접 닿는 백엔드 주소여야 함(iframe 도 사용자 브라우저에서 로드되므로 localhost).
config = rx.Config(
    app_name="barofarm",
    frontend_port=3001,
    backend_port=8000,
    api_url="http://localhost:8000",
    cors_allowed_origins=["*"],
    telemetry_enabled=False,
    tailwind=None,                    # radix 테마만 사용 → tailwind 추론 경고 제거
    db_url="sqlite:///reflex.db",     # Reflex 내부 DB는 sqlite 고정(분석용 MySQL 과 분리)
)
