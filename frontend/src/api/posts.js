import http from './http'

export const postApi = {
  list: (params = {}) => http.get('/posts', { params }),
  detail: (id) => http.get(`/posts/${id}`),
  create: (payload) => http.post('/posts', payload), // {title, content}
  update: (id, payload) => http.put(`/posts/${id}`, payload),
  remove: (id) => http.delete(`/posts/${id}`),
  trend: () => http.get('/posts/ai/trend'),
}

export const commentApi = {
  list: (postId) => http.get(`/posts/${postId}/comments`),
  create: (postId, content) => http.post(`/posts/${postId}/comments`, { content }),
  update: (commentId, content) => http.put(`/comments/${commentId}`, { content }),
  remove: (commentId) => http.delete(`/comments/${commentId}`),
}
