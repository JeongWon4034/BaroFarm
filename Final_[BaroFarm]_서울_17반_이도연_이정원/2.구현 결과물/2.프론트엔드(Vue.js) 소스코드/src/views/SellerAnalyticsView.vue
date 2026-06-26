<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useAuthStore } from '../stores/auth'

// 내 seller_id를 URL 파라미터로 Streamlit에 전달 → 내 농장 데이터만 표시.
const auth = useAuthStore()
const base = import.meta.env.VITE_STREAMLIT_URL || 'http://localhost:8501'
const SRC = computed(() => `${base}/?seller_id=${auth.user?.userId ?? auth.user?.id ?? ''}&embed=true`)

const loaded = ref(false)
const failed = ref(false)
const frameKey = ref(0)
let timer = null

function startWatch() {
  loaded.value = false
  failed.value = false
  clearTimeout(timer)
  timer = setTimeout(() => { if (!loaded.value) failed.value = true }, 14000)
}
function onLoad() { loaded.value = true; clearTimeout(timer) }
function retry()  { frameKey.value++; startWatch() }

onMounted(startWatch)
onBeforeUnmount(() => clearTimeout(timer))
</script>

<template>
  <div class="seller-analytics">
    <div class="head">
      <h1>📊 내 농장 분석 대시보드</h1>
      <p class="muted">{{ auth.user?.name }} 농장의 매출·고객·재고 데이터를 실시간으로 확인하세요</p>
    </div>

    <div class="frame-wrap">
      <div v-if="failed" class="frame-loading">
        <span class="emoji">🔌</span>
        <p>대시보드 서버에 연결할 수 없어요.<br /><small>분석 서버가 준비 중이거나 꺼져 있어요. 잠시 후 다시 시도해 주세요.</small></p>
        <button class="btn btn-outline" @click="retry">다시 시도</button>
      </div>
      <div v-else-if="!loaded" class="frame-loading">
        <span class="spin"></span>
        <p>내 농장 대시보드를 불러오는 중…<br /><small>처음엔 잠시 걸릴 수 있어요</small></p>
      </div>
      <iframe
        :key="frameKey"
        :src="SRC"
        class="frame"
        title="내 농장 분석 대시보드"
        @load="onLoad"
      />
    </div>
  </div>
</template>

<style scoped>
.seller-analytics { padding-bottom: 40px; }
.head { margin-bottom: 16px; }
.head h1 { font-size: 24px; font-weight: 800; letter-spacing: -.02em; margin: 0 0 4px; }
.head .muted { color: var(--muted); font-size: 14px; margin: 0; }

.frame-wrap { position: relative; }
.frame {
  width: 100%; height: calc(100vh - 230px); min-height: 640px;
  border: 1px solid var(--line); border-radius: 16px; background: #fff; display: block;
}
.frame-loading {
  position: absolute; inset: 0; display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 14px; color: var(--muted);
  border: 1px solid var(--line); border-radius: 16px; background: var(--cream);
}
.frame-loading small { color: var(--faint); font-size: 12.5px; }
.spin {
  width: 34px; height: 34px; border-radius: 50%;
  border: 3px solid var(--leaf-100); border-top-color: var(--leaf-600);
  animation: sp .8s linear infinite;
}
@keyframes sp { to { transform: rotate(360deg) } }
</style>
