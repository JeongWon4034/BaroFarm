import http from './http'

export const productApi = {
  // 목록 (백엔드는 page/size만 지원 → 카테고리·검색·정렬은 클라이언트에서 처리)
  list: (page = 0, size = 100) => http.get('/products', { params: { page, size } }),
  detail: (productId) => http.get(`/products/${productId}`),
  reviews: (productId) => http.get(`/products/${productId}/reviews`),
}
