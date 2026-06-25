<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useCartStore } from '../stores/cart'
import { useWishlistStore } from '../stores/wishlist'
import { useNotificationStore } from '../stores/notification'
import { categoryLabel } from '../utils/format'
import logoUrl from '../assets/logo.png'

const router = useRouter()
const auth = useAuthStore()
const cart = useCartStore()
const wishlist = useWishlistStore()
const noti = useNotificationStore()

const cartCount = computed(() => cart.count)

// 카테고리 코드(백엔드 enum) — 클릭 시 상품목록(products)으로 ?category= 쿼리 전달.
// ProductListView 가 route.query.category 를 복원해 필터링한다.
const CATEGORY_CODES = ['vegetable', 'fruit', 'seafood', 'meat', 'grain', 'etc']

// 카테고리 플라이아웃 토글 (바깥 클릭 시 닫힘)
const catOpen = ref(false)
const catMenuEl = ref(null)
function toggleCat() { catOpen.value = !catOpen.value }
function closeCat() { catOpen.value = false }
function onDocClick(e) {
  if (catMenuEl.value && !catMenuEl.value.contains(e.target)) catOpen.value = false
}
onMounted(() => document.addEventListener('click', onDocClick))
onBeforeUnmount(() => document.removeEventListener('click', onDocClick))

// 헤더 전역 검색 → 상품목록으로 이동
const keyword = ref('')
function submitSearch() {
  const k = keyword.value.trim()
  router.push({ name: 'products', query: k ? { keyword: k } : {} })
}

