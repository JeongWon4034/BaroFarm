import http from './http'

export const productApi = {
  // 목록 (백엔드는 page/size만 지원 → 카테고리·검색·정렬은 클라이언트에서 처리)
  list: (params = {}) => http.get('/products', { params }), // {page,size,keyword,category,sort}
  detail: (productId) => http.get(`/products/${productId}`),
  lots: (productId) => http.get(`/products/${productId}/lots`), // 폐기기간별 옵션(가격·재고·D-day)
  reviews: (productId) => http.get(`/products/${productId}/reviews`),
  // 판매자 본인 상품 (응답에 폐기위험·할인가 엔진값 포함). X-USER-ID 헤더 필요.
  sellerProducts: () => http.get('/seller/products'),
  // 판매자 상품 관리 (SELLER 권한)
  create: (payload) => http.post('/products', payload),
  update: (productId, payload) => http.put(`/products/${productId}`, payload),
  remove: (productId) => http.delete(`/products/${productId}`),
  // AI 등록 도우미
  priceSuggestion: (name, category) => http.get('/products/ai/price-suggestion', { params: { name, category } }),
  generateDescription: (payload) => http.post('/products/ai/description', payload), // {name, category, expirationDate, stockQty}
  sellerReport: () => http.get('/products/ai/seller-report'),
  recipes: () => http.get('/products/ai/recipes'), // 홈 AI 추천 레시피(판매중 재료 매핑)
  recipeDetail: (idx) => http.get(`/products/ai/recipes/${idx}`), // 조리법 + AI 생성 이미지(첫 호출 ~십수초)
}
