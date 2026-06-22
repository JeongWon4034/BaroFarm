import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// 백엔드(Spring Boot, 8080)로 /api 요청을 프록시 → CORS 설정 없이 개발 가능.
// 도커에서는 VITE_PROXY_TARGET=http://backend:8080 주입, 로컬 npm 실행 시 기본값(localhost).
const proxyTarget = process.env.VITE_PROXY_TARGET || 'http://localhost:8080'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0', // 컨테이너 밖(호스트 브라우저)에서 접근 가능하게
    port: 5173,
    proxy: {
      '/api': {
        target: proxyTarget,
        changeOrigin: true,
      },
    },
    watch: {
      usePolling: true, // macOS/윈도우 도커 bind mount에서 파일변경 감지 안정화
    },
  },
})
