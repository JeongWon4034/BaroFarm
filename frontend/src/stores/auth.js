import { defineStore } from 'pinia'
import { authApi } from '../api/auth'

// 로그인 사용자 상태. userId는 localStorage에 저장돼 X-USER-ID 헤더로 사용됨.
export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user') || 'null'),
  }),
  getters: {
    isLoggedIn: (s) => !!s.user,
    isSeller: (s) => s.user?.role === 'SELLER',
    isBuyer: (s) => s.user?.role === 'BUYER',
  },
  actions: {
    persist(user) {
      this.user = user
      localStorage.setItem('user', JSON.stringify(user))
      localStorage.setItem('userId', user.userId)
    },
    async login(payload) {
      const user = await authApi.login(payload)
      this.persist(user)
      return user
    },
    async signup(payload) {
      return authApi.signup(payload)
    },
    async updateProfile(payload) {
      const user = await authApi.updateProfile(payload)
      this.persist(user)
      return user
    },
    logout() {
      this.user = null
      localStorage.removeItem('user')
      localStorage.removeItem('userId')
    },
  },
})
