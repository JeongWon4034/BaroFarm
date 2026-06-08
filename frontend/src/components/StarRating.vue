<script setup>
const props = defineProps({
  rating: { type: Number, default: 0 },
  size: { type: String, default: '14px' },
})
function star(i) {
  // i: 1~5
  if (props.rating >= i) return 'full'
  if (props.rating >= i - 0.5) return 'half'
  return 'empty'
}
</script>

<template>
  <span class="stars" :style="{ fontSize: size }">
    <span v-for="i in 5" :key="i" class="star" :class="star(i)">★</span>
  </span>
</template>

<style scoped>
.stars { display: inline-flex; letter-spacing: 1px; }
.star { color: #d6dade; }
.star.full { color: var(--color-star); }
.star.half {
  background: linear-gradient(90deg, var(--color-star) 50%, #d6dade 50%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}
</style>
