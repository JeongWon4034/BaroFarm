# BaroFarm 분석 대시보드 (Reflex)

기존 Streamlit 대시보드(`analytics/dashboard.py`)의 **농장 분석 + AI 예측** 화면을
[Reflex](https://reflex.dev)(순수 파이썬 → React+FastAPI 컴파일)로 이식한 버전.
같은 MySQL을 직접 읽어 농장별 KPI와 5개 ML 예측을 보여주며, Vue 프론트에서
`iframe(?seller_id=X)`으로 임베드한다. **Streamlit(8501)과 병렬로 운영**한다.

## 구조
```
analytics_reflex/
├─ rxconfig.py            # frontend 3001 / backend 8000, cors *, 내부 db=sqlite
├─ requirements.txt       # reflex/pydantic/sqlmodel 호환 핀 + ML 스택
├─ Dockerfile             # python:3.11-slim + reflex init
├─ run_dev.sh             # 로컬 dev 실행 헬퍼 (cd + reflex run)
└─ barofarm/
   ├─ data.py             # ★ 프레임워크 비종속 코어: DB + ML 5종 + plotly Figure 빌더
   ├─ state.py            # rx.State: ?seller_id 해석 → KPI/그림/표 계산
   └─ barofarm.py         # UI: 헤더 + KPI 6종 + rx.tabs 5탭 + app.add_page(on_load)
```
`data.py`는 UI 의존성이 전혀 없어 Streamlit/Reflex 양쪽에서 재사용 가능하다.
ML 로직은 `analytics/dashboard.py`와 동일(Ridge·LinearRegression·KMeans·MinMax/StandardScaler).

## 5개 AI 모듈
1. 📈 **매출 예측** — Ridge + 주간·월간 계절성 → 30일 예측 + ±1σ 신뢰구간
2. 🛒 **매입 추천** — velocity·trend·rev_share·재구매율 MinMax 가중합 Top-10
3. 🔮 **수요 예측** — 상위 8개 상품 주간 LinearRegression → 4주 예측
4. 👥 **고객 세그먼트** — RFM + KMeans(k=4) → VIP/충성/잠재/이탈위험
5. 📅 **계절성** — 카테고리×월 히트맵 + 전월 대비 성장률

## 실행

### Docker (권장 — 스택과 함께)
```bash
# 저장소 루트에서
docker compose -f docker-compose.yml -f docker-compose.reflex.yml up -d --build reflex
# frontend http://localhost:3001  /  backend http://localhost:8000
```
DB는 컨테이너 네트워크의 `mysql` 서비스를 `ANALYTICS_DB_URL`로 주입한다.

### 로컬 (빠른 개발)
```bash
cd analytics_reflex
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
./run_dev.sh          # ANALYTICS_DB_URL 기본값 = 127.0.0.1:3306
```

## 임베드 / 접속
- 농장별: `http://localhost:3001/?seller_id=<판매자 user_id>`
  - `seller_id` 생략 시 GMV 1위 농장으로 폴백
- 예) 테스트농장: `http://localhost:3001/?seller_id=39`

## 의존성 핀 주의
`reflex==0.7.14`의 pydantic-v1 호환 패치가 pydantic 2.11+와 충돌한다. 따라서
`pydantic==2.10.6` + `sqlmodel==0.0.24`(pydantic<2.11 허용)로 고정해야 `import reflex`가 된다.
또한 `ANALYTICS_DB_URL`을 쓰는 이유는 Reflex가 자체 내부 DB 설정으로 `DB_URL`을
읽어버리기 때문(충돌 회피). Reflex 내부 DB는 `rxconfig.py`에서 sqlite로 고정.

## Streamlit → Reflex 전환 경로 (선택)
현재는 **병렬 운영**이라 프론트는 여전히 Streamlit(8501)을 임베드한다.
완전 전환을 원하면 프론트 환경변수만 바꾸면 된다:
```
VITE_STREAMLIT_URL = http://localhost:3001
```
(프론트 `SellerDashboardView.vue` / `AnalyticsView.vue`의 iframe base가 이 값을 사용)
