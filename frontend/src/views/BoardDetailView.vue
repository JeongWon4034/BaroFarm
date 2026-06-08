<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { postApi } from '../api/posts'
import { useAuthStore } from '../stores/auth'
import { dateOnly } from '../utils/format'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const post = ref(null)
const loading = ref(true)
const error = ref('')

onMounted(load)
async function load() {
  loading.value = true
  error.value = ''
  try {
    post.value = await postApi.detail(route.params.id)
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
</script>

<template>
  <div>
    <router-link :to="{ name: 'board' }" class="back muted">← 목록</router-link>

    <div v-if="loading" class="empty"><span class="emoji">⏳</span>불러오는 중…</div>
    <div v-else-if="error" class="empty"><span class="emoji">⚠️</span>{{ error }}</div>

    <article v-else-if="post" class="card post">
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

      <!-- 댓글 섹션 자리 (다음 작업) -->
    </article>
  </div>
</template>

<style scoped>
.back { display: inline-block; margin-bottom: 16px; font-size: 14px; }
.post { padding: 24px; }
.title { font-size: 24px; margin: 0 0 10px; }
.meta { display: flex; align-items: center; justify-content: space-between; font-size: 14px; }
.owner { display: flex; gap: 6px; }
.link-btn { background: none; border: none; color: var(--color-primary-dark); font-weight: 600; font-size: 13px; cursor: pointer; padding: 4px 6px; }
.link-btn.danger { color: var(--color-accent-dark); }
.link-btn:hover { text-decoration: underline; }
.divider { border: none; border-top: 1px solid var(--color-border); margin: 16px 0; }
.content { line-height: 1.7; color: #34404a; white-space: pre-wrap; min-height: 120px; }
</style>
