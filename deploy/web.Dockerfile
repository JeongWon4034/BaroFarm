# BaroFarm v1 웹 컨테이너 — 프론트(Vue) 정적 빌드 → Caddy로 서빙 + API 프록시 + 자동 HTTPS.
# build context = 레포 루트 (deploy/Caddyfile + frontend/ 둘 다 필요).

# ── 빌드 스테이지: vite build → /dist ──────────────────────────────
FROM node:20-alpine AS build
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ .
# v1에선 분석 대시보드(Streamlit) 미배포 → 메뉴 숨김 + URL 비워 '준비 중'으로 처리
ENV VITE_STREAMLIT_URL=""
ENV VITE_DASHBOARD_ENABLED="false"
RUN npm run build

# ── 서빙 스테이지: Caddy가 dist 서빙 + 프록시 ──────────────────────
FROM caddy:2-alpine
COPY --from=build /app/dist /srv
COPY deploy/Caddyfile /etc/caddy/Caddyfile
EXPOSE 80 443
