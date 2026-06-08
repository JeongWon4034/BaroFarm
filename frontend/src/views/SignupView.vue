<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()

const form = ref({ name: '', email: '', password: '', role: 'BUYER' })
const error = ref('')
const loading = ref(false)

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

function validate() {
  if (!form.value.name.trim()) return '이름을 입력하세요.'
  if (!EMAIL_RE.test(form.value.email)) return '올바른 이메일 형식이 아닙니다.'
  if (form.value.password.length < 8) return '비밀번호는 8자 이상이어야 합니다.'
  return ''
}

async function submit() {
  error.value = ''
  const v = validate()
  if (v) { error.value = v; return }
  loading.value = true
  try {
    await auth.signup({ ...form.value })
    // 가입 후 자동 로그인
    await auth.login({ email: form.value.email, password: form.value.password })
    router.push({ name: 'products' })
  } catch (e) {
    // 중복 이메일 등 구체 메시지 노출 (인터셉터가 error.detail/code 전달)
    error.value = e.code === 'DUPLICATED_EMAIL' ? '이미 사용 중인 이메일입니다.' : e.message
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-wrap">
    <div class="auth-card card">
      <h1 class="brand">🥬 회원가입</h1>
      <p class="muted sub">신선한 산지 직거래, FreshGrowth와 함께해요.</p>

      <form @submit.prevent="submit">
        <div class="field">
          <label>이름</label>
          <input v-model="form.name" class="input" placeholder="홍길동" required />
        </div>
        <div class="field">
          <label>이메일</label>
          <input v-model="form.email" type="email" class="input" placeholder="you@example.com" required />
        </div>
        <div class="field">
          <label>비밀번호 <span class="hint muted">(8자 이상)</span></label>
          <input v-model="form.password" type="password" class="input" placeholder="8자 이상" required />
        </div>
        <div class="field">
          <label>가입 유형</label>
          <div class="role-pick">
            <button type="button" class="role" :class="{ on: form.role === 'BUYER' }" @click="form.role = 'BUYER'">🛒 구매자</button>
            <button type="button" class="role" :class="{ on: form.role === 'SELLER' }" @click="form.role = 'SELLER'">🏡 판매자</button>
          </div>
        </div>
        <p v-if="error" class="err">{{ error }}</p>
        <button class="btn btn-primary btn-block" :disabled="loading">{{ loading ? '가입 중…' : '회원가입' }}</button>
      </form>

      <p class="foot muted">
        이미 계정이 있으신가요?
        <router-link :to="{ name: 'login' }" class="link">로그인</router-link>
      </p>
    </div>
  </div>
</template>

<style scoped>
.auth-wrap { display: flex; justify-content: center; padding: 32px 0; }
.auth-card { width: 100%; max-width: 400px; padding: 32px; }
.brand { font-size: 24px; margin: 0 0 4px; text-align: center; }
.sub { text-align: center; margin: 0 0 24px; font-size: 14px; }
.role-pick { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.role { padding: 12px; border: 1px solid var(--color-border); border-radius: var(--radius-sm); background: #fff; font-weight: 600; color: var(--color-muted); }
.role.on { border-color: var(--color-primary); background: var(--color-primary-soft); color: var(--color-primary-dark); }
.err { color: var(--color-accent-dark); font-size: 14px; margin: 0 0 12px; }
.btn-block { margin-top: 4px; padding: 13px; }
.foot { text-align: center; margin: 20px 0 0; font-size: 14px; }
.link { color: var(--color-primary-dark); font-weight: 600; }
</style>
