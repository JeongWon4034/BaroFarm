<script setup>
import AppHeader from './components/AppHeader.vue'
</script>

<template>
  <AppHeader />
  <main class="container page">
    <router-view />
  </main>
  <footer class="site-footer">
    <div class="container">
      FreshGrowth — 소상공인 신선식품 직거래 마켓 · 포트폴리오 데모
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
