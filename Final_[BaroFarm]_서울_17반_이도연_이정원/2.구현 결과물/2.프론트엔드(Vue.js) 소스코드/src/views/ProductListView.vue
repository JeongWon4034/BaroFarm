<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { productApi } from '../api/products'
import { useCartStore } from '../stores/cart'
import { categoryLabel } from '../utils/format'
import { track } from '../api/track'
import ProductCard from '../components/ProductCard.vue'
import HeroBanner from '../components/HeroBanner.vue'
import DailyDeal from '../components/home/DailyDeal.vue'
import GardenPick from '../components/home/GardenPick.vue'
import RecipeSection from '../components/home/RecipeSection.vue'
import ReviewSection from '../components/home/ReviewSection.vue'

const cart = useCartStore()
const route = useRoute()
const router = useRouter()
const CATEGORIES = ['all', 'vegetable', 'fruit', 'seafood', 'meat', 'grain', 'etc']
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

// 홈(랜딩) 여부 — 카테고리 쿼리(전체 포함)·검색·페이지가 없는 첫 화면일 때만 랜딩 노출.
// '전체'(?category=all)는 홈이 아니라 '전체 상품 그리드'로 취급한다.
const isHome = computed(() => !route.query.category && !keyword.value.trim() && page.value === 0)
// 일일특가에 넘길 상품 — 현재 목록 중 할인율 최고 1개.
const dailyDeal = computed(() =>
  products.value.length
    ? [...products.value].sort((a, b) => (b.discountRate ?? 0) - (a.discountRate ?? 0))[0]
    : null
)
// 섹션 제목 — 홈='갓 들어온 신선식품', 전체='전체 상품', 카테고리 선택 시 그 카테고리명(예: 채소).
const sectionTitle = computed(() =>
  route.query.category === 'all'
    ? '전체 상품'
    : activeCategory.value === 'all'
      ? '갓 들어온 신선식품'
      : categoryLabel(activeCategory.value)
)

// 홈 '갓 들어온 신선식품' — 서로 다른 카테고리에서 랜덤 4개를 뽑아 다양하게 노출.
const homePicks = ref([])
async function loadHomePicks() {
  try {
    const res = await productApi.list({ page: 0, size: 100 })
    const all = res.content || []
    const byCat = {}
    for (const p of all) {
      if (p.category === 'processed') continue // 정체불명 카테고리는 추천에서 제외
      if (!byCat[p.category]) byCat[p.category] = []
      byCat[p.category].push(p)
    }
    const cats = Object.keys(byCat).sort(() => Math.random() - 0.5) // 카테고리 순서 셔플
    const picks = []
    for (const c of cats) {                                        // 카테고리당 1개씩
      picks.push(byCat[c][Math.floor(Math.random() * byCat[c].length)])
      if (picks.length >= 4) break
    }
    if (picks.length < 4) {                                        // 카테고리가 4개 미만이면 보충
      const rest = all.filter((p) => !picks.includes(p)).sort(() => Math.random() - 0.5)
      picks.push(...rest.slice(0, 4 - picks.length))
    }
    homePicks.value = picks
  } catch {
    homePicks.value = []
  }
}

onMounted(() => {
  track('view_home') // 퍼널 1단계 — 홈/상품목록 진입
  loadHomePicks()
  load()
})

