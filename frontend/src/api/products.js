import http from './http'

export const productApi = {
  // 목록 (백엔드는 page/size만 지원 → 카테고리·검색·정렬은 클라이언트에서 처리)
  list: (page = 0, size = 100) => http.get('/products', { params: { page, size } }),
  detail: (productId) => http.get(`/products/${productId}`),
  reviews: (productId) => http.get(`/products/${productId}/reviews`),
  // 판매자 본인 상품 (응답에 폐기위험·떨이가 엔진값 포함). X-USER-ID 헤더 필요.
  sellerProducts: () => http.get('/seller/products'),
  // 판매자 상품 관리 (SELLER 권한)
  create: (payload) => http.post('/products', payload),
  update: (productId, payload) => http.put(`/products/${productId}`, payload),
  remove: (productId) => http.delete(`/products/${productId}`),
}
