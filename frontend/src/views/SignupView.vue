<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()

const form = ref({ name: '', email: '', password: '', passwordConfirm: '', role: 'BUYER' })
const error = ref('')
const loading = ref(false)
const touched = ref({ name: false, email: false, password: false, passwordConfirm: false })

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

// 비밀번호 강도 (0~3)
const pwStrength = computed(() => {
  const pw = form.value.password
  if (!pw) return { level: 0, label: '', cls: '' }
  let score = 0
  if (pw.length >= 8) score++
  if (/[A-Z]/.test(pw) && /[a-z]/.test(pw)) score++
  if (/\d/.test(pw) && /[^A-Za-z0-9]/.test(pw)) score++
  const map = [
    { label: '약함', cls: 'weak' },
    { label: '보통', cls: 'fair' },
    { label: '강함', cls: 'strong' },
  ]
  return { level: score, ...map[Math.min(score, 2)] }
})

// 필드별 인라인 오류
const fieldError = computed(() => ({
  name: touched.value.name && !form.value.name.trim() ? '이름을 입력하세요.' : '',
  email: touched.value.email && !EMAIL_RE.test(form.value.email) ? '올바른 이메일 형식이 아닙니다.' : '',
  password: touched.value.password && form.value.password.length > 0 && form.value.password.length < 8 ? '비밀번호는 8자 이상이어야 합니다.' : '',
  passwordConfirm: touched.value.passwordConfirm && form.value.passwordConfirm && form.value.password !== form.value.passwordConfirm ? '비밀번호가 일치하지 않습니다.' : '',
}))

function validate() {
  if (!form.value.name.trim()) return '이름을 입력하세요.'
  if (!EMAIL_RE.test(form.value.email)) return '올바른 이메일 형식이 아닙니다.'
  if (form.value.password.length < 8) return '비밀번호는 8자 이상이어야 합니다.'
  if (form.value.password !== form.value.passwordConfirm) return '비밀번호가 일치하지 않습니다.'
  return ''
}

async function submit() {
  error.value = ''
  touched.value = { name: true, email: true, password: true, passwordConfirm: true }
  const v = validate()
  if (v) { error.value = v; return }
  loading.value = true
  try {
    await auth.signup({ name: form.value.name, email: form.value.email, password: form.value.password, role: form.value.role })
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
          <input v-model="form.name" class="input" :class="{ 'input-err': fieldError.name }" placeholder="홍길동" required @blur="touched.name = true" />
          <p v-if="fieldError.name" class="field-err">{{ fieldError.name }}</p>
        </div>
        <div class="field">
          <label>이메일</label>
          <input v-model="form.email" type="email" class="input" :class="{ 'input-err': fieldError.email }" placeholder="you@example.com" required @blur="touched.email = true" />
          <p v-if="fieldError.email" class="field-err">{{ fieldError.email }}</p>
        </div>
        <div class="field">
          <label>비밀번호 <span class="hint muted">(8자 이상)</span></label>
          <input v-model="form.password" type="password" class="input" :class="{ 'input-err': fieldError.password }" placeholder="영문 대소문자, 숫자, 특수문자 조합" required @blur="touched.password = true" />
          <p v-if="fieldError.password" class="field-err">{{ fieldError.password }}</p>
          <div v-if="form.password" class="pw-strength">
            <div class="pw-bar"><div class="pw-fill" :class="pwStrength.cls" :style="{ width: ((pwStrength.level + 1) / 3 * 100) + '%' }" /></div>
            <span class="pw-label" :class="pwStrength.cls">{{ pwStrength.label }}</span>
          </div>
        </div>
        <div class="field">
          <label>비밀번호 확인</label>
          <input v-model="form.passwordConfirm" type="password" class="input" :class="{ 'input-err': fieldError.passwordConfirm }" placeholder="비밀번호를 한 번 더 입력하세요" required @blur="touched.passwordConfirm = true" />
          <p v-if="fieldError.passwordConfirm" class="field-err">{{ fieldError.passwordConfirm }}</p>
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
.field-err { color: var(--color-accent-dark); font-size: 12px; margin: 4px 0 0; }
.input-err { border-color: var(--color-accent-dark); }
.pw-strength { display: flex; align-items: center; gap: 8px; margin-top: 6px; }
.pw-bar { flex: 1; height: 5px; background: var(--color-border); border-radius: 999px; overflow: hidden; }
.pw-fill { height: 100%; border-radius: 999px; transition: width .25s ease; }
.pw-fill.weak { background: #e5484d; }
.pw-fill.fair { background: #f59e0b; }
.pw-fill.strong { background: #22a06b; }
.pw-label { font-size: 12px; font-weight: 700; white-space: nowrap; }
.pw-label.weak { color: #e5484d; }
.pw-label.fair { color: #f59e0b; }
.pw-label.strong { color: #22a06b; }
.btn-block { margin-top: 4px; padding: 13px; }
.foot { text-align: center; margin: 20px 0 0; font-size: 14px; }
.link { color: var(--color-primary-dark); font-weight: 600; }
</style>
