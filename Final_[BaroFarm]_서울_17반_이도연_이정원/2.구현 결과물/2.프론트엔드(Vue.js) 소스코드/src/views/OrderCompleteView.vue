<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { orderApi } from '../api/orders'
import { track } from '../api/track'
import { won } from '../utils/format'
import { useNotificationStore } from '../stores/notification'

const route = useRoute()
const noti = useNotificationStore()
const orders = ref([])
const loading = ref(true)

const total = computed(() => orders.value.reduce((s, o) => s + (o.totalPrice || 0), 0))

onMounted(async () => {
  const ids = String(route.query.ids || '').split(',').filter(Boolean)
  const results = await Promise.all(ids.map((id) => orderApi.detail(id).catch(() => null)))
  orders.value = results.filter(Boolean)
  // 퍼널 5단계(전환 완료) — 주문 건마다 1회
  orders.value.forEach((o) => track('complete_order', { productId: o.productId }))
  noti.refresh() // 새 주문 반영 → 헤더 '내 메뉴' 알림 배지 갱신
  loading.value = false
})
</script>

<template>
  <div class="complete">
    <div class="cmp-card">
      <div class="cmp-check">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12 5 5L20 6" /></svg>
      </div>
      <h1>주문이 완료되었습니다!</h1>
      <p class="sub">신선한 상품을 산지에서 바로 보내드릴게요 🚚</p>
      <span v-if="orders.length" class="cmp-order-no">주문번호 #{{ orders.map((o) => o.orderId).join(', #') }}</span>

      <!-- 배송 트래커 -->
      <div class="track">
        <div class="step done"><span class="dot">✓</span><span class="lb">결제완료</span></div>
        <div class="step active"><span class="dot">📦</span><span class="lb">상품준비</span></div>
        <div class="step"><span class="dot">🚚</span><span class="lb">배송중</span></div>
        <div class="step"><span class="dot">🏠</span><span class="lb">배송완료</span></div>
      </div>

      <div v-if="loading" class="loadingtxt">불러오는 중…</div>
      <div v-else class="cmp-info">
        <div class="r" v-for="o in orders" :key="o.orderId">
          <span>{{ o.productName }} <em>× {{ o.quantity }}</em></span>
          <b>{{ won(o.totalPrice) }}</b>
        </div>
        <div class="r total"><span>총 결제 금액</span><b>{{ won(total) }}</b></div>
      </div>

      <div class="cmp-cta">
        <router-link class="btn btn-outline" :to="{ name: 'products' }">계속 쇼핑하기</router-link>
        <router-link class="btn btn-primary" :to="{ name: 'mypage' }">주문 내역 보기</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.complete { padding: 40px 0 70px; }
.cmp-card { max-width: 560px; margin: 0 auto; background: #fff; border: 1px solid var(--line); border-radius: 24px; padding: 44px; text-align: center; box-shadow: var(--shadow-md); }
.cmp-check { width: 84px; height: 84px; border-radius: 50%; background: var(--leaf-100); display: flex; align-items: center; justify-content: center; margin: 0 auto 22px; border: 3px solid var(--leaf-300); animation: pop .4s cubic-bezier(.2,.9,.3,1.4); }
.cmp-check svg { width: 42px; height: 42px; color: var(--leaf-600); }
@keyframes pop { 0% { transform: scale(.5); opacity: 0; } 100% { transform: scale(1); opacity: 1; } }
@media (prefers-reduced-motion: reduce) { .cmp-check { animation: none; } }

.cmp-card h1 { font-size: 27px; font-weight: 800; letter-spacing: -.02em; margin: 0 0 10px; }
.cmp-card .sub { color: var(--muted); font-size: 15px; margin: 0 0 16px; }
.cmp-order-no { display: inline-block; background: var(--cream); border: 1px solid var(--line); border-radius: 9px; padding: 6px 14px; font-size: 13px; color: var(--ink-2); font-weight: 600; margin-bottom: 28px; }

.track { display: flex; align-items: flex-start; justify-content: space-between; margin: 6px 0 30px; position: relative; }
.track::before { content: ""; position: absolute; top: 15px; left: 12%; right: 12%; height: 2px; background: var(--line); }
.track .step { display: flex; flex-direction: column; align-items: center; gap: 8px; flex: 1; position: relative; z-index: 1; }
.track .step .dot { width: 32px; height: 32px; border-radius: 50%; background: #fff; border: 2px solid var(--line); display: flex; align-items: center; justify-content: center; font-size: 14px; }
.track .step.done .dot { background: var(--leaf-600); border-color: var(--leaf-600); color: #fff; }
.track .step.active .dot { border-color: var(--leaf-600); box-shadow: 0 0 0 4px var(--leaf-50); }
.track .step .lb { font-size: 12.5px; color: var(--muted); font-weight: 600; }
.track .step.done .lb, .track .step.active .lb { color: var(--ink); }

.loadingtxt { color: var(--muted); margin: 24px 0; }
.cmp-info { text-align: left; border: 1px solid var(--line); border-radius: 14px; overflow: hidden; margin-bottom: 26px; }
.cmp-info .r { display: flex; justify-content: space-between; align-items: center; padding: 13px 16px; font-size: 14px; border-bottom: 1px solid var(--line); }
.cmp-info .r:last-child { border-bottom: none; }
.cmp-info .r em { color: var(--muted); font-style: normal; }
.cmp-info .r b { font-weight: 700; }
.cmp-info .r.total { background: var(--cream); font-weight: 700; }
.cmp-info .r.total b { font-size: 18px; color: var(--leaf-700); }

.cmp-cta { display: flex; gap: 12px; }
.cmp-cta .btn { flex: 1; padding: 14px; }
</style>
