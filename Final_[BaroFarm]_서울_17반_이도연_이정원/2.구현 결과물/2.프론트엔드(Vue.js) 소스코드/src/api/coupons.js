import http from './http'

export const couponApi = {
  myCoupons: () => http.get('/coupons'), // 내 챌린지 보상 쿠폰 목록
}
