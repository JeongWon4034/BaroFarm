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

onMounted(load)
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
</script>

<template>
  <div>
    <div class="page-head">
      <h1>📝 게시판</h1>
      <router-link v-if="auth.isLoggedIn" class="btn btn-primary" :to="{ name: 'board-write' }">✏️ 글쓰기</router-link>
    </div>

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
</style>
