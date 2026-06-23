<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { productApi } from '../api/products'
import { useCartStore } from '../stores/cart'
import { won, thumbEmoji, categoryLabel } from '../utils/format'

const router = useRouter()
const cart = useCartStore()

const products = ref([])
const loading = ref(true)
const error = ref('')

// 카테고리 탭 (전체 + 백엔드 코드). 라벨은 categoryLabel(code).
const TAB_CODES = ['all', 'vegetable', 'fruit', 'seafood', 'meat', 'grain', 'processed']
const activeTab = ref('all')

onMounted(load)
async function load() {
  loading.value = true
  error.value = ''
  try {
    // 응답은 인터셉터가 unwrap → res 가 곧 Page. 목록은 res.content.
    const res = await productApi.list({ page: 0, size: 50 })
    products.value = res.content || []
  } catch (e) {
    error.value = e?.message || '상품을 불러오지 못했어요.'
  } finally {
    loading.value = false
  }
}

// 판매 순위 — 전용 집계 API가 없어 reviewCount(인기 프록시)·할인율로 정렬.
// 실제 판매수 필드가 생기면 score 계산만 교체하면 됨.
function score(p) {
  return (p.reviewCount ?? 0) * 100 + (p.discountRate ?? 0)
}
const ranked = computed(() => {
  let list = products.value.slice()
  if (activeTab.value !== 'all') list = list.filter((p) => p.category === activeTab.value)
  list.sort((a, b) => score(b) - score(a))
  return list.slice(0, 9)
})

const hasDeal = (p) => (p.discountRate ?? 0) > 0
const dealPrice = (p) => p.discountedPrice ?? p.price
const soldOut = (p) => (p.stockQty ?? 0) <= 0

function addToCart(p) {
  if (soldOut(p)) return
  // 폐기기간 옵션이 있으면 상세에서 선택
  if ((p.lotCount ?? 0) > 0) {
    router.push({ name: 'product-detail', params: { id: p.productId } })
    return
  }
  cart.add(p, 1)
}
</script>

<template>
  <div class="best container">
    <div class="best-hero">
      <span class="kick">실시간 판매 순위</span>
      <h1>베스트 TOP 9</h1>
      <p>지금 가장 많이 찾는 산지 직거래 신선식품</p>
    </div>

    <div class="best-tabs">
      <button
        v-for="code in TAB_CODES" :key="code"
        class="btab" :class="{ on: activeTab === code }"
        @click="activeTab = code"
      >{{ code === 'all' ? '전체' : categoryLabel(code) }} TOP9</button>
    </div>

    <div v-if="loading" class="empty"><span class="emoji">⏳</span>순위를 불러오는 중…</div>
    <div v-else-if="error" class="empty"><span class="emoji">⚠️</span>{{ error }}<br /><button class="btn btn-outline" style="margin-top:12px" @click="load">다시 시도</button></div>
    <div v-else-if="ranked.length === 0" class="empty"><span class="emoji">🔍</span>표시할 상품이 없어요.</div>

    <div v-else class="best-grid">
      <article v-for="(p, i) in ranked" :key="p.productId" class="rank">
        <router-link :to="{ name: 'product-detail', params: { id: p.productId } }" class="rimg" :class="'t-' + p.category">
          <span class="emoji">{{ thumbEmoji(p) }}</span>
          <div v-if="soldOut(p)" class="soldout">품절</div>
        </router-link>
        <div class="rinfo">
          <div class="rno" :class="{ top: i < 3 }">{{ i + 1 }}</div>
          <router-link :to="{ name: 'product-detail', params: { id: p.productId } }" class="rnm">{{ p.name }}</router-link>
          <div class="rprice">
            <template v-if="hasDeal(p)">
              <span class="rwas">{{ won(p.price) }}</span>
              <span class="rdisc">{{ p.discountRate }}%</span>
              <span class="rnow">{{ won(dealPrice(p)) }}</span>
            </template>
            <template v-else>
              <span class="rnow">{{ won(p.price) }}</span>
            </template>
          </div>
          <button class="radd" :disabled="soldOut(p)" @click="addToCart(p)">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 3h2.2l2 13.4a1.5 1.5 0 0 0 1.5 1.3h9.7a1.5 1.5 0 0 0 1.5-1.2L21 7H5.5"/><circle cx="9" cy="21" r="1.3"/><circle cx="18" cy="21" r="1.3"/></svg>
            담기
          </button>
        </div>
      </article>
    </div>
  </div>
