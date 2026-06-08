import http from './http'

export const orderApi = {
  // 1상품 단위 주문 {productId, quantity}
  create: (payload) => http.post('/orders', payload),
  myOrders: () => http.get('/orders/my'),
  detail: (orderId) => http.get(`/orders/${orderId}`),
}

export const reviewApi = {
  create: (payload) => http.post('/reviews', payload), // {orderId, rating, content}
}
