import http from './http'

export const followApi = {
  follow: (sellerId) => http.post(`/follow/${sellerId}`),
  unfollow: (sellerId) => http.delete(`/follow/${sellerId}`),
  following: () => http.get('/follow/following'),
  seller: (sellerId) => http.get(`/sellers/${sellerId}`),
}
