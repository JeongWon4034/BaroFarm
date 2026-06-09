<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { postApi } from '../api/posts'
import { useAuthStore } from '../stores/auth'
import { dateOnly } from '../utils/format'

const router = useRouter()
const auth = useAuthStore()
const posts = ref([])
const loading = ref(true)
const error = ref('')

// AI 식료품 트렌드 카드
const trend = ref(null)
const trendLoading = ref(true)
const trendOpen = ref(false)

onMounted(() => {
  load()
  loadTrend()
})
async function load() {
  loading.value = true
  error.value = ''
  try {
    const res = await postApi.list(0, 50)
    posts.value = res.content || []
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

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

    <div v-if="loading" class="empty"><span class="emoji">⏳</span>불러오는 중…</div>
    <div v-else-if="error" class="empty"><span class="emoji">⚠️</span>{{ error }}</div>
    <div v-else-if="posts.length === 0" class="empty">
      <span class="emoji">📭</span>아직 게시글이 없어요.
      <br v-if="auth.isLoggedIn" /><router-link v-if="auth.isLoggedIn" class="btn btn-outline" style="margin-top:14px" :to="{ name: 'board-write' }">첫 글 쓰기</router-link>
    </div>

    <table v-else class="tbl">
      <thead>
        <tr><th>제목</th><th>작성자</th><th class="num">조회</th><th>작성일</th></tr>
      </thead>
      <tbody>
        <tr v-for="p in posts" :key="p.postId" @click="router.push({ name: 'board-detail', params: { id: p.postId } })">
          <td class="title">{{ p.title }}</td>
          <td>{{ p.authorName }}</td>
          <td class="num">{{ p.viewCount }}</td>
          <td class="muted">{{ dateOnly(p.createdAt) }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.page-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 18px; }
.page-head h1 { font-size: 22px; margin: 0; }
.tbl { width: 100%; border-collapse: collapse; font-size: 14px; }
.tbl th, .tbl td { padding: 12px 10px; border-bottom: 1px solid var(--color-border); text-align: left; }
.tbl th { font-size: 12px; color: var(--color-muted); font-weight: 700; }
.tbl .num { text-align: right; }
.tbl tbody tr { cursor: pointer; }
.tbl tbody tr:hover { background: var(--color-bg); }
.tbl .title { font-weight: 700; }

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
