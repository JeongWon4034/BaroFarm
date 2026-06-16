<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { productApi } from '../api/products'
import { useCartStore } from '../stores/cart'
import { categoryLabel } from '../utils/format'
import { track } from '../api/track'
import ProductCard from '../components/ProductCard.vue'

const cart = useCartStore()
const route = useRoute()
const router = useRouter()
const CATEGORIES = ['all', 'vegetable', 'fruit', 'seafood', 'meat', 'grain', 'mushroom', 'root']
const SORTS = ['latest', 'expiry', 'priceAsc', 'priceDesc']
const SORT_LABEL = { latest: '최신순', expiry: '마감임박순', priceAsc: '가격 낮은순', priceDesc: '가격 높은순' }
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

onMounted(() => {
  track('view_home') // 퍼널 1단계 — 홈/상품목록 진입
  load()
})

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
// 헤더 검색 등으로 URL keyword가 바뀌면 입력값도 동기화
watch(() => route.query.keyword, (k) => {
  const nk = k || ''
  if (nk !== keyword.value) keyword.value = nk
})
watch([activeCategory, sort], () => { page.value = 0; load() })

function setCategory(c) { activeCategory.value = c }
function setSort(s) { sort.value = s }
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
  toast.value = `${product.name} · 장바구니에 담았어요`
  clearTimeout(toastTimer)
  toastTimer = setTimeout(() => (toast.value = ''), 1800)
}
</script>

<template>
  <div>
    <!-- 배너 -->
    <div class="banner">
      <span class="b-ic">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 8v4l3 2"/><circle cx="12" cy="12" r="9"/></svg>
      </span>
      <span class="b-txt">산지에서 바로, 오늘 마감임박 신선식품<small>버려질 뻔한 신선식품을 제값에 — 농가도 식탁도 알뜰하게</small></span>
      <router-link :to="{ name: 'deals' }" class="b-link">
        마감임박 특가 보기
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>
      </router-link>
    </div>

    <div class="shop-grid">
      <!-- 사이드바: 카테고리 -->
      <aside>
        <div class="panel">
          <h4>카테고리</h4>
          <div class="catlist">
            <button
              v-for="c in CATEGORIES" :key="c"
              class="cat" :class="{ on: activeCategory === c }"
              @click="setCategory(c)"
            >
              <span class="nm"><span class="dot" />{{ c === 'all' ? '전체' : categoryLabel(c) }}</span>
            </button>
          </div>
        </div>
      </aside>

      <!-- 본문 -->
      <div>
        <div class="toolbar">
          <div class="searchwrap">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
            <input v-model="keyword" class="search" placeholder="상품명으로 검색하세요 (예: 상추)" />
          </div>
          <div class="seg">
            <button v-for="s in SORTS" :key="s" :class="{ on: sort === s }" @click="setSort(s)">{{ SORT_LABEL[s] }}</button>
          </div>
        </div>

        <div class="prod-head">
          <h2>오늘의 신선식품</h2>
          <p class="muted">총 <b>{{ totalElements }}</b>개 상품 · {{ page + 1 }}/{{ Math.max(totalPages, 1) }} 페이지</p>
        </div>

        <div v-if="loading" class="empty"><span class="emoji">⏳</span>상품을 불러오는 중…</div>
        <div v-else-if="error" class="empty"><span class="emoji">⚠️</span>{{ error }}<br /><button class="btn btn-outline" style="margin-top:12px" @click="load">다시 시도</button></div>
        <div v-else-if="products.length === 0" class="empty"><span class="emoji">🔍</span>조건에 맞는 상품이 없어요.</div>

        <template v-else>
          <div class="grid">
            <ProductCard v-for="p in products" :key="p.productId" :product="p" @add="addToCart" />
          </div>

          <div v-if="totalPages > 1" class="pagination">
            <button class="pg" :disabled="page === 0" @click="goPage(page - 1)">‹</button>
            <button v-for="p in pageWindow" :key="p" class="pg" :class="{ on: p === page }" @click="goPage(p)">{{ p + 1 }}</button>
            <button class="pg" :disabled="page >= totalPages - 1" @click="goPage(page + 1)">›</button>
          </div>
        </template>
      </div>
    </div>

    <transition name="fade">
      <div v-if="toast" class="toast">
        <span class="ic"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3.2" stroke-linecap="round"><path d="m5 12 5 5L20 6"/></svg></span>
        {{ toast }}
      </div>
    </transition>
  </div>
</template>

