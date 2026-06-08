<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { productApi } from '../api/products'
import { won, categoryLabel, dDayLabel, dateOnly, riskMeta } from '../utils/format'

const products = ref([])
const loading = ref(true)
const error = ref('')

const CATEGORIES = ['vegetable', 'fruit', 'seafood', 'meat', 'grain', 'mushroom', 'root']

const showForm = ref(false)
const editingId = ref(null)
const saving = ref(false)
const formError = ref('')
const blank = () => ({ name: '', category: 'vegetable', price: null, stockQty: null, expirationDate: '', description: '', thumbnailUrl: '' })
const form = reactive(blank())

const formTitle = computed(() => (editingId.value ? '상품 수정' : '상품 등록'))

onMounted(load)
async function load() {
  loading.value = true
  error.value = ''
  try {
    products.value = (await productApi.sellerProducts()) || []
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingId.value = null
  Object.assign(form, blank())
  formError.value = ''
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
  showForm.value = true
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
        <p class="muted">내 상품을 등록·수정·삭제하고 폐기위험/떨이가를 확인하세요.</p>
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
        <label class="fld"><span>가격(원) *</span><input v-model.number="form.price" type="number" min="0" class="input" placeholder="3900" /></label>
        <label class="fld"><span>재고(개) *</span><input v-model.number="form.stockQty" type="number" min="0" class="input" placeholder="50" /></label>
        <label class="fld span2"><span>설명</span><input v-model="form.description" class="input" placeholder="상품 설명" /></label>
        <label class="fld span2"><span>썸네일 URL (선택)</span><input v-model="form.thumbnailUrl" class="input" placeholder="비우면 이모지로 표시" /></label>
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
        <tr><th>상품</th><th>카테고리</th><th>유통기한</th><th>위험</th><th class="num">정가</th><th class="num">재고</th><th class="num">떨이가</th><th></th></tr>
      </thead>
      <tbody>
        <tr v-for="p in products" :key="p.productId">
          <td class="name">{{ p.name }}</td>
          <td>{{ categoryLabel(p.category) }}</td>
          <td><span class="dday" :class="riskMeta(p.riskLevel).cls">{{ dDayLabel(p.daysToExpiry) }}</span></td>
          <td><span class="risk-chip" :class="riskMeta(p.riskLevel).cls">{{ riskMeta(p.riskLevel).label }}</span></td>
          <td class="num">{{ won(p.price) }}</td>
          <td class="num">{{ p.stockQty }}</td>
          <td class="num deal">{{ won(p.discountedPrice) }}</td>
          <td class="actions">
            <button class="link-btn" @click="openEdit(p)">수정</button>
            <button class="link-btn danger" @click="remove(p)">삭제</button>
          </td>
        </tr>
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
.form-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 14px; }
.err { color: var(--color-accent-dark); font-size: 14px; margin: 10px 0 0; }

.tbl { width: 100%; border-collapse: collapse; font-size: 14px; }
.tbl th, .tbl td { padding: 11px 8px; border-bottom: 1px solid var(--color-border); text-align: left; }
.tbl th { font-size: 12px; color: var(--color-muted); font-weight: 700; }
.tbl .num { text-align: right; }
.tbl .name { font-weight: 700; }
.tbl .deal { color: #c1272d; font-weight: 700; }
.tbl .actions { text-align: right; white-space: nowrap; }

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
</style>
