<script setup>
// 챌린지 상태 배지(진행 중 D-day / 기간 만료 / 달성 완료).
// status는 utils/format.js의 challengeStatus()가 돌려주는 객체.
defineProps({ status: { type: Object, required: true } })
</script>

<template>
  <span class="st-badge" :class="status.cls">
    {{ status.emoji }} {{ status.label }}
    <span v-if="status.key === 'ONGOING'" class="dday">· {{ status.dday }}</span>
  </span>
</template>

<style scoped>
.st-badge {
  display: inline-flex; align-items: center; gap: 4px;
  font-size: 13px; font-weight: 700;
  padding: 4px 10px; border-radius: 999px; white-space: nowrap;
}
.st-badge .dday { font-weight: 800; }
.st-ongoing { background: var(--color-primary-soft); color: var(--color-primary-dark); }
.st-expired { background: #f0f0f0; color: #888; }
.st-done { background: #fff4d6; color: #b8860b; }
</style>
