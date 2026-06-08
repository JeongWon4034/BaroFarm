<script setup>
import { ref, computed, onMounted } from 'vue'
import { wishlistApi } from '../api/wishlist'
import { useWishlistStore } from '../stores/wishlist'
import { useCartStore } from '../stores/cart'
import ProductCard from '../components/ProductCard.vue'

const wishlist = useWishlistStore()
const cart = useCartStore()

const all = ref([])
const loading = ref(true)
const error = ref('')

onMounted(load)
async function load() {
  loading.value = true
  error.value = ''
  try {
    all.value = (await wishlistApi.list()) || []
    wishlist.ids = all.value.map((p) => p.productId)
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

// 하트 해제 시 즉시 사라지도록 store 기준으로 필터
const products = computed(() => all.value.filter((p) => wishlist.isWished(p.productId)))

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
    <h1 class="title">❤️ 찜한 상품</h1>

    <div v-if="loading" class="empty"><span class="emoji">⏳</span>불러오는 중…</div>
    <div v-else-if="error" class="empty">
      <span class="emoji">⚠️</span>{{ error }}<br />
      <button class="btn btn-outline" style="margin-top:12px" @click="load">다시 시도</button>
    </div>
    <div v-else-if="products.length === 0" class="empty">
      <span class="emoji">🤍</span>아직 찜한 상품이 없어요.<br />
      <router-link class="btn btn-primary" style="margin-top:14px" :to="{ name: 'products' }">상품 보러 가기</router-link>
    </div>

    <template v-else>
      <p class="count muted">{{ products.length }}개</p>
      <div class="grid">
        <ProductCard v-for="p in products" :key="p.productId" :product="p" @add="addToCart" />
      </div>
    </template>

    <transition name="fade">
      <div v-if="toast" class="toast">{{ toast }}</div>
    </transition>
  </div>
</template>

<style scoped>
.title { font-size: 24px; margin-bottom: 16px; }
.count { margin: 8px 0 16px; font-size: 14px; }
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
