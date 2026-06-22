<script setup>
import { ref, computed, onMounted } from 'vue'
import { orderApi } from '../api/orders'
import { useNotificationStore } from '../stores/notification'
import { won, dateOnly, thumbEmoji, orderStatusMeta, apiMessage } from '../utils/format'

const noti = useNotificationStore()
const orders = ref([])
const loading = ref(true)
const error = ref('')
const advancing = ref(null)   // 상태 전이 진행 중인 orderId (버튼 중복클릭 방지)

// 상태 필터 탭 — '' 는 전체
const FILTERS = [
  { key: '', label: '전체' },
  { key: 'PENDING', label: '확인 대기' },
  { key: 'CONFIRMED', label: '주문 확인' },
  { key: 'SHIPPING', label: '배송중' },
  { key: 'COMPLETED', label: '배송완료' },
]
const filter = ref('')

onMounted(load)
async function load() {
  loading.value = true
  error.value = ''
  try {
    orders.value = (await orderApi.sellerOrders()) || []
    noti.markSeen(orders.value) // 주문 관리 확인 → 새 주문 알림 배지 제거
  } catch (e) {
    error.value = apiMessage(e)
  } finally {
    loading.value = false
  }
}

const counts = computed(() => {
  const c = { PENDING: 0, CONFIRMED: 0, SHIPPING: 0, COMPLETED: 0 }
  orders.value.forEach((o) => { c[o.status] = (c[o.status] || 0) + 1 })
  return c
})

const visible = computed(() =>
  filter.value ? orders.value.filter((o) => o.status === filter.value) : orders.value
)

// 처리 대기(아직 배송완료 전) 건수 — 판매자가 가장 먼저 봐야 할 숫자
const pendingWork = computed(() =>
  counts.value.PENDING + counts.value.CONFIRMED + counts.value.SHIPPING
)

async function advance(o) {
  const meta = orderStatusMeta(o.status)
  if (!meta.next || advancing.value) return
  advancing.value = o.orderId
  error.value = ''
  try {
    const updated = await orderApi.updateStatus(o.orderId, meta.next)
    // 서버가 돌려준 최신 주문으로 교체(낙관적 갱신 대신 권위 있는 응답 반영)
    const i = orders.value.findIndex((x) => x.orderId === o.orderId)
    if (i !== -1) orders.value[i] = updated
  } catch (e) {
    error.value = apiMessage(e, '상태를 변경하지 못했어요.')
  } finally {
    advancing.value = null
  }
}
</script>

