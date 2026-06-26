import { defineStore } from 'pinia'
import { followApi } from '../api/follow'

// 내가 팔로우한 판매자 id 집합
export const useFollowStore = defineStore('follow', {
  state: () => ({ ids: [] }),
  getters: {
    isFollowing: (s) => (sellerId) => s.ids.includes(sellerId),
  },
  actions: {
    async load() {
      try {
        const sellers = await followApi.following()
        this.ids = (sellers || []).map((s) => s.sellerId)
      } catch {
        this.ids = []
      }
    },
    async toggle(sellerId) {
      if (this.ids.includes(sellerId)) {
        await followApi.unfollow(sellerId)
        this.ids = this.ids.filter((id) => id !== sellerId)
      } else {
        await followApi.follow(sellerId)
        this.ids.push(sellerId)
      }
    },
    clear() {
      this.ids = []
    },
  },
})