// 현재 검색 상태를 URL 쿼리에 반영(기본값은 생략해 깔끔하게)
function syncUrl() {
  const q = {}
  if (keyword.value.trim()) q.keyword = keyword.value.trim()
  if (activeCategory.value !== 'all') q.category = activeCategory.value
  else if (route.query.category === 'all') q.category = 'all' // '전체 둘러보기' 상태 유지
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
// 헤더 '카테고리' 플라이아웃이 URL category를 바꾸면 필터에 반영(이미 홈에 있어도 동작)
watch(() => route.query.category, (c) => {
  const nc = CATEGORIES.includes(c) ? c : 'all'
  if (nc !== activeCategory.value) activeCategory.value = nc
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
    <!-- 메인 배너 — 홈 최상단 -->
    <HeroBanner v-if="isHome" />

    <!-- 섹션 헤더 + 정렬 -->
    <div class="sec-head">
      <div class="sh-l">
        <span v-if="activeCategory !== 'all'" class="badge">카테고리</span>
        <h2>{{ sectionTitle }}</h2>
        <span class="muted">{{ isHome ? '카테고리별 추천 4가지' : '총 ' + totalElements + '개' }}</span>
      </div>
      <div v-if="!isHome" class="seg">
        <button v-for="s in SORTS" :key="s" :class="{ on: sort === s }" @click="setSort(s)">{{ SORT_LABEL[s] }}</button>
      </div>
    </div>

    <!-- 홈: 서로 다른 카테고리에서 랜덤 4개만 -->
    <div v-if="isHome" class="grid">
      <ProductCard v-for="p in homePicks" :key="p.productId" :product="p" @add="addToCart" />
    </div>

    <!-- 카테고리/검색: 전체 그리드 + 페이지네이션 -->
    <template v-else>
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
    </template>

    <!-- 홈 랜딩 섹션 (갓 들어온 신선식품 아래, 카테고리·검색 중엔 숨김) -->
    <template v-if="isHome">
      <GardenPick />
      <RecipeSection />
      <ReviewSection />

      <!-- 마감임박 특가 배너 (빨간 박스) → 특가 탭으로 이동 -->
      <section class="sec">
        <router-link :to="{ name: 'deals' }" class="deal-banner">
          <div class="db-l">
            <span class="eyebrow">오늘의 마감임박 특가</span>
            <h2>오늘 안 사면 사라지는 신선식품, 더 저렴하게</h2>
            <p>유통기한이 임박할수록 더 싸게 — 마감 임박 상품만 모았어요</p>
          </div>
          <span class="db-go">특가 전체 보기
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>
          </span>
        </router-link>
      </section>

      <DailyDeal :product="dailyDeal" @add="addToCart" />
    </template>

    <transition name="fade">
      <div v-if="toast" class="toast">
        <span class="ic"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3.2" stroke-linecap="round"><path d="m5 12 5 5L20 6"/></svg></span>
        {{ toast }}
      </div>
    </transition>
  </div>
</template>

<style scoped>
/* 카테고리 가로 네비 */
.cat-row{
  display:flex; gap:8px; overflow-x:auto; padding-bottom:4px; margin-bottom:26px;
  border-bottom:1px solid var(--line);
}
.cat-row::-webkit-scrollbar{ height:0; }
.cat{
  flex:none; border:none; background:transparent; cursor:pointer;
  padding:11px 16px; font-size:15px; font-weight:500; color:var(--ink-2);
  border-bottom:2.5px solid transparent; margin-bottom:-1px; transition:.13s; white-space:nowrap;
}
.cat:hover{ color:var(--leaf-700); }
.cat.on{ color:var(--leaf-700); font-weight:700; border-bottom-color:var(--leaf-600); }

/* 섹션 헤더 */
.sec-head{ display:flex; align-items:flex-end; justify-content:space-between; gap:12px; margin-bottom:22px; flex-wrap:wrap; }
.sh-l{ display:flex; align-items:baseline; gap:10px; }
.sh-l h2{ font-size:23px; font-weight:800; letter-spacing:-.02em; margin:0; }
.sh-l .muted{ font-size:14px; }
.seg{ display:flex; gap:2px; }
.seg button{ border:none; background:transparent; font-size:13.5px; font-weight:600; color:var(--muted); padding:7px 11px; border-radius:8px; transition:.13s; white-space:nowrap; }
.seg button.on{ color:var(--leaf-700); background:var(--leaf-50); }
.seg button:not(.on):hover{ color:var(--ink); }

/* 컬리식 4열 그리드 — 넉넉한 여백 */
.grid{ display:grid; grid-template-columns:repeat(4, 1fr); gap:36px 22px; }

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

@media (max-width:1080px){ .grid{ grid-template-columns:repeat(3, 1fr); } }
@media (max-width:780px){ .grid{ grid-template-columns:repeat(2, 1fr); gap:28px 16px; } }
@media (max-width:430px){ .grid{ grid-template-columns:repeat(2, 1fr); } }

/* 마감임박 특가 배너 (빨간/코랄 박스) */
.sec{ padding-top:46px; }
.deal-banner{ position:relative; overflow:hidden; border-radius:22px; border:1px solid var(--deal-soft);
  background:linear-gradient(120deg,#fbe9e3,#f7ddd4); display:flex; align-items:center;
  justify-content:space-between; gap:24px; padding:34px 40px; min-height:172px; }
.deal-banner .eyebrow{ display:inline-flex; align-items:center; gap:7px; background:#fff; color:var(--deal);
  font-weight:700; font-size:12.5px; padding:6px 13px; border-radius:999px; margin-bottom:14px; }
.deal-banner h2{ margin:0 0 8px; font-size:28px; font-weight:800; letter-spacing:-.03em; color:#5a1e13; line-height:1.2; }
.deal-banner p{ margin:0; font-size:14.5px; color:#7a3326; }
.db-go{ display:inline-flex; align-items:center; gap:8px; background:var(--deal); color:#fff; font-weight:700;
  font-size:15px; padding:13px 24px; border-radius:11px; white-space:nowrap; box-shadow:0 8px 18px rgba(214,69,47,.3); }
.db-go svg{ width:16px; height:16px; }
@media (max-width:780px){ .deal-banner{ flex-direction:column; align-items:flex-start; } }
</style>
