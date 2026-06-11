<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { postApi, commentApi } from '../api/posts'
import { useAuthStore } from '../stores/auth'
import { dateOnly } from '../utils/format'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const catMap = { general: '💬 자유', question: '❓ 질문', tip: '💡 꿀팁', recipe: '🍳 레시피', review: '📝 후기' }

const post = ref(null)
const loading = ref(true)
const error = ref('')

onMounted(load)
async function load() {
  loading.value = true
  error.value = ''
  try {
    post.value = await postApi.detail(route.params.id)
    await loadComments()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

const isAuthor = computed(() => post.value && auth.user && auth.user.userId === post.value.authorId)

async function remove() {
  if (!confirm('이 글을 삭제할까요?')) return
  try {
    await postApi.remove(route.params.id)
    router.push({ name: 'board' })
  } catch (e) {
    alert(e.message)
  }
}

// --- 댓글 ---
const comments = ref([])
const newComment = ref('')
const commentMsg = ref('')
const editingId = ref(null)
const editContent = ref('')

async function loadComments() {
  try {
    comments.value = await commentApi.list(route.params.id)
  } catch {
    comments.value = []
  }
}
function isMyComment(c) {
  return auth.user && auth.user.userId === c.authorId
}
async function addComment() {
  if (!newComment.value.trim()) return
  commentMsg.value = ''
  try {
    await commentApi.create(route.params.id, newComment.value.trim())
    newComment.value = ''
    await loadComments()
  } catch (e) {
    commentMsg.value = e.message
  }
}
function startEdit(c) {
  editingId.value = c.commentId
  editContent.value = c.content
}
async function saveEdit(c) {
  if (!editContent.value.trim()) return
  try {
    await commentApi.update(c.commentId, editContent.value.trim())
    editingId.value = null
    await loadComments()
  } catch (e) {
    alert(e.message)
  }
}
async function removeComment(c) {
  if (!confirm('댓글을 삭제할까요?')) return
  try {
    await commentApi.remove(c.commentId)
    await loadComments()
  } catch (e) {
    alert(e.message)
  }
}
</script>

<template>
  <div>
    <router-link :to="{ name: 'board' }" class="back muted">← 목록</router-link>

    <div v-if="loading" class="empty"><span class="emoji">⏳</span>불러오는 중…</div>
    <div v-else-if="error" class="empty"><span class="emoji">⚠️</span>{{ error }}</div>

    <article v-else-if="post" class="card post">
      <span class="cat-badge" :class="'cat-' + (post.category || 'general')">{{ catMap[post.category] || '💬 자유' }}</span>
      <h1 class="title">{{ post.title }}</h1>
      <div class="meta">
        <span class="muted">{{ post.authorName }} · {{ dateOnly(post.createdAt) }} · 👁 {{ post.viewCount }}</span>
        <span v-if="isAuthor" class="owner">
          <router-link :to="{ name: 'board-edit', params: { id: post.postId } }" class="link-btn">수정</router-link>
          <button class="link-btn danger" @click="remove">삭제</button>
        </span>
      </div>
      <hr class="divider" />
      <div class="content">{{ post.content }}</div>
    </article>

    <!-- 댓글 -->
    <section v-if="post" class="comments card">
      <h2 class="c-title">💬 댓글 {{ comments.length }}</h2>

      <ul v-if="comments.length" class="c-list">
        <li v-for="c in comments" :key="c.commentId" class="c-item">
          <div class="c-head">
            <strong>{{ c.authorName }}</strong>
            <span class="muted sm">{{ dateOnly(c.createdAt) }}</span>
            <span v-if="isMyComment(c) && editingId !== c.commentId" class="c-actions">
              <button class="link-btn" @click="startEdit(c)">수정</button>
              <button class="link-btn danger" @click="removeComment(c)">삭제</button>
            </span>
          </div>
          <div v-if="editingId === c.commentId" class="c-edit">
            <textarea v-model="editContent" class="input" rows="2"></textarea>
            <div class="c-edit-actions">
              <button class="link-btn" @click="editingId = null">취소</button>
              <button class="link-btn" @click="saveEdit(c)">저장</button>
            </div>
          </div>
          <p v-else class="c-body">{{ c.content }}</p>
        </li>
      </ul>
      <p v-else class="muted c-empty">첫 댓글을 남겨보세요.</p>

      <div v-if="auth.isLoggedIn" class="c-form">
        <textarea v-model="newComment" class="input" rows="2" placeholder="댓글을 입력하세요"></textarea>
        <p v-if="commentMsg" class="err">{{ commentMsg }}</p>
        <div class="c-form-actions"><button class="btn btn-primary sm-btn" @click="addComment">댓글 등록</button></div>
      </div>
      <p v-else class="muted c-login">
        <router-link :to="{ name: 'login' }" class="link">로그인</router-link> 후 댓글을 작성할 수 있어요.
      </p>
    </section>
  </div>
</template>

<style scoped>
.back { display: inline-block; margin-bottom: 16px; font-size: 14px; }
.post { padding: 24px; }
.cat-badge { display: inline-block; font-size: 12px; font-weight: 700; padding: 4px 10px; border-radius: 999px; margin-bottom: 8px; }
.cat-general { background: #f0f0f0; color: #555; }
.cat-question { background: #e8f4fd; color: #1976d2; }
.cat-tip { background: #fff8e1; color: #f57f17; }
.cat-recipe { background: #fce4ec; color: #c62828; }
.cat-review { background: #e8f5e9; color: #2e7d32; }
.title { font-size: 24px; margin: 0 0 10px; }
.meta { display: flex; align-items: center; justify-content: space-between; font-size: 14px; }
.owner { display: flex; gap: 6px; }
.link-btn { background: none; border: none; color: var(--color-primary-dark); font-weight: 600; font-size: 13px; cursor: pointer; padding: 4px 6px; }
.link-btn.danger { color: var(--color-accent-dark); }
.link-btn:hover { text-decoration: underline; }
.divider { border: none; border-top: 1px solid var(--color-border); margin: 16px 0; }
.content { line-height: 1.7; color: #34404a; white-space: pre-wrap; min-height: 120px; }

.comments { padding: 20px; margin-top: 16px; }
.c-title { font-size: 16px; margin: 0 0 16px; }
.c-list { display: flex; flex-direction: column; gap: 14px; margin-bottom: 18px; }
.c-item { border-bottom: 1px solid var(--color-border); padding-bottom: 12px; }
.c-head { display: flex; align-items: center; gap: 8px; margin-bottom: 5px; }
.c-head .sm { font-size: 12px; }
.c-actions { margin-left: auto; display: flex; gap: 4px; }
.c-body { margin: 0; line-height: 1.6; white-space: pre-wrap; }
.c-edit { display: flex; flex-direction: column; gap: 6px; }
.c-edit-actions { display: flex; gap: 6px; justify-content: flex-end; }
.c-empty { padding: 8px 0 18px; }
.c-form { display: flex; flex-direction: column; gap: 8px; }
.c-form-actions { display: flex; justify-content: flex-end; }
.sm-btn { padding: 8px 16px; font-size: 14px; }
.c-login { padding: 8px 0; }
.link { color: var(--color-primary-dark); font-weight: 600; }
</style>
