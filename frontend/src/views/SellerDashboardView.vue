<script setup>
import { ref, computed, onMounted } from 'vue'
import { productApi } from '../api/products'
import { won, riskMeta, dDayLabel, categoryLabel } from '../utils/format'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const products = ref([])
const loading = ref(true)
const error = ref('')

const aiReport = ref(null)

onMounted(load)
async function load() {
  loading.value = true
  error.value = ''
  try {
    products.value = (await productApi.sellerProducts()) || []
    // 진짜 LLM 요약(실패/미설정 시 규칙기반 summary로 폴백)
    aiReport.value = await productApi.sellerReport().catch(() => null)
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

const atRisk = computed(() =>
  products.value.filter((p) => p.riskLevel === 'HIGH' || p.riskLevel === 'MEDIUM')
)

const counts = computed(() => {
  const c = { HIGH: 0, MEDIUM: 0, LOW: 0, EXPIRED: 0 }
  products.value.forEach((p) => { c[p.riskLevel] = (c[p.riskLevel] || 0) + 1 })
  return c
})

// 방치 시 예상 폐기손실(정가 기준) vs AI 할인가로 회수 예상
const wasteLoss = computed(() =>
  atRisk.value.reduce((s, p) => s + (p.stockQty || 0) * (p.price || 0), 0)
)
const recovered = computed(() =>
  atRisk.value.reduce((s, p) => s + (p.stockQty || 0) * (p.discountedPrice ?? p.price ?? 0), 0)
)
const recoverRate = computed(() =>
  wasteLoss.value ? Math.round((recovered.value / wasteLoss.value) * 100) : 0
)

const byCategory = computed(() => {
  const m = {}
  atRisk.value.forEach((p) => { const k = p.category || '기타'; m[k] = (m[k] || 0) + 1 })
  return Object.entries(m).sort((a, b) => b[1] - a[1])
})

const riskTable = computed(() =>
  [...atRisk.value].sort(
    (a, b) => (a.daysToExpiry ?? 999) - (b.daysToExpiry ?? 999) || (b.riskScore ?? 0) - (a.riskScore ?? 0)
  )
)

// AI 요약 리포트 (현재는 규칙 기반 자동 생성 — 추후 배치 LLM 요약으로 대체)
const summary = computed(() => {
  const n = atRisk.value.length
  if (!n) return '오늘 폐기위험 상품이 없습니다. 재고 상태가 양호합니다.'
  return `오늘 폐기위험 상품 ${n}개. 방치 시 약 ${won(wasteLoss.value)}의 손실이 예상되며, ` +
    `AI 추천 할인가 적용 시 약 ${won(recovered.value)}(${recoverRate.value}%)를 회수할 수 있습니다.`
})
</script>

<template>
  <div>
    <div class="page-head">
      <h1>📊 판매자 폐기 대시보드</h1>
      <p class="muted">{{ auth.user?.name }}님 · 재고 폐기위험과 AI 추천 할인가를 한눈에</p>
    </div>

    <div v-if="loading" class="empty"><span class="emoji">⏳</span>불러오는 중…</div>
    <div v-else-if="error" class="empty">
      <span class="emoji">⚠️</span>{{ error }}<br />
      <button class="btn btn-outline" style="margin-top:12px" @click="load">다시 시도</button>
    </div>

    <template v-else>
      <!-- AI 요약 리포트 -->
      <div class="report card">
        <div class="report-tag">🤖 AI 요약 리포트<span v-if="aiReport" class="report-badge">GMS</span></div>
        <p class="report-body">{{ aiReport?.summary || summary }}</p>
        <p v-if="aiReport?.usedData?.length" class="report-ctx muted">🔎 AI가 참고한 데이터: {{ aiReport.usedData.join(' · ') }}</p>
        <p v-else class="report-note muted">※ AI 연결 전이라 규칙 기반 요약입니다.</p>
      </div>

      <!-- KPI -->
      <div class="kpi-grid">
        <div class="kpi card">
          <span class="kpi-label">전체 상품</span>
          <span class="kpi-value">{{ products.length }}개</span>
        </div>
        <div class="kpi card danger">
          <span class="kpi-label">폐기위험 상품</span>
          <span class="kpi-value">{{ atRisk.length }}개</span>
          <span class="kpi-sub">HIGH {{ counts.HIGH }} · MEDIUM {{ counts.MEDIUM }}</span>
        </div>
        <div class="kpi card">
          <span class="kpi-label">방치 시 예상 폐기손실</span>
          <span class="kpi-value">{{ won(wasteLoss) }}</span>
        </div>
        <div class="kpi card good">
          <span class="kpi-label">AI 할인가 회수 예상</span>
          <span class="kpi-value">{{ won(recovered) }}</span>
          <span class="kpi-sub">회수율 {{ recoverRate }}%</span>
        </div>
      </div>

      <!-- 카테고리별 위험 분포 -->
      <div class="card section" v-if="byCategory.length">
        <h2 class="section-title">카테고리별 위험 상품 분포</h2>
        <div class="cat-list">
          <div v-for="[cat, n] in byCategory" :key="cat" class="cat-row">
            <span class="cat-name">{{ categoryLabel(cat) }}</span>
            <div class="cat-bar">
              <div class="cat-fill" :style="{ width: (n / atRisk.length * 100) + '%' }" />
            </div>
            <span class="cat-n">{{ n }}개</span>
          </div>
        </div>
      </div>

      <!-- 위험 상품 테이블 -->
      <div class="card section">
        <h2 class="section-title">폐기위험 상품 · AI 추천 할인가 ({{ riskTable.length }}건)</h2>
        <div v-if="!riskTable.length" class="empty-inline muted">현재 위험 상품이 없습니다 👍</div>
        <table v-else class="risk-table">
          <thead>
            <tr>
              <th>상품</th><th>카테고리</th><th>유통기한</th><th>위험</th>
              <th class="num">재고</th><th class="num">정가</th><th class="num">AI 할인가</th><th class="num">회수 예상</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in riskTable" :key="p.productId">
              <td class="name">{{ p.name }}</td>
              <td>{{ categoryLabel(p.category) }}</td>
              <td>
                <span class="dday" :class="riskMeta(p.riskLevel).cls">{{ dDayLabel(p.daysToExpiry) }}</span>
              </td>
              <td><span class="risk-chip" :class="riskMeta(p.riskLevel).cls">{{ riskMeta(p.riskLevel).label }}</span></td>
              <td class="num">{{ p.stockQty }}</td>
              <td class="num orig">{{ won(p.price) }}</td>
              <td class="num deal">{{ won(p.discountedPrice) }} <small>({{ p.discountRate }}%)</small></td>
              <td class="num">{{ won((p.stockQty || 0) * (p.discountedPrice ?? p.price ?? 0)) }}</td>
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
.report-note { margin: 8px 0 0; font-size: 12px; }
.report-ctx { margin: 8px 0 0; font-size: 12px; }
.report-badge { margin-left: 8px; font-size: 11px; font-weight: 700; color: #fff; background: var(--color-primary); padding: 2px 7px; border-radius: 999px; vertical-align: middle; }

.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 18px; }
@media (max-width: 760px) { .kpi-grid { grid-template-columns: repeat(2, 1fr); } }
.kpi { padding: 16px 18px; display: flex; flex-direction: column; gap: 4px; }
.kpi-label { font-size: 13px; color: var(--color-muted); }
.kpi-value { font-size: 24px; font-weight: 800; }
.kpi-sub { font-size: 12px; color: var(--color-muted); }
.kpi.danger { border-top: 3px solid #e5484d; }
.kpi.danger .kpi-value { color: #c1272d; }
.kpi.good { border-top: 3px solid var(--color-primary); }
.kpi.good .kpi-value { color: var(--color-primary-dark); }

.section { padding: 18px; margin-bottom: 18px; }
.section-title { font-size: 16px; margin: 0 0 14px; }

.cat-list { display: flex; flex-direction: column; gap: 10px; }
.cat-row { display: grid; grid-template-columns: 80px 1fr 48px; align-items: center; gap: 12px; }
.cat-name { font-size: 14px; font-weight: 600; }
.cat-bar { background: var(--color-primary-soft); border-radius: 999px; height: 12px; overflow: hidden; }
.cat-fill { background: #e5484d; height: 100%; border-radius: 999px; }
.cat-n { font-size: 13px; color: var(--color-muted); text-align: right; }

.risk-table { width: 100%; border-collapse: collapse; font-size: 14px; }
.risk-table th, .risk-table td { padding: 10px 8px; border-bottom: 1px solid var(--color-border); text-align: left; }
.risk-table th { font-size: 12px; color: var(--color-muted); font-weight: 700; }
.risk-table .num { text-align: right; }
.risk-table .name { font-weight: 700; }
.risk-table .orig { color: var(--color-muted); text-decoration: line-through; }
.risk-table .deal { color: #c1272d; font-weight: 800; }
.risk-table .deal small { font-weight: 600; }

.dday { font-size: 12px; font-weight: 800; color: #fff; padding: 2px 8px; border-radius: 999px; background: #9aa0a6; }
.dday.risk-high { background: #e5484d; }
.dday.risk-medium { background: #f59e0b; }
.dday.risk-low { background: #7a8085; }

.risk-chip { font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 999px; }
.risk-chip.risk-high { background: #fdecec; color: #c1272d; }
.risk-chip.risk-medium { background: #fef3e2; color: #b76e00; }
.risk-chip.risk-low { background: #eef1f3; color: #7a8085; }

.empty-inline { padding: 24px; text-align: center; }
</style>
