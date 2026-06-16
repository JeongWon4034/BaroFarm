<script setup>
import { ref, computed } from 'vue'
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

// 헤더 전역 검색 → 상품목록으로 이동(ProductListView가 route.query.keyword 복원)
const keyword = ref('')
function submitSearch() {
  const k = keyword.value.trim()
  router.push({ name: 'products', query: k ? { keyword: k } : {} })
}

async function logout() {
  await auth.logout()
  wishlist.clear()
  follow.clear()
  router.push({ name: 'products' })
}
</script>

<template>
  <header class="site-header">
    <!-- 유틸 바: 커뮤니티 + 계정 -->
    <div class="util">
      <div class="container util-row">
        <div class="comm">
          <router-link :to="{ name: 'challenges' }">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9V2h12v7a6 6 0 0 1-12 0Z"/><path d="M6 5H4a2 2 0 0 0 0 4h2M18 5h2a2 2 0 0 1 0 4h-2M9 18h6M12 14v4"/></svg>챌린지
          </router-link>
          <router-link :to="{ name: 'board' }">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8 8h8M8 12h8M8 16h5"/></svg>게시판
          </router-link>
        </div>
        <div class="right">
          <template v-if="auth.isLoggedIn">
            <span class="uname">{{ auth.user.name }}님</span>
            <button class="link-btn" @click="logout">로그아웃</button>
          </template>
          <template v-else>
            <router-link class="link-btn" :to="{ name: 'login' }">로그인</router-link>
            <router-link class="link-btn" :to="{ name: 'signup' }">회원가입</router-link>
          </template>
          <span class="sep"></span>
          <router-link :to="{ name: 'cart' }" class="icn">
            <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 3h2.2l2 13.4a1.5 1.5 0 0 0 1.5 1.3h9.7a1.5 1.5 0 0 0 1.5-1.2L21 7H5.5"/><circle cx="9" cy="21" r="1.3"/><circle cx="18" cy="21" r="1.3"/></svg>장바구니
            <span v-if="cartCount" class="cnt">{{ cartCount }}</span>
          </router-link>
          <!-- 개인 메뉴 허브 진입 — 찜·마이페이지·구매분석·팔로잉을 모두 여기로 모음 -->
          <router-link v-if="auth.isSeller" :to="{ name: 'seller-center' }" class="me">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9 4 4h16l1 5"/><path d="M4 9v10a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1V9"/><path d="M3 9h18"/><path d="M9 20v-6h6v6"/></svg>판매자 센터
          </router-link>
          <router-link v-else-if="auth.isBuyer" :to="{ name: 'my-hub' }" class="me">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="4"/><path d="M5 21a7 7 0 0 1 14 0"/></svg>내 메뉴
          </router-link>
        </div>
      </div>
    </div>

    <!-- 메인 바: 로고 + 네비 + 검색 -->
    <div class="container nav-row">
      <router-link :to="{ name: 'products' }" class="logo">
        <span class="mark">
          <svg width="21" height="21" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round"><path d="M12 21c0-6 0-9 0-12"/><path d="M12 11C12 6 16 3 21 3c0 5-4 8-9 8Z"/><path d="M12 14C12 10.5 8.5 8 4 8c0 4.5 3.5 6.5 8 6Z"/></svg>
        </span>
        <span class="wm">FreshGrowth<small>산지 직거래 마켓</small></span>
      </router-link>

      <nav class="main">
        <!-- 공개 메뉴만 (개인/역할 메뉴는 상단 '내 메뉴/판매자 센터' 허브로 분리) -->
        <router-link :to="{ name: 'products' }" active-class="active" exact-active-class="active">상품 목록</router-link>
        <router-link :to="{ name: 'deals' }" class="deal" active-class="active">마감임박 특가</router-link>
      </nav>

      <form class="searchbox" @submit.prevent="submitSearch">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
        <input v-model="keyword" placeholder="상품명으로 검색 (예: 상추)" />
      </form>
    </div>
  </header>
</template>

<style scoped>
.site-header{
  position:sticky; top:0; z-index:40;
  background:rgba(255,255,255,.92); backdrop-filter:saturate(1.4) blur(10px);
  border-bottom:1px solid var(--line);
}

