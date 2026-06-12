<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { postApi } from '../api/posts'
import { useAuthStore } from '../stores/auth'
import { dateOnly, apiMessage } from '../utils/format'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const SORTS = ['latest', 'views']
const CATEGORIES = [
  { value: '', label: '전체' },
  { value: 'general', label: '자유' },
  { value: 'question', label: '질문' },
  { value: 'tip', label: '꿀팁' },
  { value: 'recipe', label: '레시피' },
  { value: 'review', label: '후기' },
]
const SIZE = 10

const posts = ref([])
const loading = ref(true)
const error = ref('')
// 초기 상태를 URL 쿼리에서 복원 → 새로고침·뒤로가기·링크 공유에도 검색조건 유지
const keyword = ref(route.query.keyword || '')
const sort = ref(SORTS.includes(route.query.sort) ? route.query.sort : 'latest')
const category = ref(route.query.category || '')
const page = ref(Math.max(0, (parseInt(route.query.page) || 1) - 1))
const totalPages = ref(0)
const totalElements = ref(0)

// AI 식료품 트렌드 카드
const trend = ref(null)
const trendLoading = ref(true)
const trendOpen = ref(false)

onMounted(() => {
  load()
  loadTrend()
})
// 현재 검색 상태를 URL 쿼리에 반영(기본값은 생략해 깔끔하게)
function syncUrl() {
  const q = {}
  if (keyword.value.trim()) q.keyword = keyword.value.trim()
  if (sort.value !== 'latest') q.sort = sort.value
  if (category.value) q.category = category.value
  if (page.value > 0) q.page = page.value + 1
  router.replace({ query: q }).catch(() => {})
}

async function load() {
  loading.value = true
  error.value = ''
  syncUrl()
  try {
    const res = await postApi.list({
      page: page.value,
      size: SIZE,
      keyword: keyword.value.trim() || undefined,
      sort: sort.value,
      category: category.value || undefined,
    })
    posts.value = res.content || []
    totalPages.value = res.totalPages || 0
    totalElements.value = res.totalElements || 0
  } catch (e) {
    error.value = apiMessage(e)
  } finally {
    loading.value = false
  }
}

// 검색은 디바운스, 정렬 변경 시 첫 페이지로 리셋 후 재조회
let searchTimer
watch(keyword, () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => { page.value = 0; load() }, 350)
})
watch(sort, () => { page.value = 0; load() })
watch(category, () => { page.value = 0; load() })

function goPage(p) {
  if (p < 0 || p >= totalPages.value || p === page.value) return
  page.value = p
  load()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const pageWindow = computed(() => {
  const tp = totalPages.value
  if (tp <= 1) return []
  let start = Math.max(0, page.value - 2)
  const end = Math.min(tp, start + 5)
  start = Math.max(0, end - 5)
  return Array.from({ length: end - start }, (_, i) => start + i)
})

async function loadTrend() {
  trendLoading.value = true
  try {
    const res = await postApi.trend()
    trend.value = res?.available ? res : null
  } catch {
    trend.value = null // 트렌드 실패는 게시판 본문에 영향 주지 않음
  } finally {
    trendLoading.value = false
  }
}

function pct(v) {
  return `${v > 0 ? '+' : ''}${v}%`
}

function catLabel(val) {
  return CATEGORIES.find(c => c.value === val)?.label || '자유'
}
const catEmoji = { general: '💬', question: '❓', tip: '💡', recipe: '🍳', review: '📝' }
</script>

<template>
  <div>
    <div class="page-head">
      <h1>📝 게시판</h1>
      <router-link v-if="auth.isLoggedIn" class="btn btn-primary" :to="{ name: 'board-write' }">✏️ 글쓰기</router-link>
    </div>

    <!-- AI 식료품 트렌드 카드 -->
    <section v-if="trendLoading" class="trend trend--skeleton">🥬 식료품 트렌드 분석 중…</section>
    <section v-else-if="trend" class="trend">
      <div class="trend-head">
        <h2>🥬 이번 달 식료품 트렌드 <span class="badge">AI</span></h2>
        <button class="toggle" @click="trendOpen = !trendOpen">{{ trendOpen ? '접기' : '자세히 보기' }}</button>
      </div>
      <div class="movers">
        <span v-for="m in trend.fallers" :key="'f' + m.itemName" class="chip down">
          {{ m.itemName }} {{ pct(m.changePct) }}
        </span>
        <span v-for="m in trend.risers" :key="'r' + m.itemName" class="chip up">
          {{ m.itemName }} {{ pct(m.changePct) }}
        </span>
      </div>
      <p class="trend-summary" :class="{ clamp: !trendOpen }">{{ trend.summary }}</p>
      <p v-if="trendOpen" class="trend-basis">{{ trend.basis }}</p>
    </section>

    <div class="cat-tabs">
      <button v-for="c in CATEGORIES" :key="c.value" class="cat-tab" :class="{ active: category === c.value }" @click="category = c.value">
        {{ c.label }}
      </button>
    </div>

    <div class="search-row">
      <input v-model="keyword" class="input search" placeholder="제목·내용으로 검색하세요" />
      <div class="sort">
        <label class="muted">정렬</label>
        <select v-model="sort" class="select">
          <option value="latest">최신순</option>
          <option value="views">조회순</option>
        </select>
      </div>
    </div>

    <p class="count muted">총 {{ totalElements }}개 글 · {{ page + 1 }}/{{ Math.max(totalPages, 1) }} 페이지</p>

    <div v-if="loading" class="empty"><span class="emoji">⏳</span>불러오는 중…</div>
    <div v-else-if="error" class="empty"><span class="emoji">⚠️</span>{{ error }}</div>
    <div v-else-if="posts.length === 0 && keyword.trim()" class="empty">
      <span class="emoji">🔍</span>'{{ keyword.trim() }}'에 대한 검색 결과가 없어요.
    </div>
    <div v-else-if="posts.length === 0" class="empty">
      <span class="emoji">📭</span>아직 게시글이 없어요.
      <br v-if="auth.isLoggedIn" /><router-link v-if="auth.isLoggedIn" class="btn btn-outline" style="margin-top:14px" :to="{ name: 'board-write' }">첫 글 쓰기</router-link>
    </div>

    <template v-else>
      <table class="tbl">
        <thead>
          <tr><th class="cat-col">분류</th><th>제목</th><th>작성자</th><th class="num">조회</th><th>작성일</th></tr>
        </thead>
        <tbody>
          <tr v-for="p in posts" :key="p.postId" @click="router.push({ name: 'board-detail', params: { id: p.postId } })">
            <td class="cat-col"><span class="cat-badge" :class="'cat-' + (p.category || 'general')">{{ catEmoji[p.category] || '💬' }} {{ catLabel(p.category) }}</span></td>
            <td class="title">{{ p.title }}</td>
            <td>{{ p.authorName }}</td>
            <td class="num">{{ p.viewCount }}</td>
            <td class="muted">{{ dateOnly(p.createdAt) }}</td>
          </tr>
        </tbody>
      </table>

      <div v-if="totalPages > 1" class="pagination">
        <button class="pg-btn" :disabled="page === 0" @click="goPage(page - 1)">‹</button>
        <button v-for="p in pageWindow" :key="p" class="pg-btn" :class="{ active: p === page }" @click="goPage(p)">{{ p + 1 }}</button>
        <button class="pg-btn" :disabled="page >= totalPages - 1" @click="goPage(page + 1)">›</button>
      </div>
    </template>
  </div>
</template>

<style scoped>
.page-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 18px; }
.page-head h1 { font-size: 22px; margin: 0; }

