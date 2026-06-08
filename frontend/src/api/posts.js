import http from './http'

export const postApi = {
  list: (page = 0, size = 50) => http.get('/posts', { params: { page, size } }),
  detail: (id) => http.get(`/posts/${id}`),
  create: (payload) => http.post('/posts', payload), // {title, content}
  update: (id, payload) => http.put(`/posts/${id}`, payload),
  remove: (id) => http.delete(`/posts/${id}`),
}

export const commentApi = {
  list: (postId) => http.get(`/posts/${postId}/comments`),
  create: (postId, content) => http.post(`/posts/${postId}/comments`, { content }),
  update: (commentId, content) => http.put(`/comments/${commentId}`, { content }),
  remove: (commentId) => http.delete(`/comments/${commentId}`),
}
