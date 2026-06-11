<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { postApi } from '../api/posts'

const route = useRoute()
const router = useRouter()

const editId = computed(() => route.params.id || null)
const form = reactive({ category: 'general', title: '', content: '' })
const saving = ref(false)
const error = ref('')
const CATEGORIES = [
  { value: 'general', label: '💬 자유' },
  { value: 'question', label: '❓ 질문' },
  { value: 'tip', label: '💡 꿀팁' },
  { value: 'recipe', label: '🍳 레시피' },
  { value: 'review', label: '📝 후기' },
]

onMounted(async () => {
  if (editId.value) {
    try {
      const p = await postApi.detail(editId.value)
      form.category = p.category || 'general'
      form.title = p.title
      form.content = p.content
    } catch (e) {
      error.value = e.message
    }
  }
})

async function submit() {
  error.value = ''
  if (!form.title.trim()) { error.value = '제목을 입력하세요.'; return }
  if (!form.content.trim()) { error.value = '내용을 입력하세요.'; return }
  saving.value = true
  try {
    const payload = { category: form.category, title: form.title.trim(), content: form.content.trim() }
    const res = editId.value
      ? await postApi.update(editId.value, payload)
      : await postApi.create(payload)
    router.push({ name: 'board-detail', params: { id: editId.value || res.postId } })
  } catch (e) {
    error.value = e.message
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="wrap">
    <h1 class="title">{{ editId ? '글 수정' : '글쓰기' }}</h1>
    <div class="card form">
      <div class="fld">
        <span>분류</span>
        <div class="cat-pick">
          <button v-for="c in CATEGORIES" :key="c.value" type="button" class="cat-opt" :class="{ on: form.category === c.value }" @click="form.category = c.value">
            {{ c.label }}
          </button>
        </div>
      </div>
      <label class="fld"><span>제목</span><input v-model="form.title" class="input" placeholder="제목을 입력하세요" /></label>
      <label class="fld"><span>내용</span><textarea v-model="form.content" class="input area" rows="12" placeholder="내용을 입력하세요" /></label>
      <p v-if="error" class="err">{{ error }}</p>
      <div class="actions">
        <router-link :to="{ name: 'board' }" class="btn btn-outline">취소</router-link>
        <button class="btn btn-primary" :disabled="saving" @click="submit">{{ saving ? '저장 중…' : (editId ? '수정' : '등록') }}</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.wrap { max-width: 720px; margin: 0 auto; }
.title { font-size: 22px; margin-bottom: 18px; }
.form { padding: 22px; display: flex; flex-direction: column; gap: 16px; }
.fld { display: flex; flex-direction: column; gap: 6px; font-size: 13px; font-weight: 600; color: var(--color-muted); }
.fld .input { font-weight: 500; color: var(--color-text); }
.area { resize: vertical; line-height: 1.6; font-family: inherit; }
.cat-pick { display: flex; gap: 8px; flex-wrap: wrap; }
.cat-opt {
  padding: 8px 14px; border: 1px solid var(--color-border); border-radius: 999px;
  background: #fff; font-size: 13px; font-weight: 600; color: var(--color-muted); cursor: pointer;
}
.cat-opt.on { border-color: var(--color-primary); background: var(--color-primary-soft); color: var(--color-primary-dark); }
.err { color: var(--color-accent-dark); font-size: 14px; margin: 0; }
.actions { display: flex; justify-content: flex-end; gap: 10px; }
</style>
