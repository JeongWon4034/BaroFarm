import { defineStore } from 'pinia'
import { wishlistApi } from '../api/wishlist'

// 찜한 상품 id 집합을 들고 다니며 카드 하트 상태/토글을 처리
export const useWishlistStore = defineStore('wishlist', {
  state: () => ({ ids: [] }),
  getters: {
    isWished: (s) => (productId) => s.ids.includes(productId),
    count: (s) => s.ids.length,
  },
  actions: {
    async load() {
      try {
        const products = await wishlistApi.list()
        this.ids = (products || []).map((p) => p.productId)
      } catch {
        this.ids = []
      }
    },
    async toggle(productId) {
      if (this.ids.includes(productId)) {
        await wishlistApi.remove(productId)
        this.ids = this.ids.filter((id) => id !== productId)
      } else {
        await wishlistApi.add(productId)
        this.ids.push(productId)
      }
    },
    clear() {
      this.ids = []
    },
  },
})
