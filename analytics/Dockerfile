# BaroFarm 분석 대시보드 (Streamlit) — 같은 MySQL을 읽어 차트로 보여준다.
# 프론트(Vue)에서 iframe(?embed=true)으로 임베드된다.
FROM python:3.11-slim
WORKDIR /app

# 의존성 먼저(레이어 캐시)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 대시보드 + 보조 스크립트
COPY . .

EXPOSE 8501

# iframe 임베드를 위해 CORS/XSRF 비활성(다른 오리진에서 websocket 연결 허용), headless 실행.
CMD ["streamlit", "run", "dashboard.py", \
     "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true", \
     "--server.enableCORS=false", "--server.enableXsrfProtection=false"]
