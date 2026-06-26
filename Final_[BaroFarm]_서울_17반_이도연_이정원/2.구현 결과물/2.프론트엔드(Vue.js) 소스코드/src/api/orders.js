import http from './http'

export const orderApi = {
  // 1상품 단위 주문 {productId, quantity}
  create: (payload) => http.post('/orders', payload),
  myOrders: () => http.get('/orders/my'),
  detail: (orderId) => http.get(`/orders/${orderId}`),
  insight: () => http.get('/orders/ai/insight'), // 내 구매 분석 AI 인사이트
  // 판매자 — 주문 조회·상태 전이
  sellerOrders: () => http.get('/seller/orders'),
  updateStatus: (orderId, status) => http.patch(`/seller/orders/${orderId}/status`, { status }),
}

export const reviewApi = {
  create: (payload) => http.post('/reviews', payload), // {orderId, rating, content}
}
