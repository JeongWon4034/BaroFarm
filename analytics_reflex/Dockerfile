# BaroFarm 분석 대시보드 (Reflex) — 같은 MySQL 을 읽어 ML 예측을 차트로 보여준다.
# 프론트(Vue)에서 iframe(:3001/?seller_id=X)으로 임베드된다.
FROM python:3.11-slim

# Reflex 가 프론트 빌드 시 bun/node 를 받기 위해 필요한 도구
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl unzip && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 프론트 의존성 미리 초기화(빌드 레이어 캐시)
RUN reflex init --loglevel warning || true

EXPOSE 3001 8000

# dev 모드 실행 — frontend 3001 / backend 8000
CMD ["reflex", "run", "--env", "dev", \
     "--frontend-port", "3001", "--backend-port", "8000"]
