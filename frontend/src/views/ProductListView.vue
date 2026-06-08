<script setup>
import { ref, computed, onMounted } from 'vue'
import { productApi } from '../api/products'
import { useCartStore } from '../stores/cart'
import { categoryLabel } from '../utils/format'
import ProductCard from '../components/ProductCard.vue'

const cart = useCartStore()

const products = ref([])
const loading = ref(true)
const error = ref('')
const keyword = ref('')
const activeCategory = ref('all')
const sort = ref('latest')

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

// 상품에 존재하는 카테고리들로 필터칩 동적 구성
const categories = computed(() => {
  const set = [...new Set(products.value.map((p) => p.category).filter(Boolean))]
  return ['all', ...set]
})

const filtered = computed(() => {
  let list = products.value
  if (activeCategory.value !== 'all') {
    list = list.filter((p) => p.category === activeCategory.value)
  }
  if (keyword.value.trim()) {
    const kw = keyword.value.trim().toLowerCase()
    list = list.filter((p) => p.name?.toLowerCase().includes(kw))
  }
  const sorted = [...list]
  const dday = (p) => (p.daysToExpiry == null ? 9999 : p.daysToExpiry)
  const deal = (p) => p.discountedPrice ?? p.price
  if (sort.value === 'urgent') sorted.sort((a, b) => dday(a) - dday(b) || (b.discountRate ?? 0) - (a.discountRate ?? 0))
  else if (sort.value === 'discount') sorted.sort((a, b) => (b.discountRate ?? 0) - (a.discountRate ?? 0))
  else if (sort.value === 'priceAsc') sorted.sort((a, b) => deal(a) - deal(b))
  else if (sort.value === 'priceDesc') sorted.sort((a, b) => deal(b) - deal(a))
  else sorted.sort((a, b) => b.productId - a.productId)
  return sorted
})

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
    <!-- 배너 -->
    <div class="banner">
      🥬 산지에서 바로, 신선식품 직거래
      <router-link :to="{ name: 'deals' }" class="banner-badge deals-link">⏰ 마감임박 특가 →</router-link>
    </div>

    <!-- 검색 -->
    <div class="search-row">
      <input v-model="keyword" class="input search" placeholder="상품명으로 검색하세요 (예: 상추)" />
    </div>

    <!-- 카테고리 필터칩 + 정렬 -->
    <div class="filter-row">
      <div class="chips">
        <button
          v-for="c in categories" :key="c"
          class="chip" :class="{ active: activeCategory === c }"
          @click="activeCategory = c"
        >
          <span class="dot" />{{ c === 'all' ? '전체' : categoryLabel(c) }}
        </button>
      </div>
      <div class="sort">
        <label class="muted">정렬</label>
        <select v-model="sort" class="select">
          <option value="urgent">마감임박순</option>
          <option value="discount">할인율순</option>
          <option value="priceAsc">가격 낮은순</option>
          <option value="priceDesc">가격 높은순</option>
          <option value="latest">최신순</option>
        </select>
      </div>
    </div>

    <p class="count muted">{{ filtered.length }}개 상품</p>

    <div v-if="loading" class="empty"><span class="emoji">⏳</span>상품을 불러오는 중…</div>
    <div v-else-if="error" class="empty"><span class="emoji">⚠️</span>{{ error }}<br /><button class="btn btn-outline" style="margin-top:12px" @click="load">다시 시도</button></div>
    <div v-else-if="filtered.length === 0" class="empty"><span class="emoji">🔍</span>조건에 맞는 상품이 없어요.</div>

    <div v-else class="grid">
      <ProductCard v-for="p in filtered" :key="p.productId" :product="p" @add="addToCart" />
    </div>

    <transition name="fade">
      <div v-if="toast" class="toast">{{ toast }}</div>
    </transition>
  </div>
</template>

<style scoped>
.banner {
  background: var(--color-primary-soft);
  border: 1px solid #cfe8d4;
  color: var(--color-primary-dark);
  border-radius: var(--radius);
  padding: 16px 18px;
  font-weight: 700;
  display: flex; align-items: center; gap: 10px;
  margin-bottom: 18px;
}
.banner-badge { background: var(--color-primary); color: #fff; font-size: 12px; padding: 3px 10px; border-radius: 999px; }
.deals-link { font-weight: 700; transition: background 0.15s ease; }
.deals-link:hover { background: var(--color-primary-dark); }

.search-row { margin-bottom: 14px; }
.search { max-width: 420px; }

.filter-row { display: flex; align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap; }
.chips { display: flex; gap: 8px; flex-wrap: wrap; }
.chip {
  display: inline-flex; align-items: center; gap: 6px;
  background: #fff; border: 1px solid var(--color-border);
  border-radius: 999px; padding: 7px 14px; font-size: 14px; font-weight: 600; color: var(--color-muted);
}
.chip .dot { width: 8px; height: 8px; border-radius: 50%; background: #d6dade; }
.chip:hover { border-color: var(--color-primary); }
.chip.active { color: var(--color-primary-dark); border-color: var(--color-primary); background: var(--color-primary-soft); }
.chip.active .dot { background: var(--color-accent); }

.sort { display: flex; align-items: center; gap: 8px; }
.sort .select { width: auto; padding: 8px 12px; }

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
