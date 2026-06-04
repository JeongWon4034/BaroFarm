import axios from 'axios'

// Vite 프록시를 통해 Spring Boot(/api/v1)로 전달됨
const http = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
})

// 로그인한 사용자의 userId를 X-USER-ID 헤더로 자동 부착 (JWT는 후순위 항목)
http.interceptors.request.use((config) => {
  const userId = localStorage.getItem('userId')
  if (userId) config.headers['X-USER-ID'] = userId
  return config
})

// 백엔드 공통 응답 포맷 { success, message, data, error } → data만 꺼내고, 실패 시 message로 에러
http.interceptors.response.use(
  (res) => {
    const body = res.data
    if (body && body.success === false) {
      return Promise.reject(new Error(body.message || '요청에 실패했습니다.'))
    }
    return body?.data ?? body
  },
  (error) => {
    const msg = error.response?.data?.message || error.message || '서버와 통신할 수 없습니다.'
    return Promise.reject(new Error(msg))
  }
)

export default http
