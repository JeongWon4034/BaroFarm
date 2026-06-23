# BaroFarm 프론트엔드 — 디자인 핸드오프 계약서

> 새 `.vue` 화면/컴포넌트를 만들 때 **반드시 이 계약을 지킬 것.** 백엔드는 손대지 않으며,
> 프론트는 아래 API·스토어·토큰·기존 컴포넌트와 정확히 맞물려야 빈 화면/빌드붕괴가 안 난다.

## 0. 스택 / 전제
- **Vue 3 `<script setup>`** + **Pinia**(스토어) + **vue-router** + **axios**(`api/http.js` 경유).
- CSS 프레임워크 없음 → **컴포넌트 `<style scoped>` + 전역 토큰**(`assets/styles.css`)만 사용. Tailwind/부트스트랩 금지.
- 폰트 Pretendard. 색·간격·라운드·그림자는 **CSS 변수 토큰만** 사용(하드코딩 색 최소화).
- 새 컴포넌트는 `frontend/src/components/`, 새 화면은 `frontend/src/views/`. import 경로는 거기 기준 상대경로.

## 1. HTTP / API 계약 (가장 중요)
모든 호출은 `api/*.js`의 래퍼를 통해서 한다. **직접 axios/fetch 쓰지 말 것.**
- baseURL = **`/api/v1`** (Vite가 `/api`를 백엔드로 프록시).
- JWT는 `localStorage('token')`에서 **자동 부착**됨(직접 헤더 X).
- 백엔드 응답 봉투 `{ success, message, data, error }` 는 **인터셉터가 자동으로 벗겨서 `data`만 반환**.
  → `const x = await productApi.list()` 하면 `x`가 **이미 `data`** 다. `x.data.content` ❌ / `x.content` ✅.
- 실패 시 reject되며 `err.message`(상세) + `err.code`. **401이면 자동 로그아웃 처리**되니, 인증 필요한 화면은 비로그인 시 빈 데이터로 graceful 하게.

### 사용 가능한 API (이미 존재 — 새로 만들지 말 것)
```
productApi  (api/products.js)
  list(params)            GET  /products        params {page,size}  → Page{content[],totalPages,totalElements,number,size}
  detail(id)              GET  /products/{id}
  lots(id)                GET  /products/{id}/lots         폐기기간 옵션[]
  reviews(id)             GET  /products/{id}/reviews
  sellerProducts()        GET  /seller/products            (SELLER)
  create / update / remove                                  (SELLER)
  priceSuggestion(name,category)  GET /products/ai/price-suggestion
  generateDescription(payload)    POST /products/ai/description
  sellerReport()          GET  /products/ai/seller-report  (SELLER)

orderApi   (api/orders.js)
  create({productId,quantity})  POST /orders
  myOrders()              GET  /orders/my
  detail(orderId)         GET  /orders/{id}
  insight()               GET  /orders/ai/insight          내 구매 AI 인사이트
  sellerOrders()          GET  /seller/orders              (SELLER)
  updateStatus(orderId,status)  PATCH /seller/orders/{id}/status
reviewApi.create({orderId,rating,content})  POST /reviews

authApi    (api/auth.js)   signup / login / logout / me / updateProfile / deactivate
challengeApi (api/challenges.js)  list / detail(id) / join(id) / myChallenges
couponApi.myCoupons()      GET /coupons
postApi / commentApi (api/posts.js)  게시판 CRUD + trend()
followApi  (api/follow.js)  follow / unfollow / following / seller(id)
wishlistApi (api/wishlist.js)  list / add(productId) / remove(productId)
track(eventType, {productId})  행동로그 fire-and-forget — 실패 무시. view_home|click_product|view_detail|click_checkout|complete_order
```

## 2. 데이터 모델 (실제 필드명 — camelCase)
**Product** (목록/상세 아이템):
```
productId, sellerId, name, description, category, price, stockQty,
thumbnailUrl, expirationDate,
// 떨이 엔진이 채워주는 파생 필드:
riskLevel('HIGH'|'MEDIUM'|'LOW'|'EXPIRED'), daysToExpiry(숫자),
discountRate(%), discountedPrice, lotCount,
avgRating, reviewCount, abVariant
```
- `id`/`product_id` 아님 → **`productId`**. snake_case 절대 금지.
- **category 코드**: `vegetable` `fruit` `seafood` `meat` `grain` `mushroom` `root` `processed`
  (한글 라벨은 `categoryLabel(code)` 사용).

**Lot(폐기기간 옵션)**: `lotId, price, discountedPrice, discountRate, stockQty, expirationDate, daysToExpiry`
**User**: `userId, role('BUYER'|'SELLER'), email, name, intro, phone`
**Order**: `orderId, status, ...` / **Coupon·Challenge·Post**: 목록 API 응답 그대로 바인딩.

## 3. Pinia 스토어 (import해서 그대로 사용)
```
useCartStore  (stores/cart.js)   장바구니(로컬)
  state.items[]  getters: count, totalPrice
  add(product, qty=1, lot=null) / updateQty(key,qty) / remove(key) / clear()
useAuthStore  (stores/auth.js)
  getters: isLoggedIn, isSeller, isBuyer   state: user{userId,role,name,...}, token
  login(payload) / logout() / signup() / validate()
useWishlistStore (stores/wishlist.js)  ids[], isWished(productId), toggle(productId), load()
useFollowStore   (stores/follow.js)    ids[], (팔로우 상태)
useNotificationStore (stores/notification.js)  주문 알림 뱃지
```

