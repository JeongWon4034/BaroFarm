import http from './http'

export const authApi = {
  signup: (payload) => http.post('/auth/signup', payload), // {email,password,name,role}
  login: (payload) => http.post('/auth/login', payload),   // {email,password} → UserResponse
  me: () => http.get('/users/me'),
  updateProfile: (payload) => http.put('/users/me', payload), // {name, intro, phone, profileImage}
}
