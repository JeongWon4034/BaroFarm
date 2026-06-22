<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '../stores/cart'
import { useAuthStore } from '../stores/auth'
import { orderApi } from '../api/orders'
import { track } from '../api/track'
import { won, thumbEmoji, dDayLabel } from '../utils/format'

const router = useRouter()
const cart = useCartStore()
const auth = useAuthStore()

const submitting = ref(false)
const error = ref('')

// 표시용 합계 — 결제 로직과 무관(요약 카드 표시만)
const origTotal = computed(() =>
  cart.items.reduce((s, i) => s + (i.originalPrice || i.price) * i.quantity, 0)
)
const savedTotal = computed(() => Math.max(0, origTotal.value - cart.totalPrice))
const shipFee = computed(() => (cart.totalPrice >= 30000 || cart.totalPrice === 0 ? 0 : 3000))
const payTotal = computed(() => cart.totalPrice + shipFee.value)

async function checkout() {
  // 퍼널 4단계 — 장바구니 결제 시도(담은 항목들 기준)
  cart.items.forEach((item) => track('click_checkout', { productId: item.productId }))
  if (!auth.isLoggedIn) {
    router.push({ name: 'login', query: { redirect: '/cart' } })
    return
  }
  if (cart.items.length === 0) return
  submitting.value = true
  error.value = ''
  try {
    // 백엔드는 1상품 단위 주문 → 항목별로 순차 생성
    const ids = []
    for (const item of cart.items) {
      const order = await orderApi.create({ productId: item.productId, lotId: item.lotId, quantity: item.quantity })
      ids.push(order.orderId)
    }
    cart.clear()
    router.push({ name: 'order-complete', query: { ids: ids.join(',') } })
  } catch (e) {
    error.value = e.message
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="cartpage">
    <h1 class="cart-h">🧺 장바구니</h1>
    <p class="cart-sub">{{ cart.items.length ? `담은 상품 ${cart.items.length}종 · 확인 후 결제하세요` : '담은 상품이 없어요' }}</p>

    <div v-if="cart.items.length === 0" class="cart-empty">
      <span class="ce-emoji">🛒</span>
      <p>장바구니가 비어 있어요.<br />산지 직송 신선식품을 둘러보세요!</p>
      <router-link class="btn btn-primary" :to="{ name: 'products' }">상품 보러 가기</router-link>
    </div>

    <div v-else class="cart-grid">
      <div class="cart-list">
        <div class="citem" v-for="item in cart.items" :key="item.key">
          <div class="ci-tile">{{ thumbEmoji(item) }}</div>
          <div class="ci-info">
            <div class="ci-meta">
              <span v-if="item.discountRate" class="chip urgent">{{ item.discountRate }}% 할인</span>
              <span v-if="item.daysToExpiry != null" class="chip dday">⏰ {{ dDayLabel(item.daysToExpiry) }} 옵션</span>
            </div>
            <router-link :to="{ name: 'product-detail', params: { id: item.productId } }" class="nm">{{ item.name }}</router-link>
            <div class="qtybox">
              <button @click="cart.updateQty(item.key, item.quantity - 1)" :disabled="item.quantity <= 1">−</button>
              <span class="q">{{ item.quantity }}</span>
              <button @click="cart.updateQty(item.key, item.quantity + 1)">+</button>
            </div>
          </div>
          <div class="ci-right">
            <div class="pr">
              <span v-if="item.discountRate" class="pct">{{ item.discountRate }}%</span>
              <span class="now">{{ won(item.price * item.quantity) }}</span>
            </div>
            <span v-if="item.discountRate" class="was">{{ won((item.originalPrice || item.price) * item.quantity) }}</span>
            <span class="ci-del" @click="cart.remove(item.key)">삭제</span>
          </div>
        </div>
      </div>

      <aside class="summary">
        <h3>결제 예정 금액</h3>
        <div class="srow"><span>상품 금액</span><span>{{ won(origTotal) }}</span></div>
        <div v-if="savedTotal > 0" class="srow save"><span>마감임박 할인</span><span>-{{ won(savedTotal) }}</span></div>
        <div class="srow"><span>배송비</span><span :class="{ free: shipFee === 0 }">{{ shipFee === 0 ? '무료' : won(shipFee) }}</span></div>
        <div class="divider"></div>
        <div class="srow total"><span>결제 예정</span><b>{{ won(payTotal) }}</b></div>
        <p v-if="error" class="err">{{ error }}</p>
        <button class="btn btn-accent" :disabled="submitting" @click="checkout">
          {{ submitting ? '결제 처리 중…' : `${won(payTotal)} 결제하기` }}
        </button>
        <div class="ship-note">🌱 산지직송 · 내일 도착 · 30,000원 이상 무료배송</div>
        <p v-if="!auth.isLoggedIn" class="hint">결제하려면 로그인이 필요해요.</p>
      </aside>
    </div>
  </div>
</template>

<style scoped>
.cartpage { padding: 4px 0 40px; }
.cart-h { font-size: 28px; font-weight: 800; letter-spacing: -.02em; margin: 0 0 6px; }
.cart-sub { color: var(--muted); font-size: 14px; margin: 0 0 26px; }

.cart-empty { background: #fff; border: 1px dashed var(--line-2); border-radius: 18px; padding: 56px 24px; text-align: center; color: var(--muted); display: flex; flex-direction: column; align-items: center; gap: 14px; }
.cart-empty .ce-emoji { font-size: 46px; }
.cart-empty p { margin: 0; line-height: 1.6; }

.cart-grid { display: grid; grid-template-columns: 1fr 360px; gap: 30px; align-items: start; }
.cart-list { display: flex; flex-direction: column; gap: 14px; }
.citem { display: grid; grid-template-columns: 96px 1fr auto; gap: 18px; align-items: center; background: #fff; border: 1px solid var(--line); border-radius: 16px; padding: 16px; box-shadow: var(--shadow-sm); transition: box-shadow .15s; }
.citem:hover { box-shadow: var(--shadow-md); }
.ci-tile { width: 96px; height: 96px; border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 50px; background: radial-gradient(circle at 50% 36%, var(--leaf-50), var(--leaf-100)); }
.ci-info { display: flex; flex-direction: column; gap: 9px; min-width: 0; }
.ci-meta { display: flex; gap: 6px; flex-wrap: wrap; min-height: 1px; }
.chip { font-size: 11.5px; font-weight: 600; padding: 3px 9px; border-radius: 7px; background: var(--leaf-50); color: var(--leaf-700); white-space: nowrap; }
.chip.urgent { background: var(--deal-soft); color: var(--deal); }
.chip.dday { background: #23281c; color: #fff; }
.ci-info .nm { font-size: 16.5px; font-weight: 700; }
.ci-info .nm:hover { color: var(--leaf-700); }
.qtybox { display: inline-flex; align-items: center; border: 1.5px solid var(--line-2); border-radius: 11px; overflow: hidden; background: #fff; width: fit-content; }
.qtybox button { width: 36px; height: 38px; border: none; background: #fff; font-size: 18px; color: var(--ink-2); }
.qtybox button:hover:not(:disabled) { background: var(--leaf-50); color: var(--leaf-700); }
.qtybox button:disabled { opacity: .35; }
.qtybox .q { width: 42px; text-align: center; font-weight: 700; font-variant-numeric: tabular-nums; }
.ci-right { display: flex; flex-direction: column; align-items: flex-end; gap: 8px; text-align: right; }
.ci-right .pr { display: flex; align-items: baseline; gap: 7px; }
.ci-right .pct { color: var(--deal); font-weight: 800; }
.ci-right .now { font-weight: 800; font-size: 19px; letter-spacing: -.02em; }
.ci-right .was { color: var(--faint); text-decoration: line-through; font-size: 12.5px; }
.ci-del { font-size: 12.5px; color: var(--faint); cursor: pointer; }
.ci-del:hover { color: var(--deal); }

.summary { position: sticky; top: 130px; background: #fff; border: 1.5px solid var(--ink); border-radius: 18px; padding: 22px; box-shadow: var(--shadow-md); }
.summary h3 { font-size: 18px; font-weight: 800; margin: 0 0 16px; }
.srow { display: flex; justify-content: space-between; align-items: center; font-size: 14.5px; color: var(--ink-2); margin-bottom: 12px; }
.srow.save { color: var(--deal); font-weight: 600; }
.srow .free { color: var(--leaf-700); font-weight: 700; }
.divider { height: 1px; background: var(--line); margin: 16px 0; }
.srow.total { font-size: 16px; font-weight: 700; color: var(--ink); }
.srow.total b { font-size: 24px; font-weight: 800; letter-spacing: -.02em; }
.summary .btn { width: 100%; margin-top: 6px; padding: 16px; font-size: 17px; }
.ship-note { display: flex; align-items: center; gap: 8px; background: var(--leaf-50); border: 1px solid var(--leaf-100); border-radius: 11px; padding: 11px 13px; font-size: 12.5px; color: var(--leaf-700); font-weight: 600; margin-top: 14px; }
.hint { font-size: 13px; text-align: center; color: var(--muted); margin: 10px 0 0; }
.err { color: var(--deal); font-size: 14px; margin: 0 0 10px; }

@media (max-width: 900px) {
  .cart-grid { grid-template-columns: 1fr; }
  .summary { position: static; }
}
</style>