## 4. 라우터 (`router/index.js`) — `<router-link :to="{name:'...'}">` 로만 이동
기존 route name(이미 등록됨): `products`(/), `deals`, `challenges`, `challenge-detail`,
`board`, `board-detail`, `product-detail`(params{id}), `cart`, `order-complete`,
`wishlist`*, `following`*, `my-hub`*, `mypage`*, `purchase-insights`*, `my-coupons`*,
`seller-center`*‡, `seller-dashboard`*‡, `seller-products`*‡, `seller-orders`*‡,
`login`, `signup`   (`*`=로그인 필요 meta.auth, `‡`=SELLER 필요 meta.seller)
- **새 화면을 추가하면 route를 직접 등록해야 함** → 내(이도연)가 `router/index.js`에 줄 추가. 새 name은 기존과 겹치지 않게.

## 5. 재사용 컴포넌트 (새로 만들지 말고 import)
```
ProductCard.vue   props: { product: Object(required) }   emits: 'add'(product)
                  → <ProductCard :product="p" @add="cart.add($event)" />
StarRating.vue    props: { rating, size }
utils/format.js   won(원화), thumbEmoji(product), categoryLabel(code), dDayLabel(days),
                  dateOnly(v), riskMeta(level)→{cls,label}, apiMessage(e), orderStatusMeta(s)
```

## 6. 디자인 토큰 — `assets/styles.css` (★ 통째 교체 금지, **머지**)
새 시안 색/타이포/간격은 **아래 `:root` 토큰 값을 갱신/추가**하는 방식으로. 특히 **`--color-*` 별칭 레이어는 유지**(28개 화면이 의존). 유틸 클래스명 `.btn .badge .card .input .empty .container`도 그대로 둘 것.
```css
:root{
  /* 브랜드 — 딥 포레스트 그린(유지 권장: 톤 핵심) */
  --leaf-700:#0e4a2e; --leaf-600:#176b42; --leaf-500:#2a8a5a; --leaf-400:#5aa982;
  --leaf-300:#93c9ac; --leaf-100:#dcefe4; --leaf-50:#eef7f1;
  /* 중립 */ --ink:#1c2215; --ink-2:#3e4736; --muted:#7c8470; --faint:#a2a899;
  --line:#e9eae1; --line-2:#dcdecf; --paper:#fff; --cream:#f6f8f6;
  /* 강조(마감임박/가격) */ --deal:#d6452f; --deal-soft:#fbe7e1; --gold:#c1872b; --gold-soft:#f6ecd5; --star:#f5b50a;
  /* 호환 별칭 — 삭제·이름변경 금지 */
  --color-primary:var(--leaf-600); --color-primary-dark:var(--leaf-700); --color-primary-soft:var(--leaf-100);
  --color-accent:var(--deal); --color-bg:var(--cream); --color-card:var(--paper);
  --color-text:var(--ink); --color-muted:var(--muted); --color-border:var(--line); --color-star:var(--star);
  /* 형태 */ --r-card:18px; --r-btn:11px; --radius:var(--r-card); --radius-sm:var(--r-btn);
  --shadow-sm:0 1px 2px rgba(28,34,21,.06),0 1px 3px rgba(28,34,21,.05);
  --shadow-md:0 6px 16px rgba(28,34,21,.08),0 2px 5px rgba(28,34,21,.05);
  --shadow-lg:0 18px 40px rgba(28,34,21,.13),0 6px 14px rgba(28,34,21,.07);
  --maxw:1240px;
}
```
유틸 클래스: `.btn`(+`.btn-primary/.btn-accent/.btn-outline/.btn-block`), `.badge`(+`.badge-accent`),
`.card`, `.field/.input/.select`, `.empty`(+`.empty .emoji`), `.container`(max 1240·좌우 28px), `.muted`.

## 7. 가드레일 (이거 어기면 화면 깨짐)
1. **import 경로 정확히** — 없는 파일/오타 import 하나면 Vite가 **사이트 전체**를 못 띄움(흰 화면). 새로 만드는 자식 컴포넌트는 같은 PR에 포함.
2. **필드명은 camelCase 실제값** (`productId`, `stockQty`, `discountedPrice` …). 추측 금지 — 위 모델만 사용.
3. **응답은 이미 unwrap**됨 — `res.content`지 `res.data.content` 아님. 목록은 Spring Page 형태.
4. **styles.css는 머지**(별칭·유틸 클래스명 유지), 통째 교체 금지.
5. **인증 데이터는 비로그인/401 graceful** — 빈 배열·플레이스홀더로. 에러로 화면 안 죽이기.
6. 정적 더미 대신 **API 바인딩**(`v-for`, `computed`). 카운트다운/모션은 `onMounted`+`ref`+`setInterval`(+`onBeforeUnmount` cleanup).
7. **새 route name은 직접 router 등록 필요**하다고 알려줄 것(나(이도연)가 추가).
```
