import os
import reflex as rx

# REFLEX_API_URL: 브라우저가 백엔드 WebSocket에 닿는 공개 주소
#   로컬: http://localhost:8000 (기본값)
#   AWS EC2: http://<EC2_PUBLIC_IP>:8000  (docker-compose.aws.yml 에서 주입)
_api_url = os.getenv("REFLEX_API_URL", "http://localhost:8000")

config = rx.Config(
    app_name="barofarm",
    frontend_port=3001,
    backend_port=8000,
    api_url=_api_url,
    cors_allowed_origins=["*"],
    telemetry_enabled=False,
    tailwind=None,
    db_url="sqlite:///reflex.db",
)