/* 유틸 바 */
.util{ border-bottom:1px solid var(--line); }
.util-row{ display:flex; align-items:center; gap:20px; height:40px; font-size:13px; color:var(--muted); }
.comm{ display:flex; align-items:center; gap:18px; }
.comm a{ display:inline-flex; align-items:center; gap:6px; transition:color .15s; }
.comm a:hover{ color:var(--leaf-700); }
.right{ margin-left:auto; display:flex; align-items:center; gap:16px; }
.right a:hover{ color:var(--ink); }
.sep{ width:1px; height:13px; background:var(--line-2); }
.uname{ color:var(--ink-2); font-weight:600; }
.link-btn{ background:transparent; border:none; color:var(--muted); font-size:13px; font-weight:500; padding:0; }
.link-btn:hover{ color:var(--ink); text-decoration:underline; }
.icn{ display:inline-flex; align-items:center; gap:6px; color:var(--ink-2); position:relative; }
.icn:hover{ color:var(--leaf-700); }
.cnt{
  background:var(--deal); color:#fff; font-size:10.5px; font-weight:700;
  min-width:16px; height:16px; border-radius:9px;
  display:inline-flex; align-items:center; justify-content:center; padding:0 4px;
}

/* 메인 바 */
.nav-row{ display:flex; align-items:center; gap:28px; height:74px; }
.logo{ display:flex; align-items:center; gap:11px; }
.logo .mark{
  width:38px; height:38px; border-radius:12px 12px 12px 4px;
  background:linear-gradient(150deg, var(--leaf-500), var(--leaf-600));
  display:flex; align-items:center; justify-content:center; color:#fff; box-shadow:var(--shadow-sm);
}
.logo .wm{ font-size:22px; font-weight:800; letter-spacing:-.02em; line-height:1; }
.logo .wm small{ display:block; font-size:11px; font-weight:500; color:var(--muted); letter-spacing:0; margin-top:3px; }

.main{ display:flex; align-items:center; gap:4px; }
.main a{
  padding:8px 13px; border-radius:9px; font-size:15px; font-weight:600;
  color:var(--ink-2); transition:.15s; position:relative; white-space:nowrap;
}
.main a:hover{ background:var(--leaf-50); color:var(--leaf-700); }
.main a.active{ color:var(--leaf-700); }
.main a.active::after{
  content:""; position:absolute; left:13px; right:13px; bottom:-3px;
  height:2.5px; border-radius:2px; background:var(--leaf-600);
}
.main a.deal{ color:var(--deal); display:inline-flex; align-items:center; gap:6px; }
.main a.deal::before{ content:""; width:6px; height:6px; border-radius:50%; background:var(--deal); }
.main a.deal:hover{ background:var(--deal-soft); color:var(--deal); }

/* 상단 우측 개인 메뉴 허브 진입 — 눈에 띄게 pill로 강조 */
.me{
  display:inline-flex; align-items:center; gap:6px;
  background:var(--leaf-600); color:#fff; font-weight:700; font-size:12.5px;
  padding:6px 13px; border-radius:999px; transition:background .15s;
}
.me:hover{ background:var(--leaf-700); color:#fff; }
.me.router-link-active{ background:var(--leaf-700); }

.searchbox{
  margin-left:auto; display:flex; align-items:center; gap:9px;
  background:#fff; border:1.5px solid var(--line-2); border-radius:12px;
  padding:0 14px; height:44px; width:280px; transition:.18s;
}
.searchbox:focus-within{ border-color:var(--leaf-400); box-shadow:0 0 0 4px var(--leaf-50); }
.searchbox svg{ color:var(--faint); }
.searchbox input{ border:none; outline:none; font-family:inherit; font-size:14.5px; width:100%; background:transparent; color:var(--ink); }
.searchbox input::placeholder{ color:var(--faint); }

@media (max-width:780px){
  .searchbox{ display:none; }
  .main{ gap:0; }
  .main a{ padding:8px 9px; font-size:14px; }
}
</style>
