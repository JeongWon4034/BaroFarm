import { defineStore } from 'pinia'

// 장바구니: 프론트에서만 관리. 결제 시 항목별로 주문(POST /orders) 생성.
export const useCartStore = defineStore('cart', {
  state: () => ({
    items: JSON.parse(localStorage.getItem('cart') || '[]'),
    // item: { key, productId, lotId, name, price, quantity, category, expirationDate, daysToExpiry }
    // key = productId + lotId 조합 → 같은 상품의 다른 폐기기간 옵션을 별개 항목으로 담는다.
  }),
  getters: {
    count: (s) => s.items.reduce((sum, i) => sum + i.quantity, 0),
    totalPrice: (s) => s.items.reduce((sum, i) => sum + i.price * i.quantity, 0),
  },
  actions: {
    save() {
      localStorage.setItem('cart', JSON.stringify(this.items))
    },
    // lot(폐기기간 옵션)을 골라 담을 수 있다. lot 이 없으면 상품 대표가로 담긴다.
    add(product, quantity = 1, lot = null) {
      const key = `${product.productId}:${lot?.lotId ?? 'base'}`
      const found = this.items.find((i) => i.key === key)
      if (found) {
        found.quantity += quantity
      } else {
        // 결제가 = lot(또는 상품) 할인가. 정가는 취소선 표시용으로 같이 보관.
        const src = lot ?? product
        this.items.push({
          key,
          productId: product.productId,
          lotId: lot?.lotId ?? null,
          name: product.name,
          thumbnailUrl: product.thumbnailUrl ?? null,
          price: src.discountedPrice ?? src.price,
          originalPrice: src.price ?? product.price,
          discountRate: src.discountRate ?? 0,
          category: product.category,
          expirationDate: src.expirationDate ?? null,
          daysToExpiry: src.daysToExpiry ?? null,
          quantity,
        })
      }
      this.save()
    },
    updateQty(key, quantity) {
      const item = this.items.find((i) => i.key === key)
      if (item) {
        item.quantity = Math.max(1, quantity)
        this.save()
      }
    },
    remove(key) {
      this.items = this.items.filter((i) => i.key !== key)
      this.save()
    },
    clear() {
      this.items = []
      this.save()
    },
  },
})
