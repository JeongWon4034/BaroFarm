<script setup>
import { onMounted } from 'vue'
import AppHeader from './components/AppHeader.vue'
import { useAuthStore } from './stores/auth'
import { useWishlistStore } from './stores/wishlist'
import { useFollowStore } from './stores/follow'
import { useNotificationStore } from './stores/notification'

const auth = useAuthStore()
const wishlist = useWishlistStore()
const follow = useFollowStore()
const noti = useNotificationStore()

// 앱 진입 시 캐시된 토큰을 먼저 검증 — 만료/무효면 세션 정리(헤더가 로그인/회원가입으로).
// 유효할 때만 찜/팔로우 로드(구매자) + 새 주문 알림 갱신(구매자·판매자 공통).
onMounted(async () => {
  if (auth.token && !(await auth.validate())) return
  if (!auth.isLoggedIn) return
  noti.refresh()
  if (auth.isBuyer) {
    wishlist.load()
    follow.load()
  }
})
</script>

<template>
  <AppHeader />
  <main class="container page">
    <router-view />
  </main>
  <footer class="site-footer">
    <div class="container">
      BaroFarm — 산지 직거래 신선식품 마켓
    </div>
  </footer>
</template>

<style scoped>
.page { padding-top: 24px; padding-bottom: 64px; min-height: 60vh; }
.site-footer {
  border-top: 1px solid var(--color-border);
  background: #fff;
  color: var(--color-muted);
  font-size: 13px;
  padding: 24px 0;
  text-align: center;
}
</style>
