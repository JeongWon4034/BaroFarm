#!/usr/bin/env bash
# 로컬 dev 실행 헬퍼 — analytics_reflex 디렉터리에서 reflex 를 띄운다.
# 분석용 MySQL 은 ANALYTICS_DB_URL 로 주입(Reflex 내부 db_url 환경변수와 충돌 회피).
set -e
cd "$(dirname "$0")"
export ANALYTICS_DB_URL="${ANALYTICS_DB_URL:-mysql+pymysql://root:1234@127.0.0.1:3306/freshgrowth?charset=utf8mb4}"
exec .venv/bin/reflex run --env dev --frontend-port 3001 --backend-port 8000
