<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { won, thumbEmoji, categoryLabel, dDayLabel, riskMeta } from '../utils/format'
import { useWishlistStore } from '../stores/wishlist'
import { useAuthStore } from '../stores/auth'
import { track } from '../api/track'
import StarRating from './StarRating.vue'

const props = defineProps({
  product: { type: Object, required: true },
})
const emit = defineEmits(['add'])

const router = useRouter()
const wishlist = useWishlistStore()
const auth = useAuthStore()

const emoji = computed(() => thumbEmoji(props.product))
const soldOut = computed(() => (props.product.stockQty ?? 0) <= 0)
const lowStock = computed(() => !soldOut.value && (props.product.stockQty ?? 0) <= 5)
// 유통기한 경과(마감) — 상세 페이지와 동일 기준. 장바구니 담기 불가.
const isExpired = computed(() => props.product.riskLevel === 'EXPIRED' || (props.product.daysToExpiry ?? 0) < 0)
const wished = computed(() => wishlist.isWished(props.product.productId))

async function toggleWish() {
  if (!auth.isLoggedIn) {
    router.push({ name: 'login' })
    return
  }
  await wishlist.toggle(props.product.productId)
}

const hasDeal = computed(() => (props.product.discountRate ?? 0) > 0)
const dealPrice = computed(() => props.product.discountedPrice ?? props.product.price)
const risk = computed(() => riskMeta(props.product.riskLevel))

function add() {
  if (soldOut.value || isExpired.value) return
  emit('add', props.product)
}

// 퍼널 2단계 — 상품 카드 클릭(상세 진입 직전)
function onOpen() {
  track('click_product', { productId: props.product.productId, abTestGroup: props.product.abVariant })
}
</script>

<template>
  <article class="product-card">
    <router-link :to="{ name: 'product-detail', params: { id: product.productId } }" class="thumb" :class="'t-' + product.category" @click="onOpen">
      <!-- 좌상단: 유통기한 D-day (폐기위험 색상) -->
      <span v-if="product.daysToExpiry != null" class="dday" :class="risk.cls">
        <svg v-if="risk.cls === 'risk-high'" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M12 8v4l3 2"/><circle cx="12" cy="12" r="9"/></svg>
        {{ dDayLabel(product.daysToExpiry) }}
      </span>
      <!-- 우상단: 할인율 -->
      <span v-if="hasDeal" class="disc">{{ product.discountRate }}%</span>
      <span class="emoji">{{ emoji }}</span>
      <div v-if="soldOut" class="soldout">품절</div>
      <button v-else-if="!auth.isSeller" class="like" :class="{ on: wished }" :title="wished ? '찜 해제' : '찜하기'" @click.prevent="toggleWish">
        <svg viewBox="0 0 24 24" :fill="wished ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="2"><path d="M19 14c1.5-1.5 3-3.3 3-5.5A4.5 4.5 0 0 0 12 6 4.5 4.5 0 0 0 2 8.5C2 13 12 21 12 21s4-3.2 7-7Z"/></svg>
      </button>
    </router-link>

    <div class="body">
      <div class="chips">
        <span class="chip">{{ categoryLabel(product.category) }}</span>
        <span class="risk-chip" :class="risk.cls">{{ risk.label }}</span>
      </div>
      <router-link :to="{ name: 'product-detail', params: { id: product.productId } }" class="name" @click="onOpen">
        {{ product.name }}
      </router-link>

      <div class="price-row">
        <template v-if="hasDeal">
          <span class="pct">{{ product.discountRate }}%</span>
          <span class="now">{{ won(dealPrice) }}</span>
          <span class="was">{{ won(product.price) }}</span>
        </template>
        <span v-else class="now">{{ won(product.price) }}</span>
      </div>

      <div class="meta">
        <span class="stock" :class="{ low: lowStock }">
          {{ soldOut ? '품절' : (lowStock ? '단 ' + product.stockQty + '개 남음' : '재고 ' + product.stockQty + '개') }}
        </span>
        <span v-if="product.reviewCount" class="rating">
          <StarRating :rating="product.avgRating" />
          <span class="muted">{{ Number(product.avgRating).toFixed(1) }} ({{ product.reviewCount }})</span>
        </span>
      </div>
    </div>

    <button class="add" :disabled="soldOut || isExpired" @click="add">
      <svg v-if="!soldOut && !isExpired" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 3h2.2l2 13.4a1.5 1.5 0 0 0 1.5 1.3h9.7a1.5 1.5 0 0 0 1.5-1.2L21 7H5.5"/><circle cx="9" cy="21" r="1.3"/><circle cx="18" cy="21" r="1.3"/></svg>
      {{ soldOut ? '품절' : isExpired ? '판매 마감' : '담기' }}
    </button>
  </article>
</template>

