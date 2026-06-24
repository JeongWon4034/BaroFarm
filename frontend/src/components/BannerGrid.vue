<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({
  images:   { type: Array,  required: true },
  perPage:  { type: Number, default: 4 },    // 한 번에 보여줄 이미지 수
  autoplay: { type: Number, default: 3000 }, // ms, 0이면 자동넘김 없음
})

const page = ref(0)
const totalPages = computed(() => Math.max(1, Math.ceil(props.images.length / props.perPage)))
const currentSlice = computed(() => {
  const s = page.value * props.perPage
  return props.images.slice(s, s + props.perPage)
})

function go(i)  { page.value = (i + totalPages.value) % totalPages.value }
function next() { go(page.value + 1) }
function prev() { go(page.value - 1) }

let timer = null
function start() {
  if (props.autoplay > 0 && totalPages.value > 1) {
    stop(); timer = setInterval(next, props.autoplay)
  }
}
function stop() { if (timer) { clearInterval(timer); timer = null } }

onMounted(start)
onBeforeUnmount(stop)
</script>

<template>
  <div v-if="images.length" class="bg-wrap" @mouseenter="stop" @mouseleave="start">
    <div class="grid">
      <div v-for="(src, i) in currentSlice" :key="src" class="cell">
        <img :src="src" :alt="`배너 ${page * perPage + i + 1}`" />
      </div>
      <!-- 마지막 페이지가 홀수 개일 때 빈 칸 채움 -->
      <div v-if="currentSlice.length % 2 !== 0" class="cell cell-empty" />
    </div>

    <div v-if="totalPages > 1" class="controls">
      <button class="arr" @click="prev" aria-label="이전">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="m15 6-6 6 6 6"/></svg>
      </button>
      <div class="dots">
        <button
          v-for="n in totalPages" :key="n"
          :class="{ on: n - 1 === page }"
          @click="go(n - 1)"
          :aria-label="`${n}페이지`"
        />
      </div>
      <button class="arr" @click="next" aria-label="다음">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="m9 6 6 6-6 6"/></svg>
      </button>
    </div>
  </div>

  <div v-else class="empty">이미지를 폴더에 추가하면 자동으로 표시됩니다</div>
</template>

<style scoped>
.bg-wrap { display: flex; flex-direction: column; gap: 14px; }

.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.cell {
  border-radius: 16px;
  overflow: hidden;
  aspect-ratio: 2 / 1;
  background: var(--leaf-50);
}
.cell img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform .25s;
}
.cell img:hover { transform: scale(1.03); }
.cell-empty { background: transparent; }

.controls {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}
.arr {
  width: 34px; height: 34px;
  border-radius: 50%; border: 1.5px solid var(--line);
  background: #fff; color: var(--ink-2);
  display: flex; align-items: center; justify-content: center;
  transition: .14s; cursor: pointer;
}
.arr:hover { border-color: var(--leaf-400); color: var(--leaf-700); }

.dots { display: flex; gap: 6px; }
.dots button {
  width: 8px; height: 8px;
  border-radius: 999px; border: none; padding: 0;
  background: var(--line); transition: .2s; cursor: pointer;
}
.dots button.on { width: 22px; background: var(--leaf-600); }

.empty {
  padding: 32px;
  text-align: center;
  color: var(--muted);
  font-size: 14px;
  border: 1.5px dashed var(--line);
  border-radius: 16px;
}

@media (max-width: 600px) {
  .grid { grid-template-columns: 1fr; }
}
</style>