async function logout() {
  await auth.logout()
  wishlist.clear?.()
  noti.clear?.()
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
          <router-link v-if="auth.isBuyer" :to="{ name: 'following' }">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="9" cy="8" r="3"/><path d="M3 20a6 6 0 0 1 12 0M16 6a3 3 0 0 1 0 6M21 20a6 6 0 0 0-4-5.6"/></svg>팔로잉
          </router-link>
        </div>
        <div class="right">
          <template v-if="auth.isLoggedIn">
            <span class="uname">{{ auth.user?.name }}님</span>
            <button class="link-btn" @click="logout">로그아웃</button>
            <span class="sep"></span>
            <router-link v-if="auth.isAdmin" :to="{ name: 'analytics' }" class="hub">
              관리자 대시보드
            </router-link>
            <router-link v-if="auth.isSeller" :to="{ name: 'seller-center' }" class="hub">
              판매자 센터<span v-if="noti.count" class="cnt">{{ noti.count }}</span>
            </router-link>
            <router-link v-else :to="{ name: 'my-hub' }" class="hub">
              내 메뉴<span v-if="noti.count" class="cnt">{{ noti.count }}</span>
            </router-link>
          </template>
          <template v-else>
            <router-link class="link-btn" :to="{ name: 'login' }">로그인</router-link>
            <router-link class="link-btn" :to="{ name: 'signup' }">회원가입</router-link>
          </template>
        </div>
      </div>
    </div>

    <!-- 브랜드 바: 가운데 로고 + 우측 아이콘 -->
    <div class="container brand-row">
      <div class="br-side br-left"></div>
      <router-link :to="{ name: 'products' }" class="logo">
        <img :src="logoUrl" alt="BaroFarm — 산지 직거래 신선식품 마켓" class="logo-img" />
      </router-link>
      <div class="br-side br-right">
        <form class="searchbox" @submit.prevent="submitSearch">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
          <input v-model="keyword" placeholder="신선한 상품 검색" />
        </form>
        <router-link v-if="auth.isLoggedIn" :to="{ name: 'wishlist' }" class="ibtn" aria-label="찜">
          <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 14c1.5-1.5 3-3.3 3-5.5A4.5 4.5 0 0 0 12 6 4.5 4.5 0 0 0 2 8.5C2 13 12 21 12 21s4-3.2 7-7Z"/></svg>
          <span v-if="wishlist.ids?.length" class="cnt">{{ wishlist.ids.length }}</span>
        </router-link>
        <router-link :to="{ name: 'cart' }" class="ibtn" aria-label="장바구니">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 3h2.2l2 13.4a1.5 1.5 0 0 0 1.5 1.3h9.7a1.5 1.5 0 0 0 1.5-1.2L21 7H5.5"/><circle cx="9" cy="21" r="1.3"/><circle cx="18" cy="21" r="1.3"/></svg>
          <span v-if="cartCount" class="cnt">{{ cartCount }}</span>
        </router-link>
      </div>
    </div>

    <!-- 네비 바: 카테고리 플라이아웃 + 5탭 -->
    <div class="container nav-row">
      <div class="cat-menu" ref="catMenuEl">
        <button class="cat-btn" :class="{ open: catOpen }" @click.stop="toggleCat" :aria-expanded="catOpen">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M4 6h16M4 12h16M4 18h16"/></svg>카테고리
        </button>
        <div class="cat-flyout" :class="{ open: catOpen }">
          <div class="cat-vlist">
            <router-link class="cat" :to="{ name: 'products', query: { category: 'all' } }" @click="closeCat">
              <span class="nm">전체</span>
            </router-link>
            <router-link
              v-for="code in CATEGORY_CODES" :key="code"
              class="cat" :to="{ name: 'products', query: { category: code } }" @click="closeCat"
            >
              <span class="nm">{{ categoryLabel(code) }}</span>
            </router-link>
          </div>
        </div>
      </div>

      <nav class="main">
        <router-link :to="{ name: 'products' }" active-class="active" exact-active-class="active">홈</router-link>
        <span class="navsep"></span>
        <router-link :to="{ name: 'about' }" active-class="active">About BaroFarm</router-link>
        <span class="navsep"></span>
        <router-link :to="{ name: 'best' }" active-class="active">베스트</router-link>
        <span class="navsep"></span>
        <router-link :to="{ name: 'deals' }" class="deal" active-class="active">특가</router-link>
        <span class="navsep"></span>
        <router-link :to="{ name: 'benefits' }" active-class="active">혜택 및 공지</router-link>
      </nav>
    </div>
  </header>
</template>

<style scoped>
.site-header{
  position:sticky; top:0; z-index:40;
  background:rgba(255,255,255,.93); backdrop-filter:saturate(1.4) blur(10px);
  border-bottom:1px solid var(--line);
}

/* 유틸 바 */
.util{ border-bottom:1px solid var(--line); }
.util-row{ display:flex; align-items:center; gap:20px; height:40px; font-size:13px; color:var(--muted); }
.comm{ display:flex; align-items:center; gap:18px; }
.comm a{ display:inline-flex; align-items:center; gap:5px; transition:color .15s; }
.comm a:hover{ color:var(--leaf-700); }
.right{ margin-left:auto; display:flex; align-items:center; gap:16px; }
.right a:hover{ color:var(--ink); }
.sep{ width:1px; height:13px; background:var(--line-2); }
.uname{ color:var(--ink-2); font-weight:600; }
.link-btn{ background:transparent; border:none; color:var(--muted); font-size:13px; font-weight:500; padding:0; }
.link-btn:hover{ color:var(--ink); text-decoration:underline; }
.hub{ display:inline-flex; align-items:center; gap:6px; background:var(--leaf-600); color:#fff; font-weight:700; font-size:12.5px; padding:6px 13px; border-radius:999px; transition:background .15s; }
.hub:hover{ background:var(--leaf-700); color:#fff; }
.cnt{ background:var(--deal); color:#fff; font-size:10.5px; font-weight:700; min-width:16px; height:16px; border-radius:9px; display:inline-flex; align-items:center; justify-content:center; padding:0 4px; }

/* 브랜드 바 */
.brand-row{ display:grid; grid-template-columns:1fr auto 1fr; align-items:center; height:78px; }
.br-side{ display:flex; align-items:center; }
.br-right{ justify-self:end; gap:10px; }
.logo{ display:flex; align-items:center; justify-self:center; }
.logo-img{ height:56px; width:auto; display:block; }
.searchbox{ display:flex; align-items:center; gap:9px; background:#fff; border:1.5px solid var(--line-2); border-radius:12px; padding:0 14px; height:42px; width:230px; transition:.18s; }
.searchbox:focus-within{ border-color:var(--leaf-400); box-shadow:0 0 0 4px var(--leaf-50); }
.searchbox svg{ color:var(--faint); }
.searchbox input{ border:none; outline:none; font-family:inherit; font-size:14px; width:100%; background:transparent; color:var(--ink); }
.searchbox input::placeholder{ color:var(--faint); }
.ibtn{ position:relative; width:42px; height:42px; border-radius:11px; display:flex; align-items:center; justify-content:center; color:var(--ink-2); transition:.15s; }
.ibtn:hover{ background:var(--leaf-50); color:var(--leaf-700); }
.ibtn .cnt{ position:absolute; top:4px; right:4px; }

/* 네비 바 */
.nav-row{ display:flex; align-items:center; gap:20px; height:58px; justify-content:center; position:relative; }
nav.main{ display:flex; align-items:center; gap:20px; }
nav.main a{ padding:8px 14px; border-radius:9px; font-size:15.5px; font-weight:600; color:var(--ink-2); transition:.15s; position:relative; white-space:nowrap; }
nav.main a:hover{ background:var(--leaf-50); color:var(--leaf-700); }
nav.main a.active{ color:var(--leaf-700); }
nav.main a.active::after{ content:""; position:absolute; left:14px; right:14px; bottom:-3px; height:2.5px; border-radius:2px; background:var(--leaf-600); }
nav.main a.deal{ color:var(--deal); }
nav.main a.deal:hover{ background:var(--deal-soft); color:var(--deal); }
nav.main a.deal.active{ color:var(--deal); }
nav.main a.deal.active::after{ background:var(--deal); }
.navsep{ width:1px; height:15px; background:var(--line-2); flex:none; }

/* 카테고리 플라이아웃 */
.cat-menu{ position:absolute; left:0; top:50%; transform:translateY(-50%); }
.cat-btn{ display:inline-flex; align-items:center; gap:8px; height:44px; padding:0 16px; border-radius:11px; border:1.5px solid var(--line-2); background:#fff; font-size:15px; font-weight:700; color:var(--ink); transition:.15s; }
.cat-btn svg{ width:18px; height:18px; }
.cat-btn:hover{ border-color:var(--leaf-400); background:var(--leaf-50); color:var(--leaf-700); }
.cat-btn.open{ background:var(--leaf-600); border-color:var(--leaf-600); color:#fff; }
.cat-flyout{ position:absolute; top:calc(100% + 10px); left:0; width:240px; background:#fff; border:1px solid var(--line); border-radius:16px; box-shadow:var(--shadow-lg); padding:8px; opacity:0; visibility:hidden; transform:translateY(-6px); transition:.16s; z-index:50; }
.cat-flyout.open{ opacity:1; visibility:visible; transform:translateY(0); }
.cat-vlist{ display:flex; flex-direction:column; gap:2px; }
.cat-vlist .cat{ display:flex; align-items:center; gap:11px; padding:10px 12px; border-radius:10px; font-size:15px; font-weight:600; color:var(--ink-2); transition:.13s; }
.cat-vlist .cat:hover{ background:var(--leaf-50); color:var(--leaf-700); }
.cat-vlist .cat.active{ background:var(--leaf-100); color:var(--leaf-700); }

@media (max-width:780px){
  .searchbox{ display:none; }
  nav.main{ gap:8px; }
  nav.main a{ padding:8px 9px; font-size:14px; }
}
</style>
