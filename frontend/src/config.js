// 빌드타임 기능 플래그.
// 분석 대시보드(Streamlit)는 v1 미배포 → VITE_DASHBOARD_ENABLED=false 면 메뉴 숨김.
// 개발(env 미설정)에선 기본 활성, 운영 빌드(web.Dockerfile)에서만 'false'로 끔.
export const DASHBOARD_ENABLED = import.meta.env.VITE_DASHBOARD_ENABLED !== 'false'
