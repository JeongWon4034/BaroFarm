<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '../stores/cart'
import { useAuthStore } from '../stores/auth'
import { orderApi } from '../api/orders'
import { won, thumbEmoji } from '../utils/format'

const router = useRouter()
const cart = useCartStore()
const auth = useAuthStore()

const submitting = ref(false)
const error = ref('')

async function checkout() {
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
      const order = await orderApi.create({ productId: item.productId, quantity: item.quantity })
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
  <div>
    <h1 class="title">🧺 장바구니 & 결제</h1>

    <div v-if="cart.items.length === 0" class="empty">
      <span class="emoji">🛒</span>장바구니가 비어 있어요.
      <br /><router-link class="btn btn-primary" style="margin-top:14px" :to="{ name: 'products' }">상품 보러 가기</router-link>
    </div>

    <div v-else class="cart-layout">
      <ul class="lines">
        <li v-for="item in cart.items" :key="item.productId" class="line card">
          <span class="thumb">{{ thumbEmoji(item) }}</span>
          <div class="info">
            <router-link :to="{ name: 'product-detail', params: { id: item.productId } }" class="name">{{ item.name }}</router-link>
            <span class="price">{{ won(item.price) }}</span>
          </div>
          <div class="stepper">
            <button @click="cart.updateQty(item.productId, item.quantity - 1)" :disabled="item.quantity <= 1">−</button>
            <span class="qty">{{ item.quantity }}</span>
            <button @click="cart.updateQty(item.productId, item.quantity + 1)">+</button>
          </div>
          <div class="subtotal">{{ won(item.price * item.quantity) }}</div>
          <button class="remove" @click="cart.remove(item.productId)" title="삭제">✕</button>
        </li>
      </ul>

      <aside class="summary card">
        <h3>주문 요약</h3>
        <div class="row"><span class="muted">상품 종류</span><span>{{ cart.items.length }}종</span></div>
        <div class="row"><span class="muted">총 수량</span><span>{{ cart.count }}개</span></div>
        <div class="row"><span class="muted">배송비</span><span>{{ cart.totalPrice >= 30000 ? '무료' : won(3000) }}</span></div>
        <hr class="divider" />
        <div class="row total">
          <span>결제 예정 금액</span>
          <span class="price">{{ won(cart.totalPrice + (cart.totalPrice >= 30000 ? 0 : 3000)) }}</span>
        </div>
        <p v-if="error" class="err">{{ error }}</p>
        <button class="btn btn-accent btn-block pay" :disabled="submitting" @click="checkout">
          {{ submitting ? '결제 처리 중…' : '💳 결제하기' }}
        </button>
        <p v-if="!auth.isLoggedIn" class="hint muted">결제하려면 로그인이 필요해요.</p>
      </aside>
    </div>
  </div>
</template>

<style scoped>
.title { font-size: 24px; margin-bottom: 20px; }
.cart-layout { display: grid; grid-template-columns: 1fr 320px; gap: 24px; align-items: start; }
@media (max-width: 820px) { .cart-layout { grid-template-columns: 1fr; } }

.lines { display: flex; flex-direction: column; gap: 12px; }
.line { display: flex; align-items: center; gap: 16px; padding: 14px 16px; }
.line .thumb { font-size: 40px; width: 56px; text-align: center; background: var(--color-primary-soft); border-radius: var(--radius-sm); padding: 6px 0; }
.line .info { flex: 1; display: flex; flex-direction: column; gap: 4px; }
.line .name { font-weight: 700; }
.line .name:hover { color: var(--color-primary-dark); }

.stepper { display: inline-flex; align-items: center; border: 1px solid var(--color-border); border-radius: var(--radius-sm); }
.stepper button { width: 34px; height: 34px; border: none; background: #fff; font-size: 18px; }
.stepper button:disabled { opacity: 0.35; }
.stepper .qty { width: 40px; text-align: center; font-weight: 700; }
.subtotal { width: 90px; text-align: right; font-weight: 700; }
.remove { border: none; background: transparent; color: var(--color-muted); font-size: 16px; }
.remove:hover { color: var(--color-accent-dark); }

.summary { padding: 20px; position: sticky; top: 20px; }
.summary h3 { margin: 0 0 16px; }
.row { display: flex; justify-content: space-between; font-size: 15px; margin-bottom: 10px; }
.divider { border: none; border-top: 1px solid var(--color-border); margin: 14px 0; }
.total { font-size: 17px; font-weight: 700; }
.total .price { font-size: 20px; }
.pay { margin-top: 16px; padding: 14px; font-size: 16px; }
.hint { font-size: 13px; text-align: center; margin: 10px 0 0; }
.err { color: var(--color-accent-dark); font-size: 14px; }
</style>
