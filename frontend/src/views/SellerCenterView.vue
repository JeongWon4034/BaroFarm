<script setup>
import { useAuthStore } from '../stores/auth'
import { useNotificationStore } from '../stores/notification'

const auth = useAuthStore()
const noti = useNotificationStore()

// 판매자 전용 개인 메뉴 허브 — 공개 쇼핑 메뉴와 분리된 관리 기능 모음.
const menus = [
  {
    name: 'seller-products',
    title: '상품 관리',
    desc: '내 상품 등록·수정·삭제, 폐기위험/할인가 확인',
    icon: 'box',
  },
  {
    name: 'seller-orders',
    title: '주문 관리',
    desc: '들어온 주문을 확인 → 배송 → 완료까지 처리',
    icon: 'clipboard',
  },
  {
    name: 'seller-dashboard',
    title: '판매자 대시보드',
    desc: '재고 폐기위험과 AI 추천 할인가를 한눈에',
    icon: 'chart',
  },
]
</script>

<template>
  <div class="hub">
    <div class="hub-head">
      <h1>🏪 판매자 센터</h1>
      <p class="muted">{{ auth.user?.name }}님의 판매 관리 메뉴</p>
    </div>

    <div class="grid">
      <router-link v-for="m in menus" :key="m.name" :to="{ name: m.name }" class="tile card">
        <span class="ic">
          <svg v-if="m.icon === 'box'" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M21 8 12 3 3 8l9 5 9-5Z"/><path d="M3 8v8l9 5 9-5V8"/><path d="M12 13v8"/></svg>
          <svg v-else-if="m.icon === 'clipboard'" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><rect x="8" y="3" width="8" height="4" rx="1"/><path d="M16 5h2a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2h2"/><path d="M9 12h6M9 16h4"/></svg>
          <svg v-else width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="M7 15l3-4 3 2 4-6"/></svg>
        </span>
        <div class="tx">
          <div class="t">
            {{ m.title }}
            <span v-if="m.name === 'seller-orders' && noti.count" class="tile-badge">{{ noti.count }}</span>
          </div>
          <div class="d">{{ m.desc }}</div>
        </div>
        <svg class="arr" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg>
      </router-link>
    </div>
  </div>
</template>

<style scoped>
.hub-head { margin-bottom: 22px; }
.hub-head h1 { font-size: 23px; margin: 0 0 4px; }

.grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
@media (max-width: 760px) { .grid { grid-template-columns: 1fr; } }

.tile {
  display: flex; align-items: center; gap: 15px; padding: 20px;
  transition: transform .08s ease, box-shadow .15s ease, border-color .15s ease;
}
.tile:hover { transform: translateY(-2px); box-shadow: var(--shadow-md); border-color: var(--leaf-300); }
.ic {
  width: 50px; height: 50px; flex-shrink: 0; border-radius: 14px;
  background: var(--leaf-50); color: var(--leaf-700);
  display: flex; align-items: center; justify-content: center;
}
.tx { flex: 1; min-width: 0; }
.tx .t { font-size: 16px; font-weight: 800; color: var(--ink); }
.tile-badge {
  display: inline-flex; align-items: center; justify-content: center;
  min-width: 18px; height: 18px; padding: 0 5px; margin-left: 5px;
  border-radius: 9px; background: var(--deal); color: #fff;
  font-size: 11px; font-weight: 700; vertical-align: middle;
}
.tx .d { font-size: 13px; color: var(--muted); margin-top: 3px; line-height: 1.4; }
.arr { color: var(--faint); flex-shrink: 0; }
.tile:hover .arr { color: var(--leaf-600); }
</style>
