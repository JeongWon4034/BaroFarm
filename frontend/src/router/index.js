import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  { path: '/', name: 'products', component: () => import('../views/ProductListView.vue') },
  { path: '/deals', name: 'deals', component: () => import('../views/DealsView.vue') },
  { path: '/products/:id', name: 'product-detail', component: () => import('../views/ProductDetailView.vue') },
  { path: '/cart', name: 'cart', component: () => import('../views/CartView.vue') },
  { path: '/order/complete', name: 'order-complete', component: () => import('../views/OrderCompleteView.vue') },
  { path: '/mypage', name: 'mypage', component: () => import('../views/MyPageView.vue'), meta: { auth: true } },
  { path: '/seller/dashboard', name: 'seller-dashboard', component: () => import('../views/SellerDashboardView.vue'), meta: { auth: true, seller: true } },
  { path: '/login', name: 'login', component: () => import('../views/LoginView.vue') },
  { path: '/signup', name: 'signup', component: () => import('../views/SignupView.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

// 로그인 필요한 페이지 가드
router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.auth && !auth.isLoggedIn) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if (to.meta.seller && !auth.isSeller) {
    return { name: 'products' }
  }
})

export default router
