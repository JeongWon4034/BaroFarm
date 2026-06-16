# FreshGrowth Analytics — 행동로그 시뮬레이션 & Growth 지표

실서비스 트래픽이 없는 상태에서 Layer 2 행동로그(조회·검색·찜·구매)를
**파라메트릭 시뮬레이션**으로 합성하고, 그 위에서 Growth KPI를 계산한다.

> **핵심 입장:** 데이터는 합성이지만, 생성 모델·가정·검증 과정을 전부 공개한다.
> 합성 데이터의 신뢰성은 *데이터 값*이 아니라 *생성 방법의 투명성*에서 나온다.
> 모델 위에서 계산하는 지표는 모두 실제 계산이다 (데이터만 합성, 수치는 실측).

## 생성 방법 (왜 믿을 수 있나)
1. **파라메트릭 모델** — 손으로 행을 쓰거나 LLM으로 찍지 않는다. 전환율·분포·인기도 같은
   소수의 파라미터(`simulate.py`의 `CONFIG`)를 정하고, 확률 추출로 행을 생성한다.
2. **인과 정합** — 차원(users·products) → 행동(events) → 결과(orders·wishlists·reviews)를
   하나의 흐름으로 만들어, 구매 이벤트가 orders 한 줄과 1:1로 맞물린다 (2-Layer 무결성).
3. **재현성** — `seed=42` 고정. 누가 돌려도 같은 데이터.
4. **검증** — 설정한 파라미터가 산출 데이터에서 재현되는지 확인한다.
   예) 딜 구매 배수를 1.8로 설정 → 산출 데이터 실측 ×1.83 (큰 수의 법칙 수렴).
5. **가정 공개** — 모든 파라미터·근거·한계는 [`assumptions.md`](./assumptions.md)에.

## 실행
```bash
pip install -r requirements.txt
python3 simulate.py          # 1) data/ 에 산출물 생성 (재현 가능)
python3 kpi.py               # 2) Growth KPI 콘솔 요약 (검증용)
streamlit run app.py         # 3) Growth 분석 대시보드 (포트폴리오)
uvicorn api:app --port 8000  # 4) Analytics API (Vue 판매자 대시보드용) → /docs
```

## 구성 (단일 분석 엔진)
```
data/ (합성, seed=42)
   │ load_data()
 kpi.py  ── 순수 함수 Growth 지표 엔진 (계산은 여기 한 곳에만)
  ╱        ╲
app.py(Streamlit)   api.py(FastAPI) ──→ Vue 판매자 대시보드
  포트폴리오            인앱 실시간 KPI(JSON)
```
- `kpi.py` — funnel·deal_effect(Z검정)·revenue·repurchase·cohort·category·product. DataFrame in → 지표 out, 차트 없음.
- `app.py` — kpi.py를 직접 import해 Plotly 시각화만 담당.
- `api.py` — kpi.py를 JSON으로 노출. `load_data()`를 DB 로더로 교체하면 엔드포인트 변경 없이 라이브 전환.

## 산출물 (`data/`, git 미추적 — seed로 재생성)
| 파일 | 레이어 | 내용 |
|---|---|---|
| `events.ndjson` | Layer 2 (NoSQL) | 행동로그: search·list_view·detail_view·wishlist·purchase |
| `users.csv` / `products.csv` | Layer 1 (RDB) | 차원 |
| `orders.csv` / `wishlists.csv` / `reviews.csv` | Layer 1 (RDB) | 결과 (이벤트와 정합) |

## KPI (구현 완료 — `kpi.py`)
1. 퍼널 전환율 (조회→상세→구매, 세션 기준)
2. **마감임박 딜 효과** — 딜 vs 정상가 상세→구매 전환율 + 2-비율 Z검정 ⭐ 프로젝트 시그니처
3. GMV / 객단가(AOV) + 일별 시계열
4. 재구매율 / 코호트 리텐션
5. 카테고리·상품별 성과

> 합성 데이터엔 `ab_test_group`이 없어, README §9의 A/B 검정은 **딜(`is_deal`) vs 정상가**
> 2-비율 Z검정으로 구현(딜 효과가 시그니처). 코호트 `week_0`은 "가입 주차 실구매 비율"
> 정의라 100%가 아님(획득 코호트 정의와 다름, 의도된 것).
