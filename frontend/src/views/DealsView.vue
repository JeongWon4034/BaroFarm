<script setup>
import { ref, computed, onMounted } from 'vue'
import { productApi } from '../api/products'
import { useCartStore } from '../stores/cart'
import ProductCard from '../components/ProductCard.vue'

const cart = useCartStore()

const products = ref([])
const loading = ref(true)
const error = ref('')

onMounted(load)
async function load() {
  loading.value = true
  error.value = ''
  try {
    const res = await productApi.list(0, 100)
    products.value = res.content || []
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

// 마감임박 = 떨이가가 적용된 상품(유통기한 임박). 임박순 정렬.
const deals = computed(() =>
  products.value
    .filter((p) => (p.discountRate ?? 0) > 0)
    .sort((a, b) => (a.daysToExpiry ?? 999) - (b.daysToExpiry ?? 999) || (b.discountRate ?? 0) - (a.discountRate ?? 0))
)

let toastTimer
const toast = ref('')
function addToCart(product) {
  cart.add(product, 1)
  toast.value = `🛒 ${product.name} 담음`
  clearTimeout(toastTimer)
  toastTimer = setTimeout(() => (toast.value = ''), 1800)
}
</script>

<template>
  <div>
    <div class="deal-banner">
      <div class="deal-title">⏰ 마감임박 특가</div>
      <p class="deal-sub">유통기한이 가까운 신선식품을 AI가 골라 폐기 전에 떨이가로 드려요. 빠를수록 더 싸게.</p>
    </div>

    <div v-if="loading" class="empty"><span class="emoji">⏳</span>마감임박 상품을 불러오는 중…</div>
    <div v-else-if="error" class="empty">
      <span class="emoji">⚠️</span>{{ error }}<br />
      <button class="btn btn-outline" style="margin-top:12px" @click="load">다시 시도</button>
    </div>
    <div v-else-if="deals.length === 0" class="empty">
      <span class="emoji">🌿</span>지금은 마감임박 상품이 없어요.<br />
      <router-link class="btn btn-primary" style="margin-top:14px" :to="{ name: 'products' }">전체 상품 보러 가기</router-link>
    </div>

    <template v-else>
      <p class="count muted">마감임박 {{ deals.length }}개</p>
      <div class="grid">
        <ProductCard v-for="p in deals" :key="p.productId" :product="p" @add="addToCart" />
      </div>
    </template>

    <transition name="fade">
      <div v-if="toast" class="toast">{{ toast }}</div>
    </transition>
  </div>
</template>

<style scoped>
.deal-banner {
  background: linear-gradient(120deg, #fdecec, #fff4e6);
  border: 1px solid #f6d6d6;
  border-radius: var(--radius);
  padding: 18px 20px;
  margin-bottom: 18px;
}
.deal-title { font-size: 20px; font-weight: 800; color: #c1272d; }
.deal-sub { margin: 6px 0 0; font-size: 14px; color: #8a5a2b; }

.count { margin: 16px 0; font-size: 14px; }
.grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 18px; }
@media (max-width: 900px) { .grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 520px) { .grid { grid-template-columns: 1fr; } }

.toast {
  position: fixed; bottom: 28px; left: 50%; transform: translateX(-50%);
  background: var(--color-text); color: #fff; padding: 12px 22px;
  border-radius: 999px; font-size: 14px; font-weight: 600; box-shadow: var(--shadow-hover);
}
.fade-enter-active, .fade-leave-active { transition: opacity 0.25s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
