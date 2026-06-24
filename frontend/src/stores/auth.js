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
    isAdmin: (s) => s.user?.role === 'ADMIN',
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
    // 서버 호출 없이 로컬 세션만 정리(만료/무효 토큰 정리용). 헤더가 로그인/회원가입으로 복귀.
    clearSession() {
      this.user = null
      this.token = null
      localStorage.removeItem('user')
      localStorage.removeItem('token')
      localStorage.removeItem('userId') // 레거시 정리
    },
    // 앱 시작 시 토큰 유효성 검증. 유효하면 최신 user로 갱신, 무효(401 등)면 세션 정리.
    async validate() {
      if (!this.token) {
        this.clearSession()
        return false
      }
      try {
        const user = await authApi.me() // 401이면 http 인터셉터가 reject
        this.persist(user) // 토큰 유지, 최신 정보 반영
        return true
      } catch {
        this.clearSession()
        return false
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
      this.clearSession()
    },
    async deactivate(password) {
      await authApi.deactivate({ password }) // 서버에서 비밀번호 검증 + 토큰 무효화
      this.clearSession()
    },
  },
})
