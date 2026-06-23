<script setup>
import { computed, ref } from 'vue'
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
// 실사진(thumbnailUrl)이 있으면 사진, 없거나 로드 실패 시 이모지 폴백
const imgError = ref(false)
const showImg = computed(() => !!props.product.thumbnailUrl && !imgError.value)
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
// 폐기기간 옵션(lot)이 있으면 카드에서 바로 담지 않고 상세에서 옵션을 고르게 한다.
const hasLots = computed(() => (props.product.lotCount ?? 0) > 0)

function add() {
  if (soldOut.value || isExpired.value) return
  if (hasLots.value) {
    onOpen()
    router.push({ name: 'product-detail', params: { id: props.product.productId } })
    return
  }
  emit('add', props.product)
}

// 퍼널 2단계 — 상품 카드 클릭(상세 진입 직전)
function onOpen() {
  track('click_product', { productId: props.product.productId, abTestGroup: props.product.abVariant })
}
</script>

<template>
  <article class="pcard">
    <router-link :to="{ name: 'product-detail', params: { id: product.productId } }" class="thumb" :class="'t-' + product.category" @click="onOpen">
      <img v-if="showImg" class="photo" :src="product.thumbnailUrl" :alt="product.name" loading="lazy" @error="imgError = true" />
      <span v-else class="emoji">{{ emoji }}</span>
      <!-- 마감임박(USP)만 작은 태그로 -->
      <span v-if="risk.cls === 'risk-high' || risk.cls === 'risk-medium'" class="dday" :class="risk.cls">
        {{ dDayLabel(product.daysToExpiry) }}
      </span>
      <div v-if="soldOut" class="soldout">품절</div>
      <!-- 호버 액션: 찜 · 담기(컬리식 장바구니 아이콘) -->
      <div v-else class="acts">
        <button class="act like" :class="{ on: wished }" :title="wished ? '찜 해제' : '찜하기'" @click.prevent="toggleWish">
          <svg viewBox="0 0 24 24" :fill="wished ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="2"><path d="M19 14c1.5-1.5 3-3.3 3-5.5A4.5 4.5 0 0 0 12 6 4.5 4.5 0 0 0 2 8.5C2 13 12 21 12 21s4-3.2 7-7Z"/></svg>
        </button>
        <button v-if="!auth.isSeller" class="act cart" :disabled="isExpired" :title="hasLots ? '가격 확인' : '담기'" @click.prevent="add">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 3h2.2l2 13.4a1.5 1.5 0 0 0 1.5 1.3h9.7a1.5 1.5 0 0 0 1.5-1.2L21 7H5.5"/><circle cx="9" cy="21" r="1.3"/><circle cx="18" cy="21" r="1.3"/></svg>
        </button>
      </div>
    </router-link>

    <router-link :to="{ name: 'product-detail', params: { id: product.productId } }" class="name" @click="onOpen">
      {{ product.name }}
    </router-link>

    <div class="price">
      <template v-if="hasDeal">
        <span class="pct">{{ product.discountRate }}%</span>
        <span class="now">{{ won(dealPrice) }}</span>
        <span class="was">{{ won(product.price) }}</span>
      </template>
      <template v-else>
        <span v-if="hasLots" class="from">최저</span>
        <span class="now">{{ won(product.price) }}</span>
      </template>
    </div>

    <div class="sub">
      <span v-if="product.reviewCount" class="rating">
        <StarRating :rating="product.avgRating" size="13px" />
        <span class="muted">{{ Number(product.avgRating).toFixed(1) }} ({{ product.reviewCount }})</span>
      </span>
      <span v-if="hasLots" class="lotbadge">가격 {{ product.lotCount }}옵션</span>
    </div>
  </article>
</template>

<style scoped>
/* 컬리식 클린 카드 — 테두리·그림자 없이 이미지+텍스트만 */
.pcard{ display:flex; flex-direction:column; }

.thumb{
  position:relative; aspect-ratio:1 / 1; border-radius:12px; overflow:hidden;
  display:flex; align-items:center; justify-content:center;
  background:#f4f5f3;
}
.thumb .emoji{ font-size:62px; transition:transform .3s ease; }
.thumb .photo{ width:100%; height:100%; object-fit:cover; transition:transform .3s ease; }
.pcard:hover .thumb .emoji,
.pcard:hover .thumb .photo{ transform:scale(1.06); }

/* 카테고리별 옅은 틴트 (깔끔하게 단색에 가깝게) */
.t-vegetable, .t-root, .t-mushroom{ background:#eef6e6; }
.t-fruit{ background:#fbf2e6; }
.t-seafood{ background:#eaf2f7; }
.t-meat{ background:#f8eeeb; }
.t-grain{ background:#f6f1e3; }

.dday{
  position:absolute; top:10px; left:10px;
  font-size:11.5px; font-weight:700; padding:3px 9px; border-radius:7px;
  color:#fff; white-space:nowrap;
}
.dday.risk-high{ background:var(--deal); }
.dday.risk-medium{ background:var(--gold); }

.soldout{
  position:absolute; inset:0; background:rgba(28,34,21,.45);
  display:flex; align-items:center; justify-content:center;
  color:#fff; font-weight:800; font-size:17px;
}

/* 호버 시 나타나는 액션 (찜·담기) */
.acts{
  position:absolute; right:10px; bottom:10px; display:flex; gap:7px;
  opacity:0; transform:translateY(4px); transition:.16s;
}
.pcard:hover .acts{ opacity:1; transform:none; }
.act{
  width:36px; height:36px; border-radius:50%; border:none;
  background:#fff; box-shadow:0 3px 10px rgba(0,0,0,.16);
  display:flex; align-items:center; justify-content:center; transition:.14s;
}
.act svg{ width:18px; height:18px; }
.act.like{ color:var(--faint); }
.act.like:hover{ color:var(--deal); }
.act.like.on{ color:var(--deal); }
.act.cart{ color:var(--leaf-700); }
.act.cart:hover{ background:var(--leaf-600); color:#fff; }
.act:disabled{ opacity:.4; cursor:not-allowed; }

.name{
  display:block; margin:13px 0 7px; font-size:15px; font-weight:600;
  line-height:1.4; color:var(--ink); letter-spacing:-.01em;
  display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden;
}
.name:hover{ color:var(--leaf-700); }

.price{ display:flex; align-items:baseline; gap:6px; flex-wrap:wrap; }
.pct{ color:var(--deal); font-weight:800; font-size:16px; }
.now{ font-weight:800; font-size:18px; color:var(--ink); letter-spacing:-.02em; }
.was{ color:var(--faint); text-decoration:line-through; font-size:13px; }
.from{ font-size:12.5px; color:var(--muted); font-weight:600; }

.sub{ display:flex; align-items:center; gap:8px; margin-top:9px; min-height:18px; flex-wrap:wrap; }
.rating{ display:inline-flex; align-items:center; gap:5px; font-size:12px; }
.lotbadge{ font-size:11px; font-weight:600; color:var(--leaf-700); background:var(--leaf-50); padding:2px 8px; border-radius:6px; }
</style>
