<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { won, thumbEmoji, categoryLabel, dDayLabel, riskMeta } from '../utils/format'
import { useWishlistStore } from '../stores/wishlist'
import { useAuthStore } from '../stores/auth'
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

// 떨이가 적용은 장바구니 스토어가 일괄 처리(원본 상품 그대로 전달)
function add() {
  emit('add', props.product)
}
</script>

<template>
  <div class="product-card card">
    <router-link :to="{ name: 'product-detail', params: { id: product.productId } }" class="thumb">
      <span class="emoji">{{ emoji }}</span>
      <!-- 좌상단: 유통기한 D-day -->
      <span v-if="product.daysToExpiry != null" class="dday" :class="risk.cls">
        {{ dDayLabel(product.daysToExpiry) }}
      </span>
      <!-- 우상단: 할인율 -->
      <span v-if="hasDeal" class="rate">{{ product.discountRate }}%</span>
      <span v-if="soldOut" class="soldout-tag">품절</span>
      <button v-if="!auth.isSeller" class="wish" :class="{ on: wished }" :title="wished ? '찜 해제' : '찜하기'" @click.prevent="toggleWish">
        {{ wished ? '♥' : '♡' }}
      </button>
    </router-link>

    <div class="body">
      <div class="tags">
        <span class="badge">{{ categoryLabel(product.category) }}</span>
        <span class="risk-chip" :class="risk.cls">{{ risk.label }}</span>
      </div>
      <router-link :to="{ name: 'product-detail', params: { id: product.productId } }" class="name">
        {{ product.name }}
      </router-link>

      <!-- 가격: 떨이 시 정가 취소선 + 떨이가 -->
      <div class="price-row">
        <template v-if="hasDeal">
          <span class="deal-rate">{{ product.discountRate }}%</span>
          <span class="deal-price">{{ won(dealPrice) }}</span>
          <span class="orig-price">{{ won(product.price) }}</span>
        </template>
        <span v-else class="deal-price">{{ won(product.price) }}</span>
      </div>

      <div class="meta">
        <span class="muted">재고 {{ product.stockQty }}개</span>
        <span v-if="product.averageRating" class="rating">
          <StarRating :rating="product.averageRating" />
          <span class="muted">{{ product.averageRating }}</span>
        </span>
      </div>
      <button class="btn btn-outline btn-block add-btn" :disabled="soldOut" @click="add">
        {{ soldOut ? '품절' : '🛒 담기' }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.product-card { overflow: hidden; transition: box-shadow 0.15s ease, transform 0.15s ease; }
.product-card:hover { box-shadow: var(--shadow-hover); transform: translateY(-2px); }
.thumb {
  position: relative;
  display: flex; align-items: center; justify-content: center;
  height: 140px; background: var(--color-primary-soft);
}
.thumb .emoji { font-size: 64px; }

/* D-day 뱃지 (위험도 색상) */
.dday {
  position: absolute; top: 10px; left: 10px;
  font-size: 12px; font-weight: 800; color: #fff;
  padding: 3px 9px; border-radius: 999px;
  background: #9aa0a6;
}
.dday.risk-high { background: #e5484d; }
.dday.risk-medium { background: #f59e0b; }
.dday.risk-low { background: #7a8085; }
.dday.risk-expired { background: #6b7280; }

/* 할인율 뱃지 */
.rate {
  position: absolute; top: 10px; right: 10px;
  background: #e5484d; color: #fff; font-size: 13px; font-weight: 800;
  padding: 3px 9px; border-radius: 999px;
}
.soldout-tag {
  position: absolute; bottom: 10px; left: 10px;
  background: rgba(0,0,0,0.6); color: #fff; font-size: 12px;
  padding: 2px 8px; border-radius: 6px;
}
.wish {
  position: absolute; bottom: 8px; right: 8px;
  width: 34px; height: 34px; border-radius: 50%;
  border: none; background: rgba(255,255,255,0.9); box-shadow: var(--shadow);
  font-size: 18px; line-height: 1; color: #c9ccd1; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: transform 0.12s ease, color 0.12s ease;
}
.wish:hover { transform: scale(1.1); }
.wish.on { color: #e5484d; }

.body { padding: 14px; display: flex; flex-direction: column; gap: 7px; }
.tags { display: flex; align-items: center; gap: 6px; }
.risk-chip { font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 999px; }
.risk-chip.risk-high { background: #fdecec; color: #c1272d; }
.risk-chip.risk-medium { background: #fef3e2; color: #b76e00; }
.risk-chip.risk-low { background: #eef1f3; color: #7a8085; }
.risk-chip.risk-expired { background: #eef1f3; color: #6b7280; }

.name { font-size: 15px; font-weight: 700; line-height: 1.3; min-height: 20px; }
.name:hover { color: var(--color-primary-dark); }

.price-row { display: flex; align-items: baseline; gap: 8px; flex-wrap: wrap; }
.deal-rate { color: #e5484d; font-weight: 800; font-size: 16px; }
.deal-price { font-size: 19px; font-weight: 800; color: var(--color-text); }
.orig-price { font-size: 13px; color: var(--color-muted); text-decoration: line-through; }

.meta { display: flex; align-items: center; justify-content: space-between; font-size: 13px; }
.rating { display: inline-flex; align-items: center; gap: 4px; }
.add-btn { margin-top: 4px; }
</style>
