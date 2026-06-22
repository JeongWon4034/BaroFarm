import { defineStore } from 'pinia'
import { orderApi } from '../api/orders'
import { useAuthStore } from './auth'

// 새 주문 알림 — 별도 알림 테이블 없이 "마지막으로 본 주문 이후 생긴 주문 수"를 배지로 표시.
// 마지막으로 본 주문 id를 localStorage에 역할·사용자별로 저장한다.
const seenKey = (role, userId) => `lastSeenOrderId:${role}:${userId}`
const orderId = (o) => Number(o.orderId ?? o.id) || 0
const maxOrderId = (list) => (list || []).reduce((m, o) => Math.max(m, orderId(o)), 0)

export const useNotificationStore = defineStore('notification', {
  state: () => ({
    count: 0, // 새 주문 수 (현재 로그인 역할 기준)
    maxId: 0, // 마지막 조회 시점의 최대 주문 id
  }),
  actions: {
    // 주문 목록을 받아와 마지막 본 시점과 비교 → 새 주문 수 계산.
    async refresh() {
      const auth = useAuthStore()
      if (!auth.isLoggedIn) {
        this.count = 0
        return
      }
      const role = auth.isSeller ? 'seller' : 'buyer'
      const key = seenKey(role, auth.user.userId)
      try {
        const list = auth.isSeller ? await orderApi.sellerOrders() : await orderApi.myOrders()
        this.maxId = maxOrderId(list)
        const raw = localStorage.getItem(key)
        if (raw === null) {
          // 첫 방문 — 기존 주문을 전부 '새 것'으로 잡지 않도록 현재 최대 id를 본 것으로 초기화
          localStorage.setItem(key, String(this.maxId))
          this.count = 0
          return
        }
        const lastSeen = Number(raw) || 0
        this.count = (list || []).filter((o) => orderId(o) > lastSeen).length
      } catch {
        this.count = 0
      }
    },
    // 주문 목록 화면을 봤을 때 호출 — 최신 주문까지 '본 것'으로 표시하고 배지 제거.
    markSeen(list) {
      const auth = useAuthStore()
      if (!auth.isLoggedIn) return
      const role = auth.isSeller ? 'seller' : 'buyer'
      const max = list ? maxOrderId(list) : this.maxId
      localStorage.setItem(seenKey(role, auth.user.userId), String(max))
      this.maxId = max
      this.count = 0
    },
    clear() {
      this.count = 0
      this.maxId = 0
    },
  },
})
