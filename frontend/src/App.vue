<script setup>
import { onMounted } from 'vue'
import AppHeader from './components/AppHeader.vue'
import { useAuthStore } from './stores/auth'
import { useWishlistStore } from './stores/wishlist'
import { useFollowStore } from './stores/follow'

const auth = useAuthStore()
const wishlist = useWishlistStore()
const follow = useFollowStore()

// 새로고침 후에도 찜/팔로우 상태 유지 — 구매자면 로드
onMounted(() => {
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
      FreshGrowth — 산지 직거래 신선식품 마켓
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
