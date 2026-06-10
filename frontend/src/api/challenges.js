import http from './http'

export const challengeApi = {
  list: () => http.get('/challenges'),
  detail: (id) => http.get(`/challenges/${id}`),
  join: (id) => http.post(`/challenges/${id}/join`),
  myChallenges: () => http.get('/me/challenges'),
}
