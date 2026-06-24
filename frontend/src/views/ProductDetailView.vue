<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { productApi } from '../api/products'
import { orderApi } from '../api/orders'
import { useCartStore } from '../stores/cart'
import { useAuthStore } from '../stores/auth'
import { useFollowStore } from '../stores/follow'
import { followApi } from '../api/follow'
import { won, thumbEmoji, categoryLabel, dateOnly, dDayLabel, expiryStatus } from '../utils/format'
import { track } from '../api/track'
import StarRating from '../components/StarRating.vue'

const route = useRoute()
const router = useRouter()
const cart = useCartStore()
const auth = useAuthStore()
const follow = useFollowStore()

const product = ref(null)
const lots = ref([])              // 폐기기간별 옵션
const selectedLot = ref(null)     // 선택한 옵션(없으면 상품 대표가)
const seller = ref(null)
const reviews = ref([])
const loading = ref(true)
const error = ref('')
const qty = ref(1)
const submitting = ref(false)

onMounted(loadAll)
watch(() => route.params.id, loadAll)

async function loadAll() {
  loading.value = true
  error.value = ''
  qty.value = 1
  selectedLot.value = null
  try {
    product.value = await productApi.detail(route.params.id)
    // 리뷰·판매자·폐기기간옵션은 서로 의존이 없어 병렬로 조회
    const [rv, sl, lt] = await Promise.all([
      productApi.reviews(route.params.id).catch(() => []),
      followApi.seller(product.value.sellerId).catch(() => null),
      productApi.lots(route.params.id).catch(() => []),
    ])
    reviews.value = rv
    seller.value = sl
    // 판매 가능(미만료) 옵션만, 임박순 정렬. 기본 선택 = 가장 임박(=할인 큰) 옵션.
    lots.value = (lt || []).filter((l) => l.riskLevel !== 'EXPIRED')
    selectedLot.value = lots.value[0] ?? null
    // 퍼널 3단계 — 상품 상세 조회
    track('view_detail', { productId: product.value.productId, abTestGroup: product.value.abVariant })
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

const emoji = computed(() => (product.value ? thumbEmoji(product.value) : '🥗'))
// 실사진(thumbnailUrl) 우선, 없거나 로드 실패 시 이모지 폴백
const imgError = ref(false)
const showImg = computed(() => !!product.value?.thumbnailUrl && !imgError.value)
watch(() => product.value?.productId, () => { imgError.value = false })
// 가격·재고·유통기한의 권위 = 선택된 lot(있으면), 없으면 상품 대표값
const hasLots = computed(() => lots.value.length > 0)
const active = computed(() => selectedLot.value ?? product.value)
const discRate = computed(() => active.value?.discountRate ?? 0)
const dday = computed(() => active.value?.daysToExpiry)
const basePrice = computed(() => active.value?.price ?? product.value?.price ?? 0)
const expDate = computed(() => active.value?.expirationDate ?? product.value?.expirationDate)
const selStock = computed(() => active.value?.stockQty ?? 0)

const soldOut = computed(() => selStock.value <= 0)
const isExpired = computed(() => active.value?.riskLevel === 'EXPIRED' || (dday.value ?? 0) < 0)
const maxQty = computed(() => Math.max(1, selStock.value))
const hasDeal = computed(() => discRate.value > 0)
const unitPrice = computed(() => active.value?.discountedPrice ?? active.value?.price ?? 0)
const expiry = computed(() => expiryStatus(dday.value)) // 유통기한 상태는 D-day 숫자 기준
const estimated = computed(() => unitPrice.value * qty.value)
const avgRating = computed(() => {
  if (!reviews.value.length) return product.value?.avgRating || 0
  return reviews.value.reduce((s, r) => s + (r.rating || 0), 0) / reviews.value.length
})
// 재고 게이지(시각용): 캐파 정보가 없어 20개 기준으로 환산
const stockPct = computed(() => Math.max(6, Math.min(100, Math.round((selStock.value / 20) * 100))))
const saved = computed(() => Math.max(0, basePrice.value - unitPrice.value))

function selectLot(lot) {
  selectedLot.value = lot
  qty.value = 1
}

function changeQty(delta) {
  qty.value = Math.min(maxQty.value, Math.max(1, qty.value + delta))
}

function onQtyInput(e) {
  const v = parseInt(e.target.value, 10)
  qty.value = isNaN(v) ? 1 : Math.min(maxQty.value, Math.max(1, v))
  e.target.value = qty.value
}

function addToCart() {
  if (isExpired.value) return
  cart.add(product.value, qty.value, selectedLot.value)
  router.push({ name: 'cart' })
}

const sellerName = computed(() => seller.value?.name || product.value?.sellerName || ('판매자 #' + (product.value?.sellerId ?? '')))
const following = computed(() => (product.value ? follow.isFollowing(product.value.sellerId) : false))
const followError = ref('')

async function toggleFollow() {
  if (!auth.isLoggedIn) {
    router.push({ name: 'login', query: { redirect: route.fullPath } })
    return
  }
  followError.value = ''
  const wasFollowing = following.value
  try {
    await follow.toggle(product.value.sellerId)
    if (seller.value) seller.value.followerCount += wasFollowing ? -1 : 1
  } catch (e) {
    followError.value = e.message || '팔로우 처리에 실패했어요. 다시 시도해주세요.'
  }
}

async function buyNow() {
  if (isExpired.value) return
  // 퍼널 4단계 — 결제 시도(로그인 분기 전, 구매 의도 시점)
  track('click_checkout', { productId: product.value.productId, abTestGroup: product.value.abVariant })
  if (!auth.isLoggedIn) {
    router.push({ name: 'login', query: { redirect: route.fullPath } })
    return
  }
  submitting.value = true
  error.value = ''
  try {
    const order = await orderApi.create({
      productId: product.value.productId,
      lotId: selectedLot.value?.lotId ?? null,
      quantity: qty.value,
    })
    router.push({ name: 'order-complete', query: { ids: order.orderId } })
  } catch (e) {
    error.value = e.message
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div v-if="loading" class="empty"><span class="emoji">⏳</span>불러오는 중…</div>
  <div v-else-if="error && !product" class="empty"><span class="emoji">⚠️</span>{{ error }}</div>

  <div v-else-if="product" class="pdp">
    <!-- breadcrumb -->
    <nav class="crumb">
      <router-link :to="{ name: 'products' }">홈</router-link><span class="sep">›</span>
      <router-link :to="{ name: 'products', query: { category: product.category } }">{{ categoryLabel(product.category) }}</router-link><span class="sep">›</span>
      <span>{{ product.name }}</span>
    </nav>

    <div class="pdp-grid">
      <!-- gallery -->
      <div class="gallery">
        <div class="gmain">
          <span v-if="hasDeal" class="disc-big">{{ discRate }}%</span>
          <img v-if="showImg" class="g-photo" :src="product.thumbnailUrl" :alt="product.name" @error="imgError = true" />
          <template v-else>
            <span class="g-emoji">{{ emoji }}</span>
            <span class="ph">상품 사진 자리 · 실사/AI 이미지로 교체</span>
          </template>
        </div>
        <div class="trust">
          <div class="ti"><div class="em">🚚</div><b>당일 산지직송</b><span>내일 도착</span></div>
          <div class="ti"><div class="em">❄️</div><b>신선 콜드체인</b><span>저온 배송</span></div>
          <div class="ti"><div class="em">🛡️</div><b>신선도 보장</b><span>이상 시 환불</span></div>
        </div>
      </div>

      <!-- info -->
      <div class="pinfo">
        <div class="chips">
          <span class="chip">{{ categoryLabel(product.category) }}</span>
          <span v-if="dday != null" class="chip" :class="expiry.cls">{{ expiry.label }}</span>
          <span class="chip muted">산지직송</span>
        </div>
        <h1>{{ product.name }}</h1>

        <div class="seller">
          <span class="loc">🏡 {{ sellerName }}</span>
          <button v-if="auth.isBuyer" class="follow" :class="{ on: following }" @click="toggleFollow">
            {{ following ? '✓ 팔로잉' : '+ 팔로우' }}
          </button>
          <span class="rev">
            <StarRating :rating="avgRating" size="14px" />
            {{ avgRating ? avgRating.toFixed(1) : '-' }} · 후기 {{ reviews.length }}
          </span>
        </div>
        <p v-if="followError" class="err follow-err">{{ followError }}</p>

        <div class="pricebox">
          <div v-if="dday != null && (expiry.cls === 'risk-high' || expiry.cls === 'risk-medium')" class="urgent-strip">
            ⏰ {{ dDayLabel(dday) }} · {{ expiry.label }}
          </div>
          <div class="bigprice">
            <span v-if="hasDeal" class="pct">{{ discRate }}%</span>
            <span class="now">{{ won(unitPrice) }}</span>
            <span v-if="hasDeal" class="was">{{ won(basePrice) }}</span>
          </div>
          <div v-if="hasDeal" class="save">마감임박 할인으로 {{ won(saved) }} 절약 중이에요</div>
        </div>

        <!-- 폐기기간별 가격 옵션 — 클릭해 골라 담는다 -->
        <div v-if="hasLots" class="lots">
          <div class="lots-head">
            ⏰ 가격 확인 <span class="muted">· 임박할수록 더 저렴해요</span>
          </div>
          <button
            v-for="lot in lots"
            :key="lot.lotId"
            class="lot"
            :class="[expiryStatus(lot.daysToExpiry).cls, { sel: selectedLot && selectedLot.lotId === lot.lotId }]"
            @click="selectLot(lot)"
          >
            <span class="lot-dday">{{ dDayLabel(lot.daysToExpiry) }}</span>
            <span class="lot-exp">유통기한 {{ dateOnly(lot.expirationDate) }}</span>
            <span class="lot-prices">
              <span class="lot-now">{{ won(lot.discountedPrice ?? lot.price) }}</span>
              <span v-if="(lot.discountRate ?? 0) > 0" class="lot-pct">{{ lot.discountRate }}%</span>
            </span>
            <span class="lot-stock" :class="{ low: (lot.stockQty ?? 0) <= 5 }">
              {{ (lot.stockQty ?? 0) <= 0 ? '품절' : '재고 ' + lot.stockQty }}
            </span>
            <span class="lot-check">{{ selectedLot && selectedLot.lotId === lot.lotId ? '✓' : '' }}</span>
          </button>
        </div>

        <p v-if="product.description" class="desc">{{ product.description }}</p>

        <div class="meta-list">
          <div class="ml">
            <span>재고</span>
            <b :class="{ hot: selStock <= 5 }">{{ selStock <= 5 ? '단 ' + selStock + '개 남음' : selStock + '개' }}</b>
            <div class="gauge"><i :style="{ width: stockPct + '%' }"></i></div>
          </div>
          <div class="ml"><span>배송</span><b>산지직송 · 내일 도착 예정</b></div>
          <div v-if="expDate" class="ml"><span>유통기한</span><b>{{ dateOnly(expDate) }}<span v-if="hasLots" class="muted sm"> · 선택한 옵션</span></b></div>
          <div class="ml"><span>분류</span><b>{{ categoryLabel(product.category) }} · 냉장</b></div>
        </div>

        <div class="buybar">
          <div class="qtybox">
            <button @click="changeQty(-1)" :disabled="qty <= 1">−</button>
            <input
              type="number" class="q"
              :value="qty" :min="1" :max="maxQty"
              @change="onQtyInput"
            />
            <button @click="changeQty(1)" :disabled="qty >= maxQty">+</button>
          </div>
          <div class="sub">결제 예정<b>{{ won(estimated) }}</b></div>
        </div>

        <p v-if="error" class="err">{{ error }}</p>
        <p v-if="isExpired" class="expired-notice">⛔ 유통기한이 지나 판매가 종료된 상품입니다.</p>

        <div class="cta-row">
          <button class="btn btn-outline" :disabled="soldOut || isExpired" @click="addToCart">🧺 장바구니 담기</button>
          <button class="btn btn-accent" :disabled="soldOut || isExpired || submitting" @click="buyNow">
            {{ isExpired ? '판매종료' : soldOut ? '품절' : (submitting ? '처리 중…' : '💳 결제하기') }}
          </button>
        </div>
      </div>
    </div>

    <!-- reviews -->
    <section class="reviews">
      <h2 class="reviews-title">💬 구매 리뷰 <span class="muted">({{ reviews.length }})</span></h2>
      <div v-if="reviews.length === 0" class="empty"><span class="emoji">📝</span>아직 리뷰가 없어요.</div>
      <ul v-else class="review-list">
        <li v-for="r in reviews" :key="r.reviewId" class="review-item">
          <div class="review-head">
            <span class="r-ava">{{ (r.buyerName || '구')[0] }}</span>
            <strong>{{ r.buyerName || '구매자' }}</strong>
            <StarRating :rating="r.rating" />
            <span class="muted sm">{{ dateOnly(r.createdAt) }}</span>
          </div>
          <p class="review-body">{{ r.content }}</p>
        </li>
      </ul>
    </section>
  </div>
</template>

<style scoped>
.pdp { padding: 4px 0 40px; }
.crumb { display: flex; gap: 8px; align-items: center; font-size: 13px; color: var(--muted); margin-bottom: 22px; flex-wrap: wrap; }
.crumb span { white-space: nowrap; }
.crumb .sep { color: var(--faint); }
.crumb a:hover { color: var(--leaf-700); }

.pdp-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 40px; align-items: start; }

/* gallery */
.gallery { position: sticky; top: 130px; display: flex; flex-direction: column; gap: 14px; }
.gmain { position: relative; aspect-ratio: 4/3; border-radius: 22px; border: 1px solid var(--line); display: flex; align-items: center; justify-content: center; overflow: hidden; background: radial-gradient(circle at 50% 36%, var(--leaf-50), var(--leaf-100)); }
.gmain .g-emoji { font-size: 150px; filter: drop-shadow(0 20px 26px rgba(40,40,20,.18)); }
.gmain .g-photo { width: 100%; height: 100%; object-fit: cover; }
.gmain .disc-big { position: absolute; top: 18px; left: 18px; background: var(--deal); color: #fff; font-weight: 800; font-size: 18px; padding: 6px 14px; border-radius: 12px; box-shadow: 0 8px 16px rgba(214,69,47,.3); }
.gmain .ph { position: absolute; bottom: 16px; right: 16px; font-size: 12px; color: var(--muted); background: rgba(255,255,255,.75); padding: 3px 10px; border-radius: 6px; }
.trust { display: flex; gap: 10px; }
.trust .ti { flex: 1; background: #fff; border: 1px solid var(--line); border-radius: 13px; padding: 13px 10px; text-align: center; box-shadow: var(--shadow-sm); }
.trust .ti .em { font-size: 21px; }
.trust .ti b { display: block; font-size: 13px; margin-top: 5px; }
.trust .ti span { font-size: 11px; color: var(--muted); }

/* info */
.pinfo { display: flex; flex-direction: column; gap: 16px; }
.chips { display: flex; gap: 6px; flex-wrap: wrap; }
.chip { font-size: 11.5px; font-weight: 600; padding: 3px 9px; border-radius: 7px; background: var(--leaf-50); color: var(--leaf-700); white-space: nowrap; }
.chip.muted { background: #f1f1ea; color: var(--muted); }
.chip.risk-high { background: var(--deal-soft); color: var(--deal); }
.chip.risk-medium { background: var(--gold-soft); color: var(--gold); }
.chip.risk-expired { background: #ececec; color: #888; }
.pinfo h1 { font-size: 30px; font-weight: 800; letter-spacing: -.025em; margin: 6px 0 0; line-height: 1.25; }

.seller { display: flex; align-items: center; gap: 12px; font-size: 14px; color: var(--ink-2); flex-wrap: wrap; }
.seller .loc { display: flex; align-items: center; gap: 5px; font-weight: 600; }
.seller .follow { border: 1.5px solid var(--leaf-500); color: var(--leaf-700); background: var(--leaf-50); font-weight: 700; font-size: 12.5px; padding: 5px 12px; border-radius: 999px; }
.seller .follow.on { background: var(--leaf-600); color: #fff; border-color: var(--leaf-600); }
.seller .rev { display: inline-flex; align-items: center; gap: 5px; color: var(--muted); font-size: 13px; }
.follow-err { color: var(--deal); font-size: 13px; margin: -8px 0 0; }

.pricebox { background: var(--cream); border: 1px solid var(--line); border-radius: 18px; padding: 20px; }
.urgent-strip { display: flex; align-items: center; gap: 10px; background: #23281c; color: #fff; font-weight: 700; font-size: 14px; padding: 9px 14px; border-radius: 11px; margin-bottom: 16px; width: fit-content; }
.bigprice { display: flex; align-items: baseline; gap: 12px; flex-wrap: wrap; }
.bigprice .pct { color: var(--deal); font-weight: 800; font-size: 30px; }
.bigprice .now { font-weight: 800; font-size: 36px; letter-spacing: -.03em; }
.bigprice .was { color: var(--faint); text-decoration: line-through; font-size: 18px; }
.save { margin-top: 8px; color: var(--leaf-700); font-weight: 600; font-size: 13.5px; }

/* 폐기기간별 가격 옵션 */
.lots { display: flex; flex-direction: column; gap: 8px; }
.lots-head { font-size: 14px; font-weight: 800; color: var(--ink); }
.lots-head .muted { font-weight: 500; color: var(--muted); font-size: 12.5px; }
.lot {
  display: grid; grid-template-columns: 64px 1fr auto 70px 18px; align-items: center; gap: 12px;
  width: 100%; text-align: left; background: #fff; border: 1.5px solid var(--line-2);
  border-radius: 13px; padding: 12px 14px; cursor: pointer; transition: .14s;
}
.lot:hover { border-color: var(--leaf-500); background: var(--leaf-50); }
.lot.sel { border-color: var(--ink); background: var(--cream); box-shadow: var(--shadow-sm); }
.lot-dday { font-weight: 800; font-size: 14px; padding: 4px 8px; border-radius: 8px; text-align: center; background: #eef1ea; color: var(--muted); }
.lot.risk-high .lot-dday { background: var(--deal-soft); color: #bd3a26; }
.lot.risk-medium .lot-dday { background: var(--gold-soft); color: #9a6a1c; }
.lot-exp { font-size: 12.5px; color: var(--muted); }
.lot-prices { display: inline-flex; align-items: baseline; gap: 6px; justify-self: end; }
.lot-now { font-weight: 800; font-size: 18px; letter-spacing: -.02em; }
.lot-pct { color: var(--deal); font-weight: 800; font-size: 13px; }
.lot-stock { font-size: 12px; color: var(--muted); text-align: right; }
.lot-stock.low { color: var(--deal); font-weight: 700; }
.lot-check { color: var(--leaf-700); font-weight: 900; font-size: 15px; text-align: center; }

.desc { line-height: 1.7; color: var(--ink-2); font-size: 15px; margin: 0; }

.meta-list { display: flex; flex-direction: column; border: 1px solid var(--line); border-radius: 14px; overflow: hidden; }
.meta-list .ml { display: flex; align-items: center; gap: 14px; padding: 13px 16px; font-size: 14.5px; border-bottom: 1px solid var(--line); }
.meta-list .ml:last-child { border-bottom: none; }
.meta-list .ml > span { color: var(--muted); width: 58px; flex: none; }
.meta-list .ml b { color: var(--ink); font-weight: 700; }
.meta-list .ml b.hot { color: var(--deal); }
.meta-list .ml .gauge { height: 6px; border-radius: 4px; background: var(--line); overflow: hidden; width: 120px; margin-left: auto; }
.meta-list .ml .gauge i { display: block; height: 100%; background: var(--deal); }

.buybar { display: flex; align-items: center; justify-content: space-between; padding: 4px 2px; }
.qtybox { display: inline-flex; align-items: center; border: 1.5px solid var(--line-2); border-radius: 12px; overflow: hidden; background: #fff; }
.qtybox button { width: 42px; height: 46px; border: none; background: #fff; font-size: 20px; color: var(--ink-2); }
.qtybox button:hover:not(:disabled) { background: var(--leaf-50); color: var(--leaf-700); }
.qtybox button:disabled { opacity: .35; }
.qtybox .q {
  width: 48px; text-align: center; font-weight: 700; font-size: 17px;
  font-variant-numeric: tabular-nums; border: none; outline: none;
  background: transparent; -moz-appearance: textfield;
}
.qtybox .q::-webkit-inner-spin-button,
.qtybox .q::-webkit-outer-spin-button { -webkit-appearance: none; margin: 0; }
.buybar .sub { font-size: 15px; color: var(--muted); }
.buybar .sub b { font-size: 24px; font-weight: 800; color: var(--ink); letter-spacing: -.02em; margin-left: 6px; }

.err { color: var(--deal); font-size: 14px; margin: 0; }
.expired-notice { color: #c0392b; background: var(--deal-soft); border-radius: var(--r-btn); padding: 10px 14px; font-size: 14px; font-weight: 600; margin: 0; }
.cta-row { display: flex; gap: 11px; }
.cta-row .btn { flex: 1; padding: 16px; font-size: 16px; }

.reviews { margin-top: 48px; }
.reviews-title { font-size: 20px; font-weight: 800; border-top: 1px solid var(--line); padding-top: 26px; margin-bottom: 16px; }
.review-list { display: flex; flex-direction: column; gap: 12px; list-style: none; margin: 0; padding: 0; }
.review-item { background: #fff; border: 1px solid var(--line); border-radius: 14px; padding: 16px 18px; box-shadow: var(--shadow-sm); }
.review-head { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.r-ava { width: 30px; height: 30px; border-radius: 50%; background: var(--leaf-100); color: var(--leaf-700); font-weight: 800; font-size: 13px; display: flex; align-items: center; justify-content: center; flex: none; }
.review-head strong { font-size: 14.5px; }
.review-head .sm { font-size: 12.5px; margin-left: auto; }
.review-body { margin: 0; color: var(--ink-2); line-height: 1.6; font-size: 14.5px; }

@media (max-width: 900px) {
  .pdp-grid { grid-template-columns: 1fr; gap: 26px; }
  .gallery { position: static; }
}
</style>
