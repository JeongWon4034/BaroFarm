<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useCartStore } from '../stores/cart'
import { useWishlistStore } from '../stores/wishlist'
import { useFollowStore } from '../stores/follow'

const router = useRouter()
const auth = useAuthStore()
const cart = useCartStore()
const wishlist = useWishlistStore()
const follow = useFollowStore()
const cartCount = computed(() => cart.count)

function logout() {
  auth.logout()
  wishlist.clear()
  follow.clear()
  router.push({ name: 'products' })
}
</script>

<template>
  <header class="site-header">
    <div class="top-bar">
      <div class="container top-inner">
        <router-link :to="{ name: 'products' }" class="brand">
          <span class="logo">🥬 FreshGrowth</span>
          <span class="tagline">산지 직거래 마켓 · 마감임박 특가</span>
        </router-link>

        <div class="top-right">
          <template v-if="auth.isLoggedIn">
            <span class="welcome">{{ auth.user.name }}님</span>
            <button class="link-btn" @click="logout">로그아웃</button>
          </template>
          <template v-else>
            <router-link class="link-btn" :to="{ name: 'login' }">로그인</router-link>
            <router-link class="link-btn" :to="{ name: 'signup' }">회원가입</router-link>
          </template>
          <router-link :to="{ name: 'cart' }" class="cart-chip">
            🛒 장바구니
            <span class="cart-count">{{ cartCount }}</span>
          </router-link>
        </div>
      </div>
    </div>

    <nav class="nav-bar">
      <div class="container nav-inner">
        <router-link :to="{ name: 'products' }" class="nav-item" active-class="active" exact-active-class="active">🏠 홈 / 상품 목록</router-link>
        <router-link :to="{ name: 'deals' }" class="nav-item" active-class="active">⏰ 마감임박 특가</router-link>
        <router-link :to="{ name: 'cart' }" class="nav-item" active-class="active">🧺 장바구니 & 결제</router-link>
        <router-link v-if="auth.isBuyer" :to="{ name: 'wishlist' }" class="nav-item" active-class="active">❤️ 찜</router-link>
        <router-link v-if="auth.isBuyer" :to="{ name: 'following' }" class="nav-item" active-class="active">👥 팔로잉</router-link>
        <router-link :to="{ name: 'mypage' }" class="nav-item" active-class="active">👤 마이페이지</router-link>
        <router-link v-if="auth.isSeller" :to="{ name: 'seller-products' }" class="nav-item" active-class="active">📦 상품 관리</router-link>
        <router-link v-if="auth.isSeller" :to="{ name: 'seller-dashboard' }" class="nav-item" active-class="active">📊 판매자 대시보드</router-link>
      </div>
    </nav>
  </header>
</template>

<style scoped>
.site-header { background: #fff; border-bottom: 1px solid var(--color-border); }
.top-bar {
  background: linear-gradient(120deg, var(--color-primary-dark), var(--color-primary));
  color: #fff;
}
.top-inner { display: flex; align-items: center; justify-content: space-between; height: 72px; }
.brand { display: flex; flex-direction: column; }
.logo { font-size: 22px; font-weight: 800; }
.tagline { font-size: 12px; opacity: 0.85; margin-top: 2px; }

.top-right { display: flex; align-items: center; gap: 16px; }
.welcome { font-size: 14px; opacity: 0.95; }
.link-btn {
  background: transparent; border: none; color: #fff; font-size: 14px; opacity: 0.9;
  padding: 0; font-weight: 500;
}
.link-btn:hover { opacity: 1; text-decoration: underline; }

.cart-chip {
  display: inline-flex; align-items: center; gap: 8px;
  background: rgba(255, 255, 255, 0.16);
  padding: 8px 14px; border-radius: 999px; font-size: 14px; font-weight: 600;
}
.cart-chip:hover { background: rgba(255, 255, 255, 0.26); }
.cart-count {
  background: var(--color-accent); color: #fff; border-radius: 999px;
  min-width: 20px; height: 20px; padding: 0 6px;
  display: inline-flex; align-items: center; justify-content: center; font-size: 12px;
}

.nav-bar { background: #fff; }
.nav-inner { display: flex; gap: 8px; }
.nav-item {
  padding: 14px 14px; font-size: 15px; font-weight: 600; color: var(--color-muted);
  border-bottom: 3px solid transparent;
}
.nav-item:hover { color: var(--color-text); }
.nav-item.active { color: var(--color-primary-dark); border-bottom-color: var(--color-primary); }
</style>
