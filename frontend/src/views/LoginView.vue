<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useWishlistStore } from '../stores/wishlist'
import { useFollowStore } from '../stores/follow'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const wishlist = useWishlistStore()
const follow = useFollowStore()

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  loading.value = true
  try {
    await auth.login({ email: email.value, password: password.value })
    if (auth.isBuyer) {
      await wishlist.load()
      await follow.load()
    }
    router.push(route.query.redirect || { name: 'products' })
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-wrap">
    <div class="auth-card card">
      <h1 class="brand">🥬 로그인</h1>
      <p class="muted sub">FreshGrowth에 오신 것을 환영합니다.</p>

      <form @submit.prevent="submit">
        <div class="field">
          <label>이메일</label>
          <input v-model="email" type="email" class="input" placeholder="you@example.com" required />
        </div>
        <div class="field">
          <label>비밀번호</label>
          <input v-model="password" type="password" class="input" placeholder="비밀번호" required />
        </div>
        <p v-if="error" class="err">{{ error }}</p>
        <button class="btn btn-primary btn-block" :disabled="loading">{{ loading ? '로그인 중…' : '로그인' }}</button>
      </form>

      <p class="foot muted">
        계정이 없으신가요?
        <router-link :to="{ name: 'signup' }" class="link">회원가입</router-link>
      </p>
    </div>
  </div>
</template>

<style scoped>
.auth-wrap { display: flex; justify-content: center; padding: 32px 0; }
.auth-card { width: 100%; max-width: 400px; padding: 32px; }
.brand { font-size: 24px; margin: 0 0 4px; text-align: center; }
.sub { text-align: center; margin: 0 0 24px; font-size: 14px; }
.err { color: var(--color-accent-dark); font-size: 14px; margin: 0 0 12px; }
.btn-block { margin-top: 4px; padding: 13px; }
.foot { text-align: center; margin: 20px 0 0; font-size: 14px; }
.link { color: var(--color-primary-dark); font-weight: 600; }
</style>
