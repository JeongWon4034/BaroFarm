import http from './http'

export const productApi = {
  // 목록 (백엔드는 page/size만 지원 → 카테고리·검색·정렬은 클라이언트에서 처리)
  list: (params = {}) => http.get('/products', { params }), // {page,size,keyword,category,sort}
  detail: (productId) => http.get(`/products/${productId}`),
  lots: (productId) => http.get(`/products/${productId}/lots`), // 폐기기간별 옵션(가격·재고·D-day)
  reviews: (productId) => http.get(`/products/${productId}/reviews`),
  // 판매자 본인 상품 (응답에 폐기위험·할인가 엔진값 포함). X-USER-ID 헤더 필요.
  sellerProducts: () => http.get('/seller/products'),
  sellerSales: () => http.get('/seller/products/sales'), // 상품별 판매 분석(판매량·매출·절약회수·14일 추이)
  sellerInsights: () => http.get('/seller/products/insights'), // KAMIS 소매가·현재가·추천가 + 정체 신호
  productAction: (productId) => http.get(`/seller/products/${productId}/action`), // 정체상품 AI 행동추천(hover)
  // 판매자 상품 관리 (SELLER 권한)
  create: (payload) => http.post('/products', payload),
  update: (productId, payload) => http.put(`/products/${productId}`, payload),
  remove: (productId) => http.delete(`/products/${productId}`),
  // AI 등록 도우미
  priceSuggestion: (name, category, unit) => http.get('/products/ai/price-suggestion', { params: { name, category, unit } }),
  generateDescription: (payload) => http.post('/products/ai/description', payload), // {name, category, expirationDate, stockQty}
  uploadImage: (file) => { // 상품 이미지 업로드 → { url }
    const fd = new FormData()
    fd.append('file', file)
    return http.post('/uploads', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
  },
  sellerReport: () => http.get('/products/ai/seller-report'),
  recipes: () => http.get('/products/ai/recipes'), // 홈 AI 추천 레시피(판매중 재료 매핑)
  recipeDetail: (idx) => http.get(`/products/ai/recipes/${idx}`), // 조리법 + AI 생성 이미지(첫 호출 ~십수초)
}
