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
python3 simulate.py          # data/ 에 산출물 생성 (재현 가능)
```

## 산출물 (`data/`, git 미추적 — seed로 재생성)
| 파일 | 레이어 | 내용 |
|---|---|---|
| `events.ndjson` | Layer 2 (NoSQL) | 행동로그: search·list_view·detail_view·wishlist·purchase |
| `users.csv` / `products.csv` | Layer 1 (RDB) | 차원 |
| `orders.csv` / `wishlists.csv` / `reviews.csv` | Layer 1 (RDB) | 결과 (이벤트와 정합) |

## KPI (계획)
1. 퍼널 전환율 (조회→상세→구매)
2. **마감임박 딜 효과** — 딜 vs 정상가 전환율·판매속도 ⭐ 프로젝트 시그니처
3. GMV / 객단가(AOV)
4. 재구매율 / 리텐션
5. 카테고리·상품별 성과
