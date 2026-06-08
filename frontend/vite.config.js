import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// 백엔드(Spring Boot, 8080)로 /api 요청을 프록시 → CORS 설정 없이 개발 가능
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
    },
  },
})
