<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { productApi } from '../api/products'
import { orderApi } from '../api/orders'
import { useCartStore } from '../stores/cart'
import { useAuthStore } from '../stores/auth'
import { won, thumbEmoji, categoryLabel, dateOnly } from '../utils/format'
import StarRating from '../components/StarRating.vue'

const route = useRoute()
const router = useRouter()
const cart = useCartStore()
const auth = useAuthStore()

const product = ref(null)
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
  try {
    product.value = await productApi.detail(route.params.id)
    reviews.value = await productApi.reviews(route.params.id).catch(() => [])
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

const emoji = computed(() => (product.value ? thumbEmoji(product.value) : '🥗'))
const soldOut = computed(() => (product.value?.stockQty ?? 0) <= 0)
const maxQty = computed(() => product.value?.stockQty ?? 1)
const estimated = computed(() => (product.value ? product.value.price * qty.value : 0))
const avgRating = computed(() => {
  if (!reviews.value.length) return product.value?.averageRating || 0
  return reviews.value.reduce((s, r) => s + (r.rating || 0), 0) / reviews.value.length
})

function changeQty(delta) {
  qty.value = Math.min(maxQty.value, Math.max(1, qty.value + delta))
}

function addToCart() {
  cart.add(product.value, qty.value)
  router.push({ name: 'cart' })
}

async function buyNow() {
  if (!auth.isLoggedIn) {
    router.push({ name: 'login', query: { redirect: route.fullPath } })
    return
  }
  submitting.value = true
  error.value = ''
  try {
    const order = await orderApi.create({ productId: product.value.productId, quantity: qty.value })
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

  <div v-else-if="product">
    <router-link :to="{ name: 'products' }" class="back muted">← 상품 목록으로</router-link>

    <div class="detail">
      <!-- 썸네일 -->
      <div class="thumb card">
        <span class="emoji">{{ emoji }}</span>
        <div class="thumb-badges">
          <span class="badge">{{ categoryLabel(product.category) }}</span>
          <span v-if="product.expirationDate" class="badge badge-accent">유통기한 {{ dateOnly(product.expirationDate) }}</span>
        </div>
      </div>

      <!-- 정보 + 결제 -->
      <div class="info">
        <h1 class="name">{{ product.name }}</h1>
        <p class="seller muted">판매자: 🏡 {{ product.sellerName || '판매자 #' + product.sellerId }}</p>
        <p class="rate">
          평점: <StarRating :rating="avgRating" size="16px" />
          <strong>{{ avgRating ? avgRating.toFixed(1) : '-' }}</strong>
          <span class="muted">| 리뷰 {{ reviews.length }}개</span>
        </p>

        <p v-if="product.description" class="desc">{{ product.description }}</p>

        <hr class="divider" />

        <div class="price-row">
          <div>
            <div class="muted sm">판매가격</div>
            <div class="big-price">{{ won(product.price) }}</div>
          </div>
          <div class="stock">
            <div class="muted sm">현재 재고</div>
            <div class="stock-val" :class="{ low: maxQty <= 5 }">{{ product.stockQty }}개</div>
          </div>
        </div>

        <div class="ship card">
          🚚 산지 직송 — 주문 후 24시간 내 발송<br />
          📦 택배: 무료 (3만원 이상) · 냉장 포장 제공
        </div>

        <div class="qty-row">
          <span class="qty-label">수량</span>
          <div class="stepper">
            <button @click="changeQty(-1)" :disabled="qty <= 1">−</button>
            <span class="qty-val">{{ qty }}</span>
            <button @click="changeQty(1)" :disabled="qty >= maxQty">+</button>
          </div>
        </div>

        <p class="estimated">결제 예정 금액: <span class="price">{{ won(estimated) }}</span></p>

        <p v-if="error" class="err">{{ error }}</p>

        <div class="actions">
          <button class="btn btn-outline" :disabled="soldOut" @click="addToCart">🧺 장바구니 담기</button>
          <button class="btn btn-accent" :disabled="soldOut || submitting" @click="buyNow">
            {{ soldOut ? '품절' : (submitting ? '처리 중…' : '💳 결제하기') }}
          </button>
        </div>
      </div>
    </div>

    <!-- 리뷰 -->
    <section class="reviews">
      <h2 class="reviews-title">💬 구매 리뷰 <span class="muted">({{ reviews.length }})</span></h2>
      <div v-if="reviews.length === 0" class="empty"><span class="emoji">📝</span>아직 리뷰가 없어요.</div>
      <ul v-else class="review-list">
        <li v-for="r in reviews" :key="r.reviewId" class="review-item card">
          <div class="review-head">
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
.back { display: inline-block; margin-bottom: 16px; font-size: 14px; }
.detail { display: grid; grid-template-columns: 1fr 1.1fr; gap: 28px; }
@media (max-width: 820px) { .detail { grid-template-columns: 1fr; } }

.thumb {
  position: relative; display: flex; align-items: center; justify-content: center;
  height: 360px; background: var(--color-primary-soft);
}
.thumb .emoji { font-size: 140px; }
.thumb-badges { position: absolute; bottom: 14px; left: 14px; display: flex; gap: 8px; }

.info { display: flex; flex-direction: column; }
.name { font-size: 28px; margin: 0 0 6px; }
.seller { margin: 0 0 8px; }
.rate { display: flex; align-items: center; gap: 6px; margin: 0 0 12px; font-size: 15px; }
.desc { line-height: 1.6; color: #4a5560; }
.divider { border: none; border-top: 1px solid var(--color-border); margin: 18px 0; }

.price-row { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 14px; }
.sm { font-size: 13px; }
.big-price { font-size: 32px; font-weight: 800; color: var(--color-accent-dark); }
.stock { text-align: right; }
.stock-val { font-size: 22px; font-weight: 700; color: var(--color-primary-dark); }
.stock-val.low { color: var(--color-accent-dark); }

.ship {
  background: var(--color-primary-soft); border-color: #cfe8d4;
  padding: 14px 16px; font-size: 14px; line-height: 1.7; color: var(--color-primary-dark);
  margin-bottom: 18px;
}

.qty-row { display: flex; align-items: center; gap: 16px; margin-bottom: 14px; }
.qty-label { font-weight: 600; }
.stepper { display: inline-flex; align-items: center; border: 1px solid var(--color-border); border-radius: var(--radius-sm); overflow: hidden; }
.stepper button { width: 42px; height: 42px; border: none; background: #fff; font-size: 20px; color: var(--color-text); }
.stepper button:hover:not(:disabled) { background: var(--color-bg); }
.stepper button:disabled { opacity: 0.35; }
.qty-val { width: 56px; text-align: center; font-size: 16px; font-weight: 700; }

.estimated { font-size: 16px; margin-bottom: 8px; }
.estimated .price { font-size: 20px; }
.err { color: var(--color-accent-dark); font-size: 14px; margin: 4px 0; }

.actions { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 8px; }
.actions .btn { padding: 15px; font-size: 16px; }

.reviews { margin-top: 48px; }
.reviews-title { font-size: 20px; border-top: 1px solid var(--color-border); padding-top: 24px; }
.review-list { display: flex; flex-direction: column; gap: 12px; }
.review-item { padding: 14px 16px; }
.review-head { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
.review-body { margin: 0; color: #4a5560; line-height: 1.6; }
</style>
