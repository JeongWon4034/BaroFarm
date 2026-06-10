<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { productApi } from '../api/products'
import { useCartStore } from '../stores/cart'
import { categoryLabel } from '../utils/format'
import ProductCard from '../components/ProductCard.vue'

const cart = useCartStore()
const route = useRoute()
const router = useRouter()
const CATEGORIES = ['all', 'vegetable', 'fruit', 'seafood', 'meat', 'grain', 'mushroom', 'root']
const SORTS = ['latest', 'expiry', 'priceAsc', 'priceDesc']
const SIZE = 12

const products = ref([])
const loading = ref(true)
const error = ref('')
// 초기 상태를 URL 쿼리에서 복원 → 새로고침·뒤로가기·링크 공유에도 검색조건 유지
const keyword = ref(route.query.keyword || '')
const activeCategory = ref(CATEGORIES.includes(route.query.category) ? route.query.category : 'all')
const sort = ref(SORTS.includes(route.query.sort) ? route.query.sort : 'latest')
const page = ref(Math.max(0, (parseInt(route.query.page) || 1) - 1))
const totalPages = ref(0)
const totalElements = ref(0)

onMounted(load)

// 현재 검색 상태를 URL 쿼리에 반영(기본값은 생략해 깔끔하게)
function syncUrl() {
  const q = {}
  if (keyword.value.trim()) q.keyword = keyword.value.trim()
  if (activeCategory.value !== 'all') q.category = activeCategory.value
  if (sort.value !== 'latest') q.sort = sort.value
  if (page.value > 0) q.page = page.value + 1
  router.replace({ query: q }).catch(() => {})
}

async function load() {
  loading.value = true
  error.value = ''
  syncUrl()
  try {
    const res = await productApi.list({
      page: page.value,
      size: SIZE,
      keyword: keyword.value.trim() || undefined,
      category: activeCategory.value === 'all' ? undefined : activeCategory.value,
      sort: sort.value,
    })
    products.value = res.content || []
    totalPages.value = res.totalPages || 0
    totalElements.value = res.totalElements || 0
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

// 검색은 디바운스, 필터/정렬 변경 시 첫 페이지로 리셋 후 재조회
let searchTimer
watch(keyword, () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => { page.value = 0; load() }, 350)
})
watch([activeCategory, sort], () => { page.value = 0; load() })

function setCategory(c) { activeCategory.value = c }
function goPage(p) {
  if (p < 0 || p >= totalPages.value || p === page.value) return
  page.value = p
  load()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const pageWindow = computed(() => {
  const tp = totalPages.value
  if (tp <= 1) return []
  let start = Math.max(0, page.value - 2)
  const end = Math.min(tp, start + 5)
  start = Math.max(0, end - 5)
  return Array.from({ length: end - start }, (_, i) => start + i)
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
    <div class="banner">
      🥬 산지에서 바로, 신선식품 직거래
      <router-link :to="{ name: 'deals' }" class="banner-badge deals-link">⏰ 마감임박 특가 →</router-link>
    </div>

    <div class="search-row">
      <input v-model="keyword" class="input search" placeholder="상품명으로 검색하세요 (예: 상추)" />
    </div>

    <div class="filter-row">
      <div class="chips">
        <button
          v-for="c in CATEGORIES" :key="c"
          class="chip" :class="{ active: activeCategory === c }"
          @click="setCategory(c)"
        >
          <span class="dot" />{{ c === 'all' ? '전체' : categoryLabel(c) }}
        </button>
      </div>
      <div class="sort">
        <label class="muted">정렬</label>
        <select v-model="sort" class="select">
          <option value="latest">최신순</option>
          <option value="expiry">마감임박순</option>
          <option value="priceAsc">가격 낮은순</option>
          <option value="priceDesc">가격 높은순</option>
        </select>
      </div>
    </div>

    <p class="count muted">총 {{ totalElements }}개 상품 · {{ page + 1 }}/{{ Math.max(totalPages, 1) }} 페이지</p>

    <div v-if="loading" class="empty"><span class="emoji">⏳</span>상품을 불러오는 중…</div>
    <div v-else-if="error" class="empty"><span class="emoji">⚠️</span>{{ error }}<br /><button class="btn btn-outline" style="margin-top:12px" @click="load">다시 시도</button></div>
    <div v-else-if="products.length === 0" class="empty"><span class="emoji">🔍</span>조건에 맞는 상품이 없어요.</div>

    <template v-else>
      <div class="grid">
        <ProductCard v-for="p in products" :key="p.productId" :product="p" @add="addToCart" />
      </div>

      <div v-if="totalPages > 1" class="pagination">
        <button class="pg-btn" :disabled="page === 0" @click="goPage(page - 1)">‹</button>
        <button v-for="p in pageWindow" :key="p" class="pg-btn" :class="{ active: p === page }" @click="goPage(p)">{{ p + 1 }}</button>
        <button class="pg-btn" :disabled="page >= totalPages - 1" @click="goPage(page + 1)">›</button>
      </div>
    </template>

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

.pagination { display: flex; justify-content: center; gap: 6px; margin: 28px 0 8px; }
.pg-btn {
  min-width: 36px; height: 36px; padding: 0 10px;
  border: 1px solid var(--color-border); background: #fff; border-radius: var(--radius-sm);
  font-size: 14px; font-weight: 600; color: var(--color-text); cursor: pointer;
}
.pg-btn:hover:not(:disabled) { border-color: var(--color-primary); }
.pg-btn.active { background: var(--color-primary); color: #fff; border-color: var(--color-primary); }
.pg-btn:disabled { opacity: 0.4; cursor: default; }

.toast {
  position: fixed; bottom: 28px; left: 50%; transform: translateX(-50%);
  background: var(--color-text); color: #fff; padding: 12px 22px;
  border-radius: 999px; font-size: 14px; font-weight: 600; box-shadow: var(--shadow-hover);
}
.fade-enter-active, .fade-leave-active { transition: opacity 0.25s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
