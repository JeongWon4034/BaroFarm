<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { postApi } from '../api/posts'

const route = useRoute()
const router = useRouter()

const editId = computed(() => route.params.id || null)
const form = reactive({ title: '', content: '' })
const saving = ref(false)
const error = ref('')

onMounted(async () => {
  if (editId.value) {
    try {
      const p = await postApi.detail(editId.value)
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
    const payload = { title: form.title.trim(), content: form.content.trim() }
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
.err { color: var(--color-accent-dark); font-size: 14px; margin: 0; }
.actions { display: flex; justify-content: flex-end; gap: 10px; }
</style>
