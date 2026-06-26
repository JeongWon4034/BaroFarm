<script setup>
import { useAuthStore } from '../stores/auth'
import { useNotificationStore } from '../stores/notification'

const auth = useAuthStore()
const noti = useNotificationStore()

// 구매자 전용 개인 메뉴 허브 — 공개 쇼핑 메뉴와 분리된 개인 기능 모음.
const menus = [
  {
    name: 'mypage',
    title: '마이페이지',
    desc: '구매 내역 확인과 리뷰 작성',
    icon: 'user',
  },
  {
    name: 'purchase-insights',
    title: '구매 분석',
    desc: '내 소비 패턴과 AI 장보기 추천',
    icon: 'chart',
  },
  {
    name: 'wishlist',
    title: '찜',
    desc: '관심 상품 모아보기 (할인가 반영)',
    icon: 'heart',
  },
  {
    name: 'following',
    title: '팔로잉',
    desc: '팔로우한 판매자의 상품 모아보기',
    icon: 'users',
  },
  {
    name: 'my-coupons',
    title: '내 쿠폰',
    desc: '챌린지로 받은 할인 쿠폰',
    icon: 'ticket',
  },
]
</script>

<template>
  <div class="hub">
    <div class="hub-head">
      <h1>🧺 내 메뉴</h1>
      <p class="muted">{{ auth.user?.name }}님의 쇼핑 개인 메뉴</p>
    </div>

    <div class="grid">
      <router-link v-for="m in menus" :key="m.name" :to="{ name: m.name }" class="tile card">
        <span class="ic">
          <svg v-if="m.icon === 'user'" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="4"/><path d="M5 21a7 7 0 0 1 14 0"/></svg>
          <svg v-else-if="m.icon === 'chart'" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="M7 15l3-4 3 2 4-6"/></svg>
          <svg v-else-if="m.icon === 'heart'" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M19 14c1.5-1.5 3-3.3 3-5.5A4.5 4.5 0 0 0 12 6 4.5 4.5 0 0 0 2 8.5C2 13 12 21 12 21s4-3.2 7-7Z"/></svg>
          <svg v-else-if="m.icon === 'ticket'" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M3 8a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2 2 2 0 0 0 0 4 2 2 0 0 1-2 2H5a2 2 0 0 1-2-2 2 2 0 0 0 0-4Z"/><path d="M13 6v12"/></svg>
          <svg v-else width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="8" r="3"/><path d="M3 20a6 6 0 0 1 12 0M16 6a3 3 0 0 1 0 6M21 20a6 6 0 0 0-4-5.6"/></svg>
        </span>
        <div class="tx">
          <div class="t">
            {{ m.title }}
            <span v-if="m.name === 'mypage' && noti.count" class="tile-badge">{{ noti.count }}</span>
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

.grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
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
