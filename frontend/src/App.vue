<script setup>
import { onMounted } from 'vue'
import AppHeader from './components/AppHeader.vue'
import { useAuthStore } from './stores/auth'
import { useWishlistStore } from './stores/wishlist'

const auth = useAuthStore()
const wishlist = useWishlistStore()

// 새로고침 후에도 하트 상태 유지 — 로그인돼 있으면 찜 목록 로드
onMounted(() => {
  if (auth.isLoggedIn) wishlist.load()
})
</script>

<template>
  <AppHeader />
  <main class="container page">
    <router-view />
  </main>
  <footer class="site-footer">
    <div class="container">
      FreshGrowth — 산지 직거래 신선식품 마켓 · 포트폴리오 데모
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
