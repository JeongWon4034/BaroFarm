<script setup>
import { computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import { REFLEX_URL } from '../config'

const auth = useAuthStore()
const dashboardUrl = computed(() =>
  `${REFLEX_URL}/?seller_id=${auth.user?.userId ?? ''}`
)
</script>

<template>
  <div class="seller-analytics">
    <div class="head">
      <h1>📊 내 농장 분석 대시보드</h1>
      <p class="muted">{{ auth.user?.name }} 농장의 매출·재고·공급망 데이터를 확인하세요</p>
      <a :href="dashboardUrl" target="_blank" rel="noopener noreferrer" class="open-btn">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
          <polyline points="15 3 21 3 21 9"/>
          <line x1="10" y1="14" x2="21" y2="3"/>
        </svg>
        새 창으로 열기
      </a>
    </div>

    <div class="frame-wrap">
      <iframe
        :src="dashboardUrl"
        class="frame"
        title="내 농장 분석 대시보드"
      />
    </div>
  </div>
</template>

<style scoped>
.seller-analytics { padding-bottom: 40px; }
.head {
  display: flex; align-items: center; gap: 12px;
  flex-wrap: wrap; margin-bottom: 16px;
}
.head h1 { font-size: 24px; font-weight: 800; letter-spacing: -.02em; margin: 0; flex: none; }
.head .muted { color: var(--muted); font-size: 14px; margin: 0; flex: 1; min-width: 0; }

.open-btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 9px 16px; border-radius: 10px;
  background: var(--leaf-600); color: #fff;
  font-size: 13.5px; font-weight: 700;
  text-decoration: none; flex-shrink: 0;
  transition: background .14s;
}
.open-btn:hover { background: var(--leaf-700); }

.frame-wrap { position: relative; }
.frame {
  width: 100%; height: calc(100vh - 200px); min-height: 640px;
  border: 1px solid var(--line); border-radius: 16px;
  background: #fff; display: block;
}
</style>
