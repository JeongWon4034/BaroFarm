<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { productApi } from '../api/products'
import { won, categoryLabel, dDayLabel, dateOnly, expiryStatus, thumbEmoji } from '../utils/format'

const products = ref([])
const salesMap = ref({})     // productId → 판매 분석
const insightMap = ref({})   // productId → KAMIS소매가·현재가·추천가·정체신호
const expandedId = ref(null) // 표에서 펼쳐진 상품
const loading = ref(true)
const error = ref('')

// 정체 상품 hover 시 AI 행동 추천 (lazy + 캐시)
const actionCache = ref({})    // productId → 행동추천 응답
const actionLoading = ref(null) // 현재 불러오는 productId
const hoveredId = ref(null)     // 추천가 팝오버가 열린 productId

const CATEGORIES = ['vegetable', 'fruit', 'seafood', 'meat', 'grain', 'etc']

const showForm = ref(false)
const editingId = ref(null)
const saving = ref(false)
const formError = ref('')
const blank = () => ({ name: '', category: 'vegetable', price: null, stockQty: null, expirationDate: '', description: '', thumbnailUrl: '', unit: '' })
const form = reactive(blank())

const formTitle = computed(() => (editingId.value ? '상품 수정' : '상품 등록'))

onMounted(load)
async function load() {
  loading.value = true
  error.value = ''
  try {
    const [prods, sales, insights] = await Promise.all([
      productApi.sellerProducts(),
      productApi.sellerSales().catch(() => []),     // 분석 실패해도 목록은 보여줌
      productApi.sellerInsights().catch(() => []),  // 인사이트 실패해도 목록은 보여줌
    ])
    products.value = prods || []
    const sm = {}; for (const s of (sales || [])) sm[s.productId] = s
    salesMap.value = sm
    const im = {}; for (const i of (insights || [])) im[i.productId] = i
    insightMap.value = im
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

function salesOf(p) { return salesMap.value[p.productId] || null }
function insightOf(p) { return insightMap.value[p.productId] || null }
function toggleExpand(id) { expandedId.value = expandedId.value === id ? null : id }

// 정체 상품 추천가에 hover → AI 행동 추천 lazy 로드(캐시)
async function openAction(p) {
  const ins = insightOf(p)
  if (!ins || !ins.stale) return
  hoveredId.value = p.productId
  if (actionCache.value[p.productId] || actionLoading.value === p.productId) return
  actionLoading.value = p.productId
  try {
    actionCache.value[p.productId] = await productApi.productAction(p.productId)
  } catch (e) {
    actionCache.value[p.productId] = { action: '추천을 불러오지 못했어요. 잠시 후 다시 시도해주세요.' }
  } finally {
    actionLoading.value = null
  }
}
function closeAction() { hoveredId.value = null }
function sparkMax(daily) { return Math.max(1, ...((daily || []).map(d => d.qty))) }
function pct(v, lo, hi) { return hi <= lo ? 50 : Math.min(100, Math.max(0, (v - lo) / (hi - lo) * 100)) }
const naverSearchUrl = computed(() =>
  `https://search.shopping.naver.com/search/all?query=${encodeURIComponent((form.name || '').trim())}`)

function openCreate() {
  editingId.value = null
  Object.assign(form, blank())
  formError.value = ''
  resetAi()
  showForm.value = true
}

function openEdit(p) {
  editingId.value = p.productId
  Object.assign(form, {
    name: p.name,
    category: p.category || 'vegetable',
    price: p.price,
    stockQty: p.stockQty,
    expirationDate: p.expirationDate ? dateOnly(p.expirationDate) : '',
    description: p.description || '',
    thumbnailUrl: p.thumbnailUrl || '',
  })
  formError.value = ''
  resetAi()
  showForm.value = true
}

function resetAi() {
  aiMsg.value = ''
  priceResult.value = null
}

function closeForm() {
  showForm.value = false
}

async function submit() {
  formError.value = ''
  if (!form.name.trim()) { formError.value = '상품명을 입력하세요.'; return }
  if (form.price == null || form.price < 0) { formError.value = '가격을 올바르게 입력하세요.'; return }
  if (form.stockQty == null || form.stockQty < 0) { formError.value = '재고를 올바르게 입력하세요.'; return }
  saving.value = true
  try {
    const payload = {
      name: form.name.trim(),
      category: form.category,
      price: Number(form.price),
      stockQty: Number(form.stockQty),
      expirationDate: form.expirationDate || null,
      description: form.description.trim(),
      thumbnailUrl: form.thumbnailUrl.trim() || null,
    }
    if (editingId.value) {
      await productApi.update(editingId.value, payload)
    } else {
      await productApi.create(payload)
    }
    showForm.value = false
    await load()
  } catch (e) {
    formError.value = e.message
  } finally {
    saving.value = false
  }
}

// --- 이미지 업로드 ---
const fileInput = ref(null)
const imgUploading = ref(false)
async function onPickImage(e) {
  const file = e.target.files?.[0]
  if (!file) return
  imgUploading.value = true
  formError.value = ''
  try {
    const res = await productApi.uploadImage(file)
    form.thumbnailUrl = res.url
  } catch (err) {
    formError.value = err.message || '이미지 업로드에 실패했어요.'
  } finally {
    imgUploading.value = false
    e.target.value = '' // 같은 파일 재선택 허용
  }
}

// --- AI 등록 도우미 ---
const aiPriceLoading = ref(false)
const aiDescLoading = ref(false)
const aiMsg = ref('')
const priceResult = ref(null) // 추천가 응답(원가·경쟁가 근거 포함). 신규 등록 시에만 노출.
const imgError = ref({})      // 경쟁사 이미지 로드 실패 인덱스 → 이모지 폴백(배포 핫링크 차단 대비)
const phEmoji = computed(() => thumbEmoji({ category: form.category, name: form.name }))

async function suggestPrice() {
  if (!form.name.trim()) { formError.value = '상품명을 먼저 입력하세요.'; return }
  aiMsg.value = ''
  priceResult.value = null
  imgError.value = {}
  aiPriceLoading.value = true
  try {
    const s = await productApi.priceSuggestion(form.name, form.category, form.unit)
    if (s.suggestedPrice) form.price = s.suggestedPrice
    priceResult.value = s
  } catch (e) {
    formError.value = e.message
  } finally {
    aiPriceLoading.value = false
  }
}

async function generateDesc() {
  if (!form.name.trim()) { formError.value = '상품명을 먼저 입력하세요.'; return }
  aiMsg.value = ''
  priceResult.value = null
  aiDescLoading.value = true
  try {
    const r = await productApi.generateDescription({
      name: form.name.trim(),
      category: form.category,
      expirationDate: form.expirationDate || null,
      stockQty: form.stockQty,
    })
    form.description = r.description
    const ctx = (r.usedContext || []).join(' · ')
    aiMsg.value = '✍️ AI가 설명을 생성했어요.' + (ctx ? `\n🔎 AI가 참고한 정보: ${ctx}` : '')
  } catch (e) {
    aiMsg.value = e.message
  } finally {
    aiDescLoading.value = false
  }
}

async function remove(p) {
  if (!confirm(`'${p.name}' 상품을 삭제할까요?`)) return
  try {
    await productApi.remove(p.productId)
    await load()
  } catch (e) {
    alert(e.message)
  }
}
</script>

<template>
  <div>
    <div class="page-head">
      <div>
        <h1>📦 상품 관리</h1>
        <p class="muted">KAMIS 시세 대비 추천가·판매 추이를 확인하고, 정체 상품은 추천가에 마우스를 올려 AI 행동 제안을 받으세요.</p>
      </div>
      <button class="btn btn-primary" @click="openCreate">➕ 상품 등록</button>
    </div>

    <!-- 등록/수정 폼 -->
    <div v-if="showForm" class="card form-card">
      <div class="form-head">
        <h2>{{ formTitle }}</h2>
        <button class="link-btn" @click="closeForm">✕ 닫기</button>
      </div>
      <div class="grid-form">
        <label class="fld span2"><span>상품명 *</span><input v-model="form.name" class="input" placeholder="예: 무농약 청상추" /></label>
        <label class="fld"><span>카테고리</span>
          <select v-model="form.category" class="select">
            <option v-for="c in CATEGORIES" :key="c" :value="c">{{ categoryLabel(c) }}</option>
          </select>
        </label>
        <label class="fld"><span>유통기한</span><input v-model="form.expirationDate" type="date" class="input" /></label>
        <label v-if="!editingId" class="fld span2"><span>판매 단위 <span class="fld-hint">(AI 추천가용 · 선택 — 비우면 AI가 상품명에서 추론)</span></span><input v-model="form.unit" class="input" placeholder="예: 1kg, 500g, 1단, 5개입" /></label>
        <div v-if="!editingId" class="span2">
          <button type="button" class="ai-cta" :disabled="aiPriceLoading" @click="suggestPrice">
            <span class="ai-cta-icon">💡</span>
            <span class="ai-cta-text">
              <strong>{{ aiPriceLoading ? 'AI가 시세·경쟁가 분석 중…' : 'AI 추천가 받기' }}</strong>
              <small>KAMIS 시세 + 네이버 경쟁 소매가를 분석해 최적 판매가를 제안해드려요</small>
            </span>
            <span class="ai-cta-arrow">{{ aiPriceLoading ? '⏳' : '→' }}</span>
          </button>
        </div>
        <div class="fld">
          <span>가격(원) *</span>
          <input v-model.number="form.price" type="number" min="0" class="input" placeholder="0" />
        </div>
        <label class="fld"><span>재고(개) *</span><input v-model.number="form.stockQty" type="number" min="0" class="input" placeholder="0" /></label>
        <div class="fld span2">
          <span class="fld-top">설명
            <button type="button" class="ai-btn" :disabled="aiDescLoading" @click="generateDesc">{{ aiDescLoading ? '생성 중…' : '✍️ AI 설명 생성' }}</button>
          </span>
          <input v-model="form.description" class="input" placeholder="상품 설명 (AI 생성 가능)" />
        </div>
        <div class="fld span2">
          <span>상품 이미지 <span class="fld-hint">(선택 — 비우면 이모지로 표시)</span></span>
          <div class="img-upload">
            <div class="img-preview" :class="{ empty: !form.thumbnailUrl }">
              <img v-if="form.thumbnailUrl" :src="form.thumbnailUrl" alt="상품 이미지 미리보기" />
              <span v-else class="img-ph">🖼️</span>
            </div>
            <div class="img-actions">
              <input ref="fileInput" type="file" accept="image/*" class="hidden-file" @change="onPickImage" />
              <button type="button" class="btn btn-outline btn-sm" :disabled="imgUploading" @click="fileInput?.click()">
                {{ imgUploading ? '업로드 중…' : (form.thumbnailUrl ? '🔄 이미지 변경' : '📷 이미지 업로드') }}
              </button>
              <button v-if="form.thumbnailUrl" type="button" class="link-btn danger" @click="form.thumbnailUrl = ''">제거</button>
              <p class="img-hint">jpg · png · webp · gif · 최대 5MB</p>
              <input v-model="form.thumbnailUrl" class="input url-input" placeholder="또는 이미지 URL 직접 입력" />
            </div>
          </div>
        </div>
      </div>
      <p v-if="aiMsg" class="ai-msg">{{ aiMsg }}</p>

      <!-- AI 추천가 패널 — 신규 등록 시에만 노출. 원가(KAMIS)·경쟁 소매가 분포와 그 출처를 함께 보여준다. -->
      <div v-if="priceResult && !editingId" class="price-panel">
        <div class="pp-head">
          <span class="pp-title">💡 AI 추천 판매가</span>
          <span class="pp-engine" :class="priceResult.engine === 'LLM' ? 'is-ai' : 'is-rule'">
            {{ priceResult.engine === 'LLM' ? 'AI 종합 분석' : '시세 산식' }}
          </span>
        </div>

        <div v-if="priceResult.suggestedPrice" class="pp-price">
          {{ Number(priceResult.suggestedPrice).toLocaleString() }}<span class="won">원</span>
          <span v-if="priceResult.sellUnit" class="pp-unit">/ {{ priceResult.sellUnit }} 기준</span>
        </div>
        <p v-if="priceResult.reason" class="pp-reason">{{ priceResult.reason }}</p>
        <p v-if="priceResult.unitBasis" class="pp-unitbasis">📐 단위 환산: {{ priceResult.unitBasis }}</p>

        <!-- 원가 시세: KAMIS -->
        <div v-if="priceResult.marketPrice" class="pp-block">
          <div class="pp-block-head">
            <span class="pp-label">원가 시세</span>
            <span class="pp-source">출처 · KAMIS(농수산물유통정보, aT)</span>
          </div>
          <div class="pp-row">
            <strong>{{ priceResult.marketItem }}<span v-if="priceResult.marketUnit"> ({{ priceResult.marketUnit }})</span></strong>
            <span>당일 {{ Number(priceResult.marketPrice).toLocaleString() }}원</span>
            <span v-if="priceResult.marketMonthAgo" class="muted">1개월 전 {{ Number(priceResult.marketMonthAgo).toLocaleString() }}원</span>
            <span v-if="priceResult.marketYearAgo" class="muted">1년 전 {{ Number(priceResult.marketYearAgo).toLocaleString() }}원</span>
          </div>
        </div>

        <!-- 경쟁 소매가: 네이버 쇼핑 (분포 바 + 실제 상품 카드) -->
        <div v-if="priceResult.competitorCount" class="pp-block">
          <div class="pp-block-head">
            <span class="pp-label">경쟁 소매가 분포</span>
            <span class="pp-source">출처 · 네이버 쇼핑 검색 ({{ priceResult.competitorCount }}개 몰)</span>
          </div>

          <!-- 최저~최고 레인지 바 + 평균/추천가 마커 -->
          <div class="pp-bar">
            <div class="pp-bar-track">
              <div class="pp-bar-fill"
                   :style="{ left: pct(priceResult.competitorAvg, priceResult.competitorLow, priceResult.competitorHigh) + '%' }"></div>
              <div v-if="priceResult.suggestedPrice" class="pp-bar-rec"
                   :style="{ left: pct(priceResult.suggestedPrice, priceResult.competitorLow, priceResult.competitorHigh) + '%' }"
                   :title="'추천가 ' + Number(priceResult.suggestedPrice).toLocaleString() + '원'"></div>
            </div>
            <div class="pp-bar-labels">
              <span>최저 <strong>{{ Number(priceResult.competitorLow).toLocaleString() }}</strong></span>
              <span>평균 <strong>{{ Number(priceResult.competitorAvg).toLocaleString() }}</strong></span>
              <span>최고 <strong>{{ Number(priceResult.competitorHigh).toLocaleString() }}</strong></span>
            </div>
            <p class="pp-bar-legend"><i class="dot rec"></i> 내 추천가 위치 · <i class="dot avg"></i> 경쟁 평균</p>
          </div>

          <!-- 실제 판매 상품 카드(썸네일) — 판매자가 어떻게 팔리는지 눈으로 확인 -->
          <div class="pp-cards">
            <a v-for="(c, i) in priceResult.competitors" :key="i" class="pp-card"
               :href="c.link || undefined" :target="c.link ? '_blank' : undefined" rel="noopener noreferrer">
              <div class="pp-card-thumb">
                <img v-if="c.image && !imgError[i]" :src="c.image" :alt="c.title" loading="lazy"
                     referrerpolicy="no-referrer" @error="imgError[i] = true" />
                <span v-else class="noimg">{{ phEmoji }}</span>
              </div>
              <div class="pp-card-body">
                <span class="pp-card-mall">{{ c.mall || '판매처' }}</span>
                <span class="pp-card-title">{{ c.title }}</span>
                <span class="pp-card-price">{{ Number(c.price).toLocaleString() }}원</span>
              </div>
            </a>
          </div>

          <a class="pp-naver-link" :href="naverSearchUrl" target="_blank" rel="noopener noreferrer">
            🔎 네이버 쇼핑에서 '{{ form.name }}' 실제 검색결과 전체 보기 →
          </a>
        </div>

        <p v-if="priceResult.source === 'CATALOG'" class="pp-note">
          KAMIS·경쟁가 매칭이 없어 자체 마켓 통계({{ priceResult.catalogCount }}개 평균)로 추천했어요. 상품명을 일반 명칭으로 적으면 시세·경쟁가 기반으로 더 정확해집니다.
        </p>
        <p v-else-if="priceResult.source === 'NONE'" class="pp-note">{{ priceResult.basis }}</p>
      </div>

      <p v-if="formError" class="err">{{ formError }}</p>
      <div class="form-actions">
        <button class="btn btn-outline" @click="closeForm">취소</button>
        <button class="btn btn-primary" :disabled="saving" @click="submit">{{ saving ? '저장 중…' : (editingId ? '수정' : '등록') }}</button>
      </div>
    </div>

    <div v-if="loading" class="empty"><span class="emoji">⏳</span>불러오는 중…</div>
    <div v-else-if="error" class="empty"><span class="emoji">⚠️</span>{{ error }}</div>
    <div v-else-if="products.length === 0" class="empty"><span class="emoji">📦</span>등록된 상품이 없어요. 위 "상품 등록"으로 추가하세요.</div>

    <table v-else class="tbl">
      <thead>
        <tr>
          <th>상품</th><th>카테고리</th><th>유통기한</th><th>위험</th>
          <th class="num">KAMIS 소매가</th><th class="num">현재 판매가</th><th class="num">추천 판매가</th><th class="num">재고</th>
          <th>판매 추이 (14일)</th><th></th>
        </tr>
      </thead>
      <tbody>
        <template v-for="p in products" :key="p.productId">
          <tr class="row" :class="{ open: expandedId === p.productId }" @click="toggleExpand(p.productId)">
            <td class="name">{{ p.name }}</td>
            <td>{{ categoryLabel(p.category) }}</td>
            <td><span class="dday" :class="expiryStatus(p.daysToExpiry).cls">{{ dDayLabel(p.daysToExpiry) }}</span></td>
            <td><span class="risk-chip" :class="expiryStatus(p.daysToExpiry).cls">{{ expiryStatus(p.daysToExpiry).label }}</span></td>
            <!-- KAMIS 기준 소매가 -->
            <td class="num">
              <template v-if="insightOf(p)?.kamisPrice">{{ won(insightOf(p).kamisPrice) }}<span v-if="insightOf(p).kamisUnit" class="cell-unit">/{{ insightOf(p).kamisUnit }}</span></template>
              <span v-else class="muted">—</span>
            </td>
            <!-- 현재 판매가 -->
            <td class="num cur-price">{{ won(insightOf(p)?.currentPrice ?? p.price) }}</td>
            <!-- 추천 판매가 (+ 정체 시 hover 행동 추천) -->
            <td class="num rec-cell" @click.stop>
              <template v-if="insightOf(p)?.recommendedPrice">
                <span class="rec-price" :class="{ stale: insightOf(p).stale }"
                      @mouseenter="openAction(p)" @mouseleave="closeAction">
                  {{ won(insightOf(p).recommendedPrice) }}
                  <i v-if="insightOf(p).stale" class="stale-dot">●</i>
                </span>
                <div v-if="hoveredId === p.productId && insightOf(p).stale" class="action-pop"
                     @mouseenter="hoveredId = p.productId" @mouseleave="closeAction">
                  <div v-if="actionLoading === p.productId" class="ap-loading">🤖 AI가 행동을 분석 중…</div>
                  <template v-else>
                    <div class="ap-head">⚠️ {{ actionCache[p.productId]?.headline || '판매 정체' }}
                      <span v-if="actionCache[p.productId]?.engine === 'LLM'" class="ap-engine">AI</span>
                    </div>
                    <p class="ap-body">{{ actionCache[p.productId]?.action }}</p>
                    <div v-if="actionCache[p.productId]?.recommendedPrice" class="ap-rec">
                      추천가 <strong>{{ won(actionCache[p.productId].recommendedPrice) }}</strong>
                      <span class="ap-cur">(현재 {{ won(actionCache[p.productId].currentPrice) }})</span>
                    </div>
                  </template>
                </div>
              </template>
              <span v-else class="muted">—</span>
            </td>
            <td class="num">{{ p.stockQty }}</td>
            <td class="trend-cell">
              <template v-if="salesOf(p) && salesOf(p).soldQty > 0">
                <span class="mini-spark">
                  <i v-for="(d, i) in salesOf(p).daily14" :key="i"
                     :style="{ height: (4 + d.qty / sparkMax(salesOf(p).daily14) * 18) + 'px' }"></i>
                </span>
                <span class="trend-sum">누적 {{ salesOf(p).soldQty }}개</span>
                <span class="caret">{{ expandedId === p.productId ? '▴' : '▾' }}</span>
              </template>
              <span v-else class="muted">판매 없음</span>
            </td>
            <td class="actions" @click.stop>
              <button class="link-btn" @click="openEdit(p)">수정</button>
              <button class="link-btn danger" @click="remove(p)">삭제</button>
            </td>
          </tr>

          <!-- 판매 분석 상세 (펼침) -->
          <tr v-if="expandedId === p.productId" class="detail-row">
            <td :colspan="10">
              <div v-if="salesOf(p) && salesOf(p).orderCount > 0" class="sales-panel">
                <div class="sp-kpis">
                  <div class="kpi"><span class="k-label">총 판매량</span><span class="k-val">{{ salesOf(p).soldQty }}<i>개</i></span></div>
                  <div class="kpi"><span class="k-label">매출</span><span class="k-val">{{ won(salesOf(p).revenue) }}</span></div>
                  <div class="kpi"><span class="k-label">마감임박 회수</span><span class="k-val">{{ won(salesOf(p).saved) }}</span></div>
                  <div class="kpi"><span class="k-label">마감임박 비중</span><span class="k-val">{{ salesOf(p).soldQty ? Math.round(salesOf(p).deadlineQty / salesOf(p).soldQty * 100) : 0 }}<i>%</i></span></div>
                  <div class="kpi"><span class="k-label">주문 건수</span><span class="k-val">{{ salesOf(p).orderCount }}<i>건</i></span></div>
                  <div class="kpi"><span class="k-label">최근 판매</span><span class="k-val sm">{{ salesOf(p).lastOrderDate || '—' }}</span></div>
                </div>
                <div class="sp-chart">
                  <div class="spc-head">최근 14일 일별 판매량</div>
                  <div class="bars">
                    <div v-for="(d, i) in salesOf(p).daily14" :key="i" class="bar-col">
                      <span class="bar-qty" :class="{ zero: d.qty === 0 }">{{ d.qty || '' }}</span>
                      <i class="bar" :style="{ height: (d.qty / sparkMax(salesOf(p).daily14) * 70) + 'px' }"></i>
                      <span class="bar-day">{{ d.date }}</span>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="sales-empty">아직 이 상품의 판매 기록이 없어요. 첫 주문이 들어오면 여기에 추이가 쌓입니다.</div>
            </td>
          </tr>
        </template>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.page-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; margin-bottom: 18px; }
.page-head h1 { font-size: 22px; margin: 0 0 4px; }

.form-card { padding: 18px; margin-bottom: 20px; }
.form-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; }
.form-head h2 { font-size: 17px; margin: 0; }
.grid-form { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.fld { display: flex; flex-direction: column; gap: 5px; font-size: 13px; font-weight: 600; color: var(--color-muted); }
.fld .input, .fld .select { font-weight: 500; color: var(--color-text); }
.fld.span2 { grid-column: 1 / -1; }
.fld-top { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.fld-hint { font-weight: 500; color: var(--color-muted); font-size: 11px; }
/* 이미지 업로드 */
.img-upload { display: flex; gap: 14px; align-items: flex-start; }
.img-preview { width: 96px; height: 96px; flex-shrink: 0; border-radius: var(--radius-sm); overflow: hidden; background: #f4f6f7; border: 1px solid var(--color-border); display: flex; align-items: center; justify-content: center; }
.img-preview.empty { border-style: dashed; }
.img-preview img { width: 100%; height: 100%; object-fit: cover; }
.img-ph { font-size: 32px; opacity: .35; }
.img-actions { display: flex; flex-direction: column; gap: 7px; flex: 1; min-width: 0; }
.hidden-file { display: none; }
.btn-sm { padding: 6px 12px; font-size: 13px; align-self: flex-start; }
.img-hint { font-size: 11px; color: var(--color-muted); margin: 0; }
.url-input { font-size: 12px; }
/* AI 추천가 CTA — 판매자가 적극 활용하도록 크고 눈에 띄게 */
.ai-cta { width: 100%; display: flex; align-items: center; gap: 14px; padding: 14px 18px; border: 1px solid var(--color-primary-dark); border-radius: var(--radius-sm); cursor: pointer; text-align: left;
  background: var(--color-primary-dark); color: #fff; transition: background .12s; }
.ai-cta:hover:not(:disabled) { background: var(--color-primary); border-color: var(--color-primary); }
.ai-cta:disabled { opacity: .6; cursor: default; }
.ai-cta-icon { font-size: 26px; line-height: 1; }
.ai-cta-text { flex: 1; display: flex; flex-direction: column; gap: 3px; }
.ai-cta-text strong { font-size: 16px; font-weight: 800; }
.ai-cta-text small { font-size: 12px; font-weight: 500; opacity: .92; }
.ai-cta-arrow { font-size: 20px; font-weight: 900; }
.ai-btn { background: var(--color-primary-soft); color: var(--color-primary-dark); border: 1px solid #cfe8d4; border-radius: 999px; font-size: 12px; font-weight: 700; padding: 3px 10px; cursor: pointer; }
.ai-btn:hover:not(:disabled) { background: #cfe8d4; }
.ai-btn:disabled { opacity: 0.5; cursor: default; }
.ai-msg { color: var(--color-primary-dark); font-size: 13px; margin: 10px 0 0; background: var(--color-primary-soft); padding: 10px 12px; border-radius: var(--radius-sm); white-space: pre-line; line-height: 1.55; }
.form-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 14px; }
.err { color: var(--color-accent-dark); font-size: 14px; margin: 10px 0 0; }

/* AI 추천가 패널 */
.price-panel { margin: 12px 0 0; border: 1px solid #cfe8d4; border-radius: var(--radius-sm); background: var(--color-primary-soft); padding: 14px 16px; }
.pp-head { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.pp-title { font-size: 14px; font-weight: 800; color: var(--color-primary-dark); }
.pp-engine { font-size: 11px; font-weight: 800; padding: 2px 9px; border-radius: 999px; }
.pp-engine.is-ai { background: var(--color-primary-dark); color: #fff; }
.pp-engine.is-rule { background: #e6e8ea; color: #5a6066; }
.pp-price { font-size: 26px; font-weight: 900; color: var(--color-text); margin: 8px 0 2px; }
.pp-price .won { font-size: 15px; font-weight: 700; margin-left: 2px; }
.pp-price .pp-unit { font-size: 14px; font-weight: 700; color: var(--color-muted); margin-left: 8px; }
.pp-reason { font-size: 13px; color: var(--color-text); line-height: 1.55; margin: 4px 0 0; }
.pp-unitbasis { font-size: 12.5px; color: var(--color-primary-dark); line-height: 1.5; margin: 6px 0 0; background: #fff; border: 1px dashed #cfe8d4; border-radius: var(--radius-sm); padding: 7px 10px; }
.pp-block { margin-top: 12px; padding-top: 12px; border-top: 1px dashed #cfe8d4; }
.pp-block-head { display: flex; align-items: baseline; justify-content: space-between; gap: 8px; flex-wrap: wrap; }
.pp-label { font-size: 12px; font-weight: 800; color: var(--color-primary-dark); }
.pp-source { font-size: 11px; color: var(--color-muted); font-weight: 600; }
.pp-row { display: flex; flex-wrap: wrap; align-items: baseline; gap: 4px 12px; font-size: 13px; margin-top: 6px; color: var(--color-text); }
.pp-row .muted { color: var(--color-muted); font-size: 12px; }
.pp-note { font-size: 12px; color: var(--color-muted); line-height: 1.5; margin: 10px 0 0; }

/* 경쟁가 레인지 바 */
.pp-bar { margin-top: 10px; }
.pp-bar-track { position: relative; height: 8px; border-radius: 999px; background: linear-gradient(90deg, #d8e6da, #8fd0a0); }
.pp-bar-fill { position: absolute; top: 50%; width: 12px; height: 12px; border-radius: 50%; background: #fff; border: 2px solid var(--color-primary); transform: translate(-50%, -50%); }
.pp-bar-rec { position: absolute; top: -3px; width: 0; height: 14px; border-left: 3px solid var(--color-primary-dark); transform: translateX(-50%); }
.pp-bar-labels { display: flex; justify-content: space-between; font-size: 11px; color: var(--color-muted); margin-top: 6px; }
.pp-bar-labels strong { color: var(--color-text); }
.pp-bar-legend { font-size: 11px; color: var(--color-muted); margin: 4px 0 0; }
.pp-bar-legend .dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin: 0 2px; vertical-align: middle; }
.pp-bar-legend .dot.rec { background: var(--color-primary-dark); border-radius: 1px; width: 3px; height: 10px; }
.pp-bar-legend .dot.avg { background: #fff; border: 2px solid var(--color-primary); }

/* 경쟁 상품 카드(썸네일) */
.pp-cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 8px; margin-top: 12px; }
.pp-card { display: flex; flex-direction: column; background: #fff; border: 1px solid #e1e6ea; border-radius: var(--radius-sm); overflow: hidden; text-decoration: none; color: var(--color-text); transition: border-color .15s, box-shadow .15s; }
.pp-card:hover { border-color: var(--color-primary); box-shadow: 0 2px 8px rgba(0,0,0,.07); }
.pp-card-thumb { aspect-ratio: 1 / 1; background: #f4f6f7; display: flex; align-items: center; justify-content: center; }
.pp-card-thumb img { width: 100%; height: 100%; object-fit: cover; }
.pp-card-thumb .noimg { font-size: 28px; opacity: .4; }
.pp-card-body { padding: 7px 9px; display: flex; flex-direction: column; gap: 2px; }
.pp-card-mall { font-size: 10.5px; color: var(--color-muted); }
.pp-card-title { font-size: 11.5px; line-height: 1.35; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.pp-card-price { font-size: 14px; font-weight: 800; color: var(--color-text); margin-top: 2px; }
.pp-naver-link { display: inline-block; margin-top: 12px; font-size: 12.5px; font-weight: 700; color: #03c75a; text-decoration: none; }
.pp-naver-link:hover { text-decoration: underline; }

.tbl { width: 100%; border-collapse: collapse; font-size: 14px; }
.tbl th, .tbl td { padding: 11px 8px; border-bottom: 1px solid var(--color-border); text-align: left; }
.tbl th { font-size: 12px; color: var(--color-muted); font-weight: 700; }
.tbl .num { text-align: right; }
.tbl .name { font-weight: 700; }
.tbl .deal { color: #c1272d; font-weight: 700; }
.tbl .actions { text-align: right; white-space: nowrap; }
.cell-unit { font-size: 10px; color: var(--color-muted); font-weight: 500; margin-left: 1px; }
.cur-price { font-weight: 700; }

/* 추천 판매가 + 정체 행동추천 팝오버 */
.rec-cell { position: relative; }
.rec-price { display: inline-flex; align-items: center; gap: 4px; color: var(--color-primary-dark); font-weight: 800; }
.rec-price.stale { cursor: help; padding: 2px 7px; border-radius: 999px; background: #fef3e2; color: #b76e00; }
.stale-dot { color: #f59e0b; font-size: 8px; font-style: normal; animation: pulse 1.4s ease-in-out infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: .35; } }
.action-pop { position: absolute; right: 0; top: calc(100% + 6px); z-index: 20; width: 290px; text-align: left;
  background: #fff; border: 1px solid #f0d9ad; border-radius: var(--radius-sm); box-shadow: 0 8px 24px rgba(0,0,0,.14); padding: 12px 14px; }
.ap-loading { font-size: 13px; color: var(--color-muted); }
.ap-head { font-size: 13px; font-weight: 800; color: #b76e00; display: flex; align-items: center; gap: 6px; }
.ap-engine { font-size: 10px; font-weight: 800; background: var(--color-primary-dark); color: #fff; padding: 1px 6px; border-radius: 999px; }
.ap-body { font-size: 12.5px; color: var(--color-text); line-height: 1.55; margin: 7px 0 0; white-space: normal; }
.ap-rec { font-size: 13px; margin-top: 9px; padding-top: 8px; border-top: 1px dashed #f0d9ad; color: var(--color-text); }
.ap-rec strong { color: var(--color-primary-dark); font-size: 15px; }
.ap-cur { color: var(--color-muted); font-size: 11px; margin-left: 4px; }

.link-btn { background: none; border: none; color: var(--color-primary-dark); font-weight: 600; font-size: 13px; cursor: pointer; padding: 4px 6px; }
.link-btn.danger { color: var(--color-accent-dark); }
.link-btn:hover { text-decoration: underline; }

.dday { font-size: 12px; font-weight: 800; color: #fff; padding: 2px 8px; border-radius: 999px; background: #9aa0a6; }
.dday.risk-high { background: #e5484d; }
.dday.risk-medium { background: #f59e0b; }
.dday.risk-low { background: #7a8085; }
.risk-chip { font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 999px; }
.risk-chip.risk-high { background: #fdecec; color: #c1272d; }
.risk-chip.risk-medium { background: #fef3e2; color: #b76e00; }
.risk-chip.risk-low { background: #eef1f3; color: #7a8085; }

/* 클릭 가능한 상품 행 + 판매 추이 */
.tbl .row { cursor: pointer; transition: background .12s; }
.tbl .row:hover { background: var(--color-primary-soft); }
.tbl .row.open { background: var(--color-primary-soft); }
.tbl .row.open td { border-bottom-color: transparent; }
.trend-cell { white-space: nowrap; }
.mini-spark { display: inline-flex; align-items: flex-end; gap: 1.5px; height: 22px; vertical-align: middle; }
.mini-spark i { width: 3px; background: var(--color-primary); border-radius: 1px; opacity: .85; }
.trend-sum { font-size: 12px; font-weight: 700; color: var(--color-primary-dark); margin-left: 8px; }
.caret { color: var(--color-muted); margin-left: 6px; font-size: 11px; }

/* 펼침 상세 */
.detail-row td { padding: 0 8px 14px; background: var(--color-primary-soft); }
.sales-panel { background: #fff; border: 1px solid #e1e6ea; border-radius: var(--radius-sm); padding: 14px 16px; }
.sp-kpis { display: grid; grid-template-columns: repeat(6, 1fr); gap: 10px; }
.kpi { display: flex; flex-direction: column; gap: 3px; padding: 8px 10px; background: var(--color-primary-soft); border-radius: var(--radius-sm); }
.k-label { font-size: 11px; color: var(--color-muted); font-weight: 600; }
.k-val { font-size: 18px; font-weight: 900; color: var(--color-text); }
.k-val i { font-size: 12px; font-weight: 700; color: var(--color-muted); font-style: normal; margin-left: 1px; }
.k-val.sm { font-size: 14px; font-weight: 800; }
.sp-chart { margin-top: 14px; }
.spc-head { font-size: 12px; font-weight: 700; color: var(--color-muted); margin-bottom: 8px; }
.bars { display: flex; align-items: flex-end; gap: 4px; height: 96px; }
.bar-col { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: flex-end; gap: 3px; }
.bar-qty { font-size: 10px; font-weight: 700; color: var(--color-primary-dark); height: 12px; }
.bar-qty.zero { color: transparent; }
.bar { width: 70%; max-width: 22px; min-height: 2px; background: var(--color-primary); border-radius: 2px 2px 0 0; }
.bar-day { font-size: 9px; color: var(--color-muted); }
.sales-empty { background: #fff; border: 1px dashed #d8e6da; border-radius: var(--radius-sm); padding: 16px; font-size: 13px; color: var(--color-muted); text-align: center; }

@media (max-width: 640px) {
  .sp-kpis { grid-template-columns: repeat(3, 1fr); }
}
</style>