<template>
  <div>
    <div class="page-head">
      <h1>🧾 판매 주문 관리</h1>
      <p class="muted">
        주문을 <b>확인 → 배송 시작 → 배송 완료</b> 순서로 처리하세요.
        <span v-if="pendingWork" class="hl">처리할 주문 {{ pendingWork }}건</span>
      </p>
    </div>

    <div v-if="loading" class="empty"><span class="emoji">⏳</span>불러오는 중…</div>
    <div v-else-if="error && !orders.length" class="empty">
      <span class="emoji">⚠️</span>{{ error }}<br />
      <button class="btn btn-outline" style="margin-top:12px" @click="load">다시 시도</button>
    </div>

    <template v-else>
      <!-- 상태 필터 탭 -->
      <div class="tabs">
        <button
          v-for="f in FILTERS" :key="f.key"
          class="tab" :class="{ on: filter === f.key }"
          @click="filter = f.key"
        >
          {{ f.label }}
          <span v-if="f.key" class="cnt">{{ counts[f.key] || 0 }}</span>
          <span v-else class="cnt">{{ orders.length }}</span>
        </button>
      </div>

      <p v-if="error" class="err-inline">{{ error }}</p>

      <div v-if="!visible.length" class="empty-inline muted">해당 상태의 주문이 없습니다.</div>

      <ul v-else class="orders">
        <li v-for="o in visible" :key="o.orderId" class="order-card card">
          <div class="ot">
            <span class="date">{{ dateOnly(o.orderDate) }} · 주문 #{{ o.orderId }}</span>
            <span class="status" :class="orderStatusMeta(o.status).cls">{{ orderStatusMeta(o.status).label }}</span>
          </div>

          <div class="prod">
            <div class="tile">{{ thumbEmoji({ name: o.productName }) }}</div>
            <div class="info">
              <div class="nm">{{ o.productName }}</div>
              <div class="q muted">수량 {{ o.quantity }}개 · 구매자 #{{ o.buyerId }}</div>
            </div>
            <div class="price">{{ won(o.totalPrice) }}</div>
          </div>

          <!-- 단계 진행 표시 -->
          <div class="flow">
            <span class="step" :class="{ done: ['CONFIRMED','SHIPPING','COMPLETED'].includes(o.status), cur: o.status==='PENDING' }">확인 대기</span>
            <span class="arr">›</span>
            <span class="step" :class="{ done: ['SHIPPING','COMPLETED'].includes(o.status), cur: o.status==='CONFIRMED' }">주문 확인</span>
            <span class="arr">›</span>
            <span class="step" :class="{ done: o.status==='COMPLETED', cur: o.status==='SHIPPING' }">배송중</span>
            <span class="arr">›</span>
            <span class="step" :class="{ done: o.status==='COMPLETED', cur: o.status==='COMPLETED' }">배송완료</span>
          </div>

          <div class="actions">
            <button
              v-if="orderStatusMeta(o.status).next"
              class="btn btn-primary"
              :disabled="advancing === o.orderId"
              @click="advance(o)"
            >
              {{ advancing === o.orderId ? '처리 중…' : orderStatusMeta(o.status).nextLabel + ' →' }}
            </button>
            <span v-else class="done-tag">✅ 처리 완료</span>
          </div>
        </li>
      </ul>
    </template>
  </div>
</template>

<style scoped>
.page-head { margin-bottom: 18px; }
.page-head h1 { font-size: 22px; margin: 0 0 4px; }
.page-head .hl { margin-left: 8px; font-weight: 800; color: var(--color-primary-dark); }

.tabs { display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap; }
.tab { border: 1px solid var(--color-border); background: #fff; border-radius: 999px; padding: 7px 14px; font-size: 13.5px; font-weight: 600; cursor: pointer; display: inline-flex; align-items: center; gap: 6px; }
.tab.on { background: var(--color-primary); color: #fff; border-color: var(--color-primary); }
.tab .cnt { font-size: 12px; font-weight: 800; opacity: .8; }

.err-inline { color: #c1272d; font-size: 13px; margin: 0 0 12px; }

.orders { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 12px; }
.order-card { padding: 16px 18px; }

.ot { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.ot .date { font-size: 13px; color: var(--color-muted); }
.status { font-size: 12.5px; font-weight: 800; padding: 4px 11px; border-radius: 999px; }
.status.st-pending { background: #fef3e2; color: #b76e00; }
.status.st-confirmed { background: #e7f0ff; color: #1a56b8; }
.status.st-shipping { background: #eae6ff; color: #5b3cc4; }
.status.st-completed { background: var(--color-primary-soft); color: var(--color-primary-dark); }

.prod { display: flex; align-items: center; gap: 12px; }
.tile { width: 46px; height: 46px; border-radius: 12px; background: var(--color-primary-soft); display: flex; align-items: center; justify-content: center; font-size: 24px; flex-shrink: 0; }
.info { flex: 1; min-width: 0; }
.info .nm { font-weight: 700; }
.info .q { font-size: 12.5px; }
.price { font-weight: 800; }

.flow { display: flex; align-items: center; gap: 6px; margin: 14px 0 4px; flex-wrap: wrap; }
.flow .step { font-size: 12px; color: #9aa0a6; font-weight: 600; }
.flow .step.done { color: var(--color-primary-dark); }
.flow .step.cur { color: #111; font-weight: 800; text-decoration: underline; text-underline-offset: 3px; }
.flow .arr { color: #cfd4d8; font-size: 13px; }

.actions { margin-top: 12px; display: flex; justify-content: flex-end; }
.done-tag { font-size: 13px; font-weight: 700; color: var(--color-primary-dark); }

.empty-inline { padding: 32px; text-align: center; }
</style>
