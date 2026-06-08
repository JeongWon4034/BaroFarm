import http from './http'

export const postApi = {
  list: (page = 0, size = 50) => http.get('/posts', { params: { page, size } }),
  detail: (id) => http.get(`/posts/${id}`),
  create: (payload) => http.post('/posts', payload), // {title, content}
  update: (id, payload) => http.put(`/posts/${id}`, payload),
  remove: (id) => http.delete(`/posts/${id}`),
}
