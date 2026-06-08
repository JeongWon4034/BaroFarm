import { defineStore } from 'pinia'
import { authApi } from '../api/auth'

// JWT 기반 로그인 상태. 토큰은 localStorage('token')에 저장돼 Authorization 헤더로 사용됨.
export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    token: localStorage.getItem('token') || null,
  }),
  getters: {
    isLoggedIn: (s) => !!s.user && !!s.token,
    isSeller: (s) => s.user?.role === 'SELLER',
    isBuyer: (s) => s.user?.role === 'BUYER',
  },
  actions: {
    persist(user, token) {
      this.user = user
      localStorage.setItem('user', JSON.stringify(user))
      if (token) {
        this.token = token
        localStorage.setItem('token', token)
      }
    },
    async login(payload) {
      const { token, user } = await authApi.login(payload) // LoginResponse
      this.persist(user, token)
      return user
    },
    async signup(payload) {
      return authApi.signup(payload)
    },
    async updateProfile(payload) {
      const user = await authApi.updateProfile(payload)
      this.persist(user) // 토큰 유지
      return user
    },
    async logout() {
      try {
        await authApi.logout() // 서버에서 토큰 블랙리스트 등록(헤더 아직 유효)
      } catch {
        /* 네트워크 실패해도 로컬은 정리 */
      }
      this.user = null
      this.token = null
      localStorage.removeItem('user')
      localStorage.removeItem('token')
      localStorage.removeItem('userId') // 레거시 정리
    },
  },
})