</template>

<style scoped>
.best{ padding-bottom:70px; }
.best-hero{ text-align:center; padding:38px 0 6px; }
.best-hero .kick{ display:inline-block; font-size:13px; font-weight:700; letter-spacing:.04em; color:var(--leaf-700); background:var(--leaf-50); padding:5px 13px; border-radius:999px; margin-bottom:13px; }
.best-hero h1{ margin:0 0 7px; font-size:32px; font-weight:800; letter-spacing:-.03em; }
.best-hero p{ margin:0; color:var(--muted); font-size:14.5px; }

.best-tabs{ display:flex; gap:10px; overflow-x:auto; justify-content:center; padding:26px 4px 30px; }
.btab{ flex:none; padding:12px 22px; border-radius:999px; border:none; background:#f1f1ea; font-size:15px; font-weight:700; color:var(--ink-2); white-space:nowrap; transition:.14s; }
.btab:hover{ background:var(--leaf-50); color:var(--leaf-700); }
.btab.on{ background:var(--leaf-700); color:#fff; }

.best-grid{ display:grid; grid-template-columns:repeat(3,1fr); gap:30px 32px; }
.rank{ display:grid; grid-template-columns:122px 1fr; gap:16px; }
.rank .rimg{ position:relative; aspect-ratio:1/1; border-radius:14px; overflow:hidden; background:#f4f5f3; display:flex; align-items:center; justify-content:center; }
.rank .rimg .emoji{ font-size:52px; transition:transform .3s ease; }
.rank:hover .rimg .emoji{ transform:scale(1.06); }
.t-vegetable, .t-root, .t-mushroom{ background:#eef6e6; }
.t-fruit{ background:#fbf2e6; } .t-seafood{ background:#eaf2f7; } .t-meat{ background:#f8eeeb; } .t-grain{ background:#f6f1e3; }
.soldout{ position:absolute; inset:0; background:rgba(28,34,21,.45); display:flex; align-items:center; justify-content:center; color:#fff; font-weight:800; font-size:16px; }
.rinfo{ display:flex; flex-direction:column; min-width:0; }
.rno{ font-size:26px; font-weight:800; line-height:1; margin-bottom:8px; letter-spacing:-.02em; color:var(--ink); }
.rno.top{ color:var(--leaf-700); }
.rnm{ font-size:14.5px; font-weight:600; line-height:1.4; color:var(--ink-2); margin-bottom:10px; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; }
.rnm:hover{ color:var(--leaf-700); }
.rprice{ display:flex; align-items:baseline; gap:7px; flex-wrap:wrap; margin-bottom:13px; }
.rwas{ color:var(--faint); text-decoration:line-through; font-size:12.5px; }
.rdisc{ color:var(--deal); font-weight:800; font-size:16px; }
.rnow{ font-weight:800; font-size:17px; letter-spacing:-.02em; }
.radd{ margin-top:auto; display:flex; align-items:center; justify-content:center; gap:7px; height:42px; border-radius:10px; border:1.5px solid var(--line-2); background:#fff; font-weight:700; font-size:14px; color:var(--ink); transition:.15s; }
.radd:hover:not(:disabled){ border-color:var(--leaf-500); background:var(--leaf-50); color:var(--leaf-700); }
.radd:disabled{ opacity:.45; cursor:not-allowed; }
.radd svg{ width:16px; height:16px; }

@media (max-width:1080px){ .best-grid{ grid-template-columns:repeat(2,1fr); } }
@media (max-width:680px){ .best-grid{ grid-template-columns:1fr; } }
</style>