<style scoped>
/* 배너 */
.banner{
  display:flex; align-items:center; gap:12px;
  background:linear-gradient(120deg, var(--leaf-50), var(--leaf-100));
  border:1px solid #d6ebc2; border-radius:16px; padding:16px 20px; margin-bottom:24px;
}
.b-ic{ width:38px; height:38px; border-radius:11px; background:#fff; display:flex; align-items:center; justify-content:center; color:var(--leaf-600); box-shadow:var(--shadow-sm); }
.b-txt{ font-weight:700; color:var(--leaf-700); font-size:15.5px; }
.b-txt small{ display:block; font-weight:500; color:#5b6a44; font-size:13px; margin-top:2px; }
.b-link{ margin-left:auto; display:inline-flex; align-items:center; gap:7px; background:var(--deal); color:#fff; font-weight:700; font-size:13.5px; padding:9px 16px; border-radius:999px; transition:.15s; white-space:nowrap; }
.b-link:hover{ background:#bd3a26; }

.shop-grid{ display:grid; grid-template-columns:230px 1fr; gap:32px; align-items:start; }
aside{ position:sticky; top:130px; align-self:start; }
.panel{ background:#fff; border:1px solid var(--line); border-radius:16px; padding:18px; box-shadow:var(--shadow-sm); }
.panel h4{ font-size:12px; text-transform:uppercase; letter-spacing:.08em; color:var(--faint); font-weight:700; margin:0 0 12px; }
.catlist{ display:flex; flex-direction:column; gap:2px; }
.cat{ display:flex; align-items:center; justify-content:space-between; padding:9px 11px; border-radius:10px; font-size:15px; font-weight:500; color:var(--ink-2); transition:.13s; border:none; background:transparent; text-align:left; }
.cat .nm{ display:flex; align-items:center; gap:10px; }
.cat .dot{ width:8px; height:8px; border-radius:50%; background:var(--leaf-400); flex:none; }
.cat:hover{ background:var(--leaf-50); }
.cat.on{ background:var(--leaf-100); color:var(--leaf-700); font-weight:700; }
.cat.on .dot{ background:var(--leaf-600); }

/* 툴바 */
.toolbar{ display:flex; align-items:center; gap:14px; margin-bottom:20px; flex-wrap:wrap; }
.searchwrap{ display:flex; align-items:center; gap:9px; background:#fff; border:1.5px solid var(--line-2); border-radius:12px; padding:0 14px; height:46px; flex:1; min-width:240px; transition:.18s; }
.searchwrap:focus-within{ border-color:var(--leaf-400); box-shadow:0 0 0 4px var(--leaf-50); }
.searchwrap svg{ color:var(--faint); }
.search{ border:none; outline:none; background:transparent; font-family:inherit; font-size:15px; width:100%; color:var(--ink); }
.search::placeholder{ color:var(--faint); }
.seg{ display:flex; background:#fff; border:1px solid var(--line); border-radius:10px; padding:3px; box-shadow:var(--shadow-sm); }
.seg button{ border:none; background:transparent; font-size:13.5px; font-weight:600; color:var(--muted); padding:8px 13px; border-radius:7px; transition:.13s; white-space:nowrap; }
.seg button.on{ background:var(--leaf-600); color:#fff; }
.seg button:not(.on):hover{ color:var(--ink); }

.prod-head{ display:flex; align-items:flex-end; justify-content:space-between; gap:12px; margin-bottom:18px; flex-wrap:wrap; }
.prod-head h2{ font-size:24px; font-weight:800; letter-spacing:-.02em; margin:0; }
.prod-head p{ margin:0; font-size:14px; }
.prod-head p b{ color:var(--leaf-700); font-weight:700; }

.grid{ display:grid; grid-template-columns:repeat(3, 1fr); gap:20px; }

.pagination{ display:flex; justify-content:center; gap:7px; margin:34px 0 0; }
.pg{ min-width:38px; height:38px; padding:0 11px; border:1px solid var(--line); background:#fff; border-radius:10px; font-size:14px; font-weight:600; color:var(--ink-2); transition:.13s; }
.pg:hover:not(:disabled){ border-color:var(--leaf-400); }
.pg.on{ background:var(--leaf-600); color:#fff; border-color:var(--leaf-600); }
.pg:disabled{ opacity:.4; cursor:default; }

.toast{
  position:fixed; left:50%; bottom:34px; transform:translateX(-50%);
  background:#23281c; color:#fff; font-weight:600; font-size:14.5px;
  padding:13px 22px; border-radius:13px; box-shadow:var(--shadow-lg);
  display:flex; align-items:center; gap:10px; z-index:60;
}
.toast .ic{ width:22px; height:22px; border-radius:50%; background:var(--leaf-500); display:flex; align-items:center; justify-content:center; }
.fade-enter-active, .fade-leave-active{ transition:opacity .25s ease, transform .25s ease; }
.fade-enter-from, .fade-leave-to{ opacity:0; transform:translateX(-50%) translateY(12px); }

@media (max-width:1080px){
  .shop-grid{ grid-template-columns:200px 1fr; gap:24px; }
  .grid{ grid-template-columns:repeat(2, 1fr); }
}
@media (max-width:780px){
  .shop-grid{ grid-template-columns:1fr; }
  aside{ position:static; }
  .grid{ grid-template-columns:repeat(2, 1fr); }
}
@media (max-width:520px){
  .grid{ grid-template-columns:1fr; }
}
</style>
