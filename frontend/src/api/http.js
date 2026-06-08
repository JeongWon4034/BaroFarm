import axios from 'axios'

// Vite 프록시를 통해 Spring Boot(/api/v1)로 전달됨
const http = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
})

// JWT 토큰을 Authorization: Bearer 헤더로 자동 부착
http.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers['Authorization'] = `Bearer ${token}`
  return config
})

// 백엔드 공통 응답 포맷 { success, message, data, error } → data만 꺼내고, 실패 시 message로 에러
// 실패 시 구체 메시지(error.detail)와 코드(error.code)를 함께 전달
function toError(data, fallback) {
  const e = new Error(data?.error?.detail || data?.message || fallback)
  e.code = data?.error?.code
  return e
}
http.interceptors.response.use(
  (res) => {
    const body = res.data
    if (body && body.success === false) {
      return Promise.reject(toError(body, '요청에 실패했습니다.'))
    }
    return body?.data ?? body
  },
  (error) => {
    return Promise.reject(toError(error.response?.data, error.message || '서버와 통신할 수 없습니다.'))
  }
)

export default http
