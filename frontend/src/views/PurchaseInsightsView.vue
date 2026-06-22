<script setup>
import { ref, computed, onMounted } from 'vue'
import { orderApi } from '../api/orders'
import { won, categoryLabel, thumbEmoji, dateOnly } from '../utils/format'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const orders = ref([])
const loading = ref(true)
const error = ref('')
const aiInsight = ref(null)

onMounted(load)
async function load() {
  loading.value = true
  error.value = ''
  try {
    orders.value = (await orderApi.myOrders()) || []
    // 진짜 LLM 요약(실패/미설정 시 규칙기반 fallback 으로 대체)
    aiInsight.value = await orderApi.insight().catch(() => null)
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

const totalSpend = computed(() => orders.value.reduce((s, o) => s + (o.totalPrice || 0), 0))
const totalQty = computed(() => orders.value.reduce((s, o) => s + (o.quantity || 0), 0))
const avgOrder = computed(() => (orders.value.length ? Math.round(totalSpend.value / orders.value.length) : 0))
const reviewRate = computed(() => {
  if (!orders.value.length) return 0
  const done = orders.value.filter((o) => o.reviewId).length
  return Math.round((done / orders.value.length) * 100)
})

// 월별 지출(YYYY-MM) — 최근 6개월
const byMonth = computed(() => {
  const m = {}
  orders.value.forEach((o) => {
    const ym = (o.orderDate || '').slice(0, 7)
    if (ym) m[ym] = (m[ym] || 0) + (o.totalPrice || 0)
  })
  return Object.entries(m).sort((a, b) => a[0].localeCompare(b[0])).slice(-6)
})
const monthMax = computed(() => Math.max(1, ...byMonth.value.map(([, v]) => v)))

// 이번 달 vs 지난 달
const monthDelta = computed(() => {
  const now = new Date()
  const key = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
  const thisKey = key(now)
  const lastKey = key(new Date(now.getFullYear(), now.getMonth() - 1, 1))
  const map = Object.fromEntries(byMonth.value)
  const t = map[thisKey] || 0
  const l = map[lastKey] || 0
  return { thisMonth: t, lastMonth: l, diff: t - l }
})

// 카테고리별 지출
const byCategory = computed(() => {
  const m = {}
  orders.value.forEach((o) => {
    const k = o.category || '기타'
    m[k] = (m[k] || 0) + (o.totalPrice || 0)
  })
  return Object.entries(m).sort((a, b) => b[1] - a[1])
})

// 자주 산 상품 Top 5 (수량 기준)
const topProducts = computed(() => {
  const m = {}
  orders.value.forEach((o) => {
    const k = o.productName || '-'
    m[k] = (m[k] || 0) + (o.quantity || 0)
  })
  return Object.entries(m).sort((a, b) => b[1] - a[1]).slice(0, 5)
})

// 마감임박 떨이로 아낀 금액 — 주문 시점 정가(originalUnitPrice) 대비 실결제액 차이
const savedDetail = computed(() => {
  let saved = 0
  let rescued = 0
  orders.value.forEach((o) => {
    if (o.originalUnitPrice == null) return
    const diff = o.originalUnitPrice * (o.quantity || 0) - (o.totalPrice || 0)
    if (diff > 0) { saved += diff; rescued++ }
  })
  return { saved, rescued }
})

const recentOrders = computed(() => orders.value.slice(0, 8))

function monthLabel(ym) {
  const [, mm] = ym.split('-')
  return `${Number(mm)}월`
}
</script>

<template>
  <div>
    <div class="page-head">
      <h1>📊 내 구매 분석</h1>
      <p class="muted">{{ auth.user?.name }}님의 거래 현황과 소비 패턴을 한눈에</p>
    </div>

    <div v-if="loading" class="empty"><span class="emoji">⏳</span>불러오는 중…</div>
    <div v-else-if="error" class="empty">
      <span class="emoji">⚠️</span>{{ error }}<br />
      <button class="btn btn-outline" style="margin-top:12px" @click="load">다시 시도</button>
    </div>
    <div v-else-if="orders.length === 0" class="empty">
      <span class="emoji">🧾</span>아직 구매 내역이 없어요.
      <br /><router-link class="btn btn-primary" style="margin-top:14px" :to="{ name: 'products' }">상품 보러 가기</router-link>
    </div>

    <template v-else>
      <!-- AI 인사이트 -->
      <div class="report card">
        <div class="report-tag">
          🤖 AI 구매 인사이트
          <span v-if="aiInsight" class="report-badge">GMS</span>
          <span v-if="aiInsight?.spendingType" class="type-badge">{{ aiInsight.spendingType }}</span>
        </div>
        <p class="report-body">
          {{ aiInsight?.summary || `총 ${orders.length}건 · ${won(totalSpend)}을 지출했고, 평균 주문액은 ${won(avgOrder)}입니다.` }}
        </p>
        <p v-if="aiInsight?.usedData?.length" class="report-ctx muted">🔎 AI가 참고한 데이터: {{ aiInsight.usedData.join(' · ') }}</p>
        <p v-else class="report-note muted">※ AI 연결 전이라 규칙 기반 요약입니다.</p>
      </div>

      <!-- AI 다음 장보기 추천 -->
      <div v-if="aiInsight?.recommendations?.length" class="rec-card card">
        <div class="rec-title">🛒 AI 맞춤 추천 — 다음 장보기</div>
        <p class="rec-desc muted">구매 패턴을 분석해 AI가 직접 고른 신선식품이에요.</p>
        <ul class="rec-list">
          <li v-for="(rec, i) in aiInsight.recommendations" :key="i" class="rec-item">
            <span class="rec-num">{{ i + 1 }}</span>
            <span class="rec-text">{{ rec }}</span>
          </li>
        </ul>
      </div>

      <!-- KPI -->
      <div class="kpi-grid">
        <div class="kpi card">
          <span class="kpi-label">총 구매</span>
          <span class="kpi-value">{{ orders.length }}건</span>
          <span class="kpi-sub">{{ totalQty }}개 상품</span>
        </div>
        <div class="kpi card good">
          <span class="kpi-label">총 지출</span>
          <span class="kpi-value">{{ won(totalSpend) }}</span>
        </div>
        <div class="kpi card">
          <span class="kpi-label">평균 주문액</span>
          <span class="kpi-value">{{ won(avgOrder) }}</span>
        </div>
        <div class="kpi card">
          <span class="kpi-label">이번 달 지출</span>
          <span class="kpi-value">{{ won(monthDelta.thisMonth) }}</span>
          <span class="kpi-sub" :class="monthDelta.diff > 0 ? 'up' : 'down'">
            지난 달 대비 {{ monthDelta.diff >= 0 ? '+' : '−' }}{{ won(Math.abs(monthDelta.diff)).replace('₩', '') }}원
          </span>
        </div>
      </div>

      <!-- 월별 지출 추이 -->
      <div class="card section" v-if="byMonth.length">
        <h2 class="section-title">월별 지출 추이</h2>
        <div class="month-chart">
          <div v-for="[ym, v] in byMonth" :key="ym" class="month-col">
            <span class="month-val">{{ won(v).replace('₩', '') }}</span>
            <div class="month-bar"><div class="month-fill" :style="{ height: (v / monthMax * 100) + '%' }" /></div>
            <span class="month-label">{{ monthLabel(ym) }}</span>
          </div>
        </div>
      </div>

      <!-- 카테고리별 지출 -->
      <div class="card section" v-if="byCategory.length">
        <h2 class="section-title">카테고리별 지출</h2>
        <div class="cat-list">
          <div v-for="[cat, v] in byCategory" :key="cat" class="cat-row">
            <span class="cat-name">{{ categoryLabel(cat) }}</span>
            <div class="cat-bar"><div class="cat-fill" :style="{ width: (v / totalSpend * 100) + '%' }" /></div>
            <span class="cat-n">{{ won(v) }}</span>
          </div>
        </div>
      </div>

      <!-- 자주 산 상품 -->
      <div class="card section" v-if="topProducts.length">
        <h2 class="section-title">자주 구매한 상품 Top {{ topProducts.length }}</h2>
        <ol class="top-list">
          <li v-for="[name, qty] in topProducts" :key="name" class="top-row">
            <span class="top-emoji">{{ thumbEmoji({ name }) }}</span>
            <span class="top-name">{{ name }}</span>
            <span class="top-qty">{{ qty }}개</span>
          </li>
        </ol>
      </div>

      <!-- 최근 주문 + 리뷰 작성률 -->
      <div class="card section">
        <div class="section-head">
          <h2 class="section-title">최근 주문</h2>
          <span class="review-rate">리뷰 작성률 <strong>{{ reviewRate }}%</strong></span>
        </div>
        <table class="ord-table">
          <thead>
            <tr><th>상품</th><th>카테고리</th><th>주문일</th><th class="num">수량</th><th class="num">결제액</th><th>리뷰</th></tr>
          </thead>
          <tbody>
            <tr v-for="o in recentOrders" :key="o.orderId">
              <td class="name">{{ thumbEmoji({ name: o.productName }) }} {{ o.productName }}</td>
              <td>{{ categoryLabel(o.category) }}</td>
              <td class="muted">{{ dateOnly(o.orderDate) }}</td>
              <td class="num">{{ o.quantity }}</td>
              <td class="num price">{{ won(o.totalPrice) }}</td>
              <td><span :class="o.reviewId ? 'done' : 'todo'">{{ o.reviewId ? '완료' : '미작성' }}</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </div>
</template>

<style scoped>
.page-head { margin-bottom: 18px; }
.page-head h1 { font-size: 22px; margin: 0 0 4px; }

.report { padding: 16px 18px; margin-bottom: 18px; border-left: 4px solid var(--color-primary); }
.report-tag { font-weight: 800; color: var(--color-primary-dark); font-size: 14px; margin-bottom: 6px; }
.report-body { margin: 0; font-size: 15px; line-height: 1.5; font-weight: 600; }
.report-note, .report-ctx { margin: 8px 0 0; font-size: 12px; }
.report-badge { margin-left: 8px; font-size: 11px; font-weight: 700; color: #fff; background: var(--color-primary); padding: 2px 7px; border-radius: 999px; vertical-align: middle; }
.type-badge { margin-left: 6px; font-size: 11px; font-weight: 700; color: var(--color-primary-dark); background: var(--color-primary-soft); padding: 2px 9px; border-radius: 999px; vertical-align: middle; }

.rec-card { padding: 18px; margin-bottom: 18px; border-left: 4px solid #f39c12; }
.rec-title { font-size: 14px; font-weight: 800; color: #d68910; margin-bottom: 4px; }
.rec-desc { font-size: 12px; margin: 0 0 14px; }
.rec-list { margin: 0; padding: 0; list-style: none; display: flex; flex-direction: column; gap: 10px; }
.rec-item { display: flex; align-items: flex-start; gap: 10px; }
.rec-num { width: 22px; height: 22px; flex-shrink: 0; background: #f39c12; color: #fff; border-radius: 50%; font-size: 12px; font-weight: 800; display: flex; align-items: center; justify-content: center; }
.rec-text { font-size: 14px; line-height: 1.5; flex: 1; }

.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 18px; }
@media (max-width: 760px) { .kpi-grid { grid-template-columns: repeat(2, 1fr); } }
.kpi { padding: 16px 18px; display: flex; flex-direction: column; gap: 4px; }
.kpi-label { font-size: 13px; color: var(--color-muted); }
.kpi-value { font-size: 24px; font-weight: 800; }
.kpi-sub { font-size: 12px; color: var(--color-muted); }
.kpi-sub.up { color: #c1272d; }
.kpi-sub.down { color: var(--color-primary-dark); }
.kpi.good { border-top: 3px solid var(--color-primary); }
.kpi.good .kpi-value { color: var(--color-primary-dark); }

.section { padding: 18px; margin-bottom: 18px; }
.section-title { font-size: 16px; margin: 0 0 14px; }
.section-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; }
.section-head .section-title { margin: 0; }
.review-rate { font-size: 13px; color: var(--color-muted); }
.review-rate strong { color: var(--color-primary-dark); font-size: 15px; }

/* 월별 지출 막대 차트 */
.month-chart { display: flex; align-items: flex-end; gap: 12px; height: 160px; padding-top: 8px; }
.month-col { flex: 1; display: flex; flex-direction: column; align-items: center; height: 100%; justify-content: flex-end; gap: 6px; }
.month-val { font-size: 11px; color: var(--color-muted); }
.month-bar { width: 100%; max-width: 46px; flex: 1; display: flex; align-items: flex-end; }
.month-fill { width: 100%; background: var(--color-primary); border-radius: 6px 6px 0 0; min-height: 4px; transition: height .3s; }
.month-label { font-size: 12px; font-weight: 600; }

.cat-list { display: flex; flex-direction: column; gap: 10px; }
.cat-row { display: grid; grid-template-columns: 72px 1fr 90px; align-items: center; gap: 12px; }
.cat-name { font-size: 14px; font-weight: 600; }
.cat-bar { background: var(--color-primary-soft); border-radius: 999px; height: 12px; overflow: hidden; }
.cat-fill { background: var(--color-primary); height: 100%; border-radius: 999px; }
.cat-n { font-size: 13px; color: var(--color-muted); text-align: right; }

.top-list { margin: 0; padding: 0; list-style: none; display: flex; flex-direction: column; gap: 8px; counter-reset: rank; }
.top-row { display: flex; align-items: center; gap: 10px; counter-increment: rank; }
.top-row::before { content: counter(rank); width: 22px; height: 22px; flex-shrink: 0; background: var(--color-primary-soft); color: var(--color-primary-dark); border-radius: 50%; font-size: 12px; font-weight: 800; display: flex; align-items: center; justify-content: center; }
.top-emoji { font-size: 20px; }
.top-name { flex: 1; font-weight: 600; font-size: 14px; }
.top-qty { font-size: 13px; color: var(--color-muted); }

.ord-table { width: 100%; border-collapse: collapse; font-size: 14px; }
.ord-table th, .ord-table td { padding: 10px 8px; border-bottom: 1px solid var(--color-border); text-align: left; }
.ord-table th { font-size: 12px; color: var(--color-muted); font-weight: 700; }
.ord-table .num { text-align: right; }
.ord-table .name { font-weight: 700; }
.ord-table .price { font-weight: 700; }
.ord-table .done { font-size: 12px; color: var(--color-primary-dark); font-weight: 700; }
.ord-table .todo { font-size: 12px; color: var(--color-muted); }
</style>
