#!/bin/sh
# 저사양(1GB) AWS 프리티어 전용 기동 스크립트
#
# Reflex 의 next.config 는 output:"export" 라서 프론트엔드가 "완전한 정적 사이트"
# (/app/.web/_static 의 index.html + _next/) 로 빌드된다. 따라서 런타임에 node/
# next 서버가 전혀 필요 없다.
#   - 프론트: 가벼운 python http.server 로 정적 파일만 서빙(메모리 ~15MB)
#   - 백엔드: reflex --backend-only (next build 미수행 → OOM 없음)
# 정적 JS 에는 빌드 시점 REFLEX_API_URL(EC2 퍼블릭 IP:8000)이 박혀 있어
# 브라우저가 백엔드 WebSocket 에 정상 접속한다.
set -e

# 1) 프론트엔드: 정적 export 서빙 — 백그라운드
python -m http.server 3001 --directory /app/.web/_static --bind 0.0.0.0 &

# 2) 백엔드만 기동 — 포그라운드(PID 1). 죽으면 컨테이너 재시작.
cd /app
exec reflex run --env prod --backend-only \
    --backend-host 0.0.0.0 --backend-port 8000