<style scoped>
.product-card{
  background:#fff; border:1px solid var(--line); border-radius:var(--r-card);
  overflow:hidden; display:flex; flex-direction:column;
  box-shadow:var(--shadow-sm);
  transition:transform .2s cubic-bezier(.2,.7,.3,1), box-shadow .2s;
}
.product-card:hover{ transform:translateY(-5px); box-shadow:var(--shadow-lg); }

.thumb{
  position:relative; aspect-ratio:1 / .92;
  display:flex; align-items:center; justify-content:center; overflow:hidden;
}
.thumb .emoji{ font-size:60px; transition:transform .25s ease; filter:drop-shadow(0 10px 12px rgba(40,40,20,.16)); }
.product-card:hover .thumb .emoji{ transform:scale(1.08) rotate(-2deg); }

/* 카테고리별 타일 틴트 */
.t-vegetable, .t-root, .t-mushroom{ background:radial-gradient(circle at 50% 36%, #f0f8e1, #e0efcd); }
.t-fruit{ background:radial-gradient(circle at 50% 36%, #fdf3e2, #f9e7cc); }
.t-seafood{ background:radial-gradient(circle at 50% 36%, #e9f2f7, #d8e8f1); }
.t-meat{ background:radial-gradient(circle at 50% 36%, #fbedea, #f4ddd7); }
.t-grain{ background:radial-gradient(circle at 50% 36%, #f8f3e0, #efe6c9); }

.dday{
  position:absolute; top:12px; left:12px;
  display:inline-flex; align-items:center; gap:5px;
  font-size:12px; font-weight:700; padding:4px 10px; border-radius:999px;
  color:#fff; white-space:nowrap; background:rgba(30,38,20,.55);
}
.dday.risk-high{ background:var(--deal); box-shadow:0 4px 10px rgba(214,69,47,.3); }
.dday.risk-medium{ background:var(--gold); }
.dday.risk-low{ background:rgba(30,38,20,.55); }
.dday.risk-expired{ background:#6b7280; }

.disc{
  position:absolute; top:12px; right:12px;
  background:#fff; color:var(--deal); font-weight:800; font-size:14.5px;
  padding:3px 10px; border-radius:9px; box-shadow:var(--shadow-sm);
}
.soldout{
  position:absolute; inset:0; background:rgba(28,34,21,.5);
  display:flex; align-items:center; justify-content:center;
  color:#fff; font-weight:800; font-size:18px; letter-spacing:.02em;
}
.like{
  position:absolute; bottom:12px; right:12px; width:34px; height:34px; border-radius:50%;
  background:rgba(255,255,255,.92); border:1px solid var(--line);
  display:flex; align-items:center; justify-content:center; color:var(--faint);
  transition:.15s; box-shadow:var(--shadow-sm);
}
.like:hover{ color:var(--deal); transform:scale(1.08); }
.like.on{ color:var(--deal); background:#fff; }
.like svg{ width:17px; height:17px; }

.body{ padding:14px 15px 16px; display:flex; flex-direction:column; gap:9px; flex:1; }
.chips{ display:flex; gap:6px; flex-wrap:wrap; align-items:center; }
.chip{
  font-size:11.5px; font-weight:600; padding:3px 9px; border-radius:7px;
  background:var(--leaf-50); color:var(--leaf-700); white-space:nowrap;
}
.risk-chip{ font-size:11.5px; font-weight:700; padding:3px 9px; border-radius:7px; white-space:nowrap; }
.risk-chip.risk-high{ background:var(--deal-soft); color:#bd3a26; }
.risk-chip.risk-medium{ background:var(--gold-soft); color:#9a6a1c; }
.risk-chip.risk-low{ background:#eef1ea; color:var(--muted); }
.risk-chip.risk-expired{ background:#eef1f3; color:#6b7280; }

.name{ font-size:16px; font-weight:700; line-height:1.32; letter-spacing:-.01em; }
.name:hover{ color:var(--leaf-700); }

.price-row{ display:flex; align-items:baseline; gap:8px; flex-wrap:wrap; margin-top:auto; }
.pct{ color:var(--deal); font-weight:800; font-size:16px; }
.now{ font-weight:800; font-size:21px; letter-spacing:-.02em; }
.was{ color:var(--faint); text-decoration:line-through; font-size:13px; }

.meta{ display:flex; align-items:center; justify-content:space-between; font-size:12.5px; }
.stock{ color:var(--muted); font-weight:500; }
.stock.low{ color:var(--deal); font-weight:700; }
.rating{ display:inline-flex; align-items:center; gap:5px; }

.add{
  margin:0 15px 15px; display:flex; align-items:center; justify-content:center; gap:8px;
  height:44px; border-radius:11px; border:1.5px solid var(--line-2); background:#fff;
  font-weight:700; font-size:14.5px; color:var(--ink); transition:.15s;
}
.add:hover:not(:disabled){ border-color:var(--leaf-500); background:var(--leaf-50); color:var(--leaf-700); }
.add:disabled{ opacity:.45; cursor:not-allowed; }
</style>