.cat-tabs { display: flex; gap: 6px; margin-bottom: 14px; flex-wrap: wrap; }
.cat-tab {
  padding: 7px 16px; border: 1px solid var(--color-border); border-radius: 999px;
  background: #fff; font-size: 13px; font-weight: 600; color: var(--color-muted);
  cursor: pointer; transition: all .15s ease;
}
.cat-tab:hover { border-color: var(--color-primary); color: var(--color-primary-dark); }
.cat-tab.active { background: var(--color-primary); color: #fff; border-color: var(--color-primary); }

.search-row { display: flex; align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap; margin-bottom: 14px; }
.search { max-width: 420px; flex: 1; }
.sort { display: flex; align-items: center; gap: 8px; }
.sort .select { width: auto; padding: 8px 12px; }
.count { margin: 12px 0 16px; font-size: 14px; }

.pagination { display: flex; justify-content: center; gap: 6px; margin: 28px 0 8px; }
.pg-btn {
  min-width: 36px; height: 36px; padding: 0 10px;
  border: 1px solid var(--color-border); background: #fff; border-radius: var(--radius-sm);
  font-size: 14px; font-weight: 600; color: var(--color-text); cursor: pointer;
}
.pg-btn:hover:not(:disabled) { border-color: var(--color-primary); }
.pg-btn.active { background: var(--color-primary); color: #fff; border-color: var(--color-primary); }
.pg-btn:disabled { opacity: 0.4; cursor: default; }

.tbl { width: 100%; border-collapse: collapse; font-size: 14px; }
.tbl th, .tbl td { padding: 12px 10px; border-bottom: 1px solid var(--color-border); text-align: left; }
.tbl th { font-size: 12px; color: var(--color-muted); font-weight: 700; }
.tbl .num { text-align: right; }
.tbl tbody tr { cursor: pointer; }
.tbl tbody tr:hover { background: var(--color-bg); }
.tbl .title { font-weight: 700; }
.cat-col { width: 80px; white-space: nowrap; }
.cat-badge { font-size: 12px; font-weight: 700; padding: 3px 8px; border-radius: 999px; }
.cat-general { background: #f0f0f0; color: #555; }
.cat-question { background: #e8f4fd; color: #1976d2; }
.cat-tip { background: #fff8e1; color: #f57f17; }
.cat-recipe { background: #fce4ec; color: #c62828; }
.cat-review { background: #e8f5e9; color: #2e7d32; }

/* AI 식료품 트렌드 카드 */
.trend {
  border: 1px solid var(--color-border);
  border-radius: 12px;
  background: var(--color-card);
  padding: 16px 18px;
  margin-bottom: 20px;
}
.trend--skeleton { color: var(--color-muted); font-size: 14px; }
.trend-head { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.trend-head h2 { font-size: 16px; margin: 0; display: flex; align-items: center; gap: 8px; }
.badge {
  font-size: 11px; font-weight: 700; color: #fff; background: var(--color-primary, #2e7d32);
  padding: 2px 7px; border-radius: 999px; letter-spacing: .3px;
}
.toggle {
  border: none; background: none; color: var(--color-muted); font-size: 13px;
  cursor: pointer; padding: 4px; white-space: nowrap;
}
.toggle:hover { color: var(--color-text, #222); }
.movers { display: flex; flex-wrap: wrap; gap: 6px; margin: 12px 0 10px; }
.chip { font-size: 12px; font-weight: 700; padding: 4px 9px; border-radius: 999px; }
.chip.down { background: #e7f3ea; color: #1b7f3b; }
.chip.up { background: #fdeaea; color: #c0392b; }
.trend-summary { font-size: 14px; line-height: 1.65; color: var(--color-text, #333); margin: 0; }
.trend-summary.clamp {
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
.trend-basis { font-size: 12px; color: var(--color-muted); margin: 10px 0 0; }
</style>
