<script setup>
import { computed } from 'vue'
import { won, thumbEmoji, categoryLabel } from '../utils/format'
import StarRating from './StarRating.vue'

const props = defineProps({
  product: { type: Object, required: true },
})
const emit = defineEmits(['add'])

const emoji = computed(() => thumbEmoji(props.product))
const soldOut = computed(() => (props.product.stockQty ?? 0) <= 0)
</script>

<template>
  <div class="product-card card">
    <router-link :to="{ name: 'product-detail', params: { id: product.productId } }" class="thumb">
      <span class="emoji">{{ emoji }}</span>
      <span v-if="soldOut" class="soldout-tag">품절</span>
    </router-link>

    <div class="body">
      <span class="badge">{{ categoryLabel(product.category) }}</span>
      <router-link :to="{ name: 'product-detail', params: { id: product.productId } }" class="name">
        {{ product.name }}
      </router-link>
      <div class="price">{{ won(product.price) }}</div>
      <div class="meta">
        <span class="muted">재고 {{ product.stockQty }}개</span>
        <span v-if="product.averageRating" class="rating">
          <StarRating :rating="product.averageRating" />
          <span class="muted">{{ product.averageRating }}</span>
        </span>
      </div>
      <button class="btn btn-outline btn-block add-btn" :disabled="soldOut" @click="emit('add', product)">
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
.soldout-tag {
  position: absolute; top: 10px; left: 10px;
  background: rgba(0,0,0,0.6); color: #fff; font-size: 12px;
  padding: 2px 8px; border-radius: 6px;
}
.body { padding: 14px; display: flex; flex-direction: column; gap: 7px; }
.name { font-size: 15px; font-weight: 700; line-height: 1.3; min-height: 20px; }
.name:hover { color: var(--color-primary-dark); }
.price { font-size: 18px; }
.meta { display: flex; align-items: center; justify-content: space-between; font-size: 13px; }
.rating { display: inline-flex; align-items: center; gap: 4px; }
.add-btn { margin-top: 4px; }
</style>
