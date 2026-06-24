import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// 백엔드(Spring Boot, 8080)로 /api 요청을 프록시 → CORS 설정 없이 개발 가능.
// 도커에서는 VITE_PROXY_TARGET=http://backend:8080 주입, 로컬 npm 실행 시 기본값(localhost).
const proxyTarget = process.env.VITE_PROXY_TARGET || 'http://localhost:8080'

// 배너 폴더에 이미지가 추가될 때 HeroBanner 모듈을 재로드하는 플러그인.
// Vite의 glob은 삭제는 자동 감지하지만 추가는 감지 못해서 명시적으로 처리.
function bannerWatcherPlugin() {
  const bannerDirs = [
    path.resolve('src/assets/challenge_banner'),
    path.resolve('src/assets/event_banner'),
    path.resolve('src/assets/coupon_banner'),
  ]

  return {
    name: 'banner-watcher',
    configureServer(server) {
      bannerDirs.forEach(dir => server.watcher.add(dir))

      const filesToInvalidate = [
        path.resolve('src/components/HeroBanner.vue'),
        path.resolve('src/views/BenefitsView.vue'),
      ]

      server.watcher.on('add', (filePath) => {
        if (!bannerDirs.some(dir => filePath.startsWith(dir))) return

        filesToInvalidate.forEach(target => {
          const mods = server.moduleGraph.getModulesByFile(target)
          if (mods) mods.forEach(m => server.moduleGraph.invalidateModule(m))
        })
        server.ws.send({ type: 'full-reload' })
      })
    },
  }
}

export default defineConfig({
  plugins: [vue(), bannerWatcherPlugin()],
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
