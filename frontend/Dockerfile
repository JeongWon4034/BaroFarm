# 프론트는 개발 모드(Vite dev server + HMR)로 띄운다.
# 소스는 compose에서 bind mount 하므로, 이미지엔 의존성만 설치해 둔다.
FROM node:20-alpine
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

EXPOSE 5173
# vite.config.js 가 host 0.0.0.0 + VITE_PROXY_TARGET 환경변수를 읽음
CMD ["npm", "run", "dev"]
