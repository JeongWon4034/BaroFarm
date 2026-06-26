<script setup>
const props = defineProps({
  rating: { type: Number, default: 0 },
  size: { type: String, default: '14px' },
})
// 각 별(1~5)의 금색 채움 비율 — full=100%, half=50%, empty=0%
function fill(i) {
  const r = props.rating || 0
  if (r >= i) return '100%'
  if (r >= i - 0.5) return '50%'
  return '0%'
}
</script>

<template>
  <span class="stars" :style="{ fontSize: size }">
    <span v-for="i in 5" :key="i" class="star">
      ★<span class="fill" :style="{ width: fill(i) }">★</span>
    </span>
  </span>
</template>

<style scoped>
/* 옆 텍스트와 세로 정렬이 어긋나지 않도록 inline-flex + vertical-align + line-height 고정 */
.stars {
  display: inline-flex;
  align-items: center;
  vertical-align: middle;
  line-height: 1;
  flex-shrink: 0;
  gap: 1px;
}
/* 빈 별(회색) 위에 금색 별을 width로 잘라 겹쳐 반별 표현 — 글자 메트릭이 같아 정렬이 안정적 */
.star {
  position: relative;
  display: inline-block;
  color: #d6dade;
  line-height: 1;
}
.star .fill {
  position: absolute;
  left: 0;
  top: 0;
  overflow: hidden;
  white-space: nowrap;
  color: var(--color-star);
}
</style>
