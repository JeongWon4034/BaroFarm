import { defineStore } from 'pinia'

// 장바구니: 프론트에서만 관리. 결제 시 항목별로 주문(POST /orders) 생성.
export const useCartStore = defineStore('cart', {
  state: () => ({
    items: JSON.parse(localStorage.getItem('cart') || '[]'),
    // item: { productId, name, price, quantity, category }
  }),
  getters: {
    count: (s) => s.items.reduce((sum, i) => sum + i.quantity, 0),
    totalPrice: (s) => s.items.reduce((sum, i) => sum + i.price * i.quantity, 0),
  },
  actions: {
    save() {
      localStorage.setItem('cart', JSON.stringify(this.items))
    },
    add(product, quantity = 1) {
      const found = this.items.find((i) => i.productId === product.productId)
      if (found) {
        found.quantity += quantity
      } else {
        // 결제가 = 할인가(있으면). 정가는 취소선 표시용으로 같이 보관.
        const dealPrice = product.discountedPrice ?? product.price
        this.items.push({
          productId: product.productId,
          name: product.name,
          price: dealPrice,
          originalPrice: product.price,
          discountRate: product.discountRate ?? 0,
          category: product.category,
          quantity,
        })
      }
      this.save()
    },
    updateQty(productId, quantity) {
      const item = this.items.find((i) => i.productId === productId)
      if (item) {
        item.quantity = Math.max(1, quantity)
        this.save()
      }
    },
    remove(productId) {
      this.items = this.items.filter((i) => i.productId !== productId)
      this.save()
    },
    clear() {
      this.items = []
      this.save()
    },
  },
})
