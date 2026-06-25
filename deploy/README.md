# BaroFarm v1 배포 가이드

메인 앱(Vue + Spring + MySQL)을 **Caddy 단일 진입점**으로 배포한다.
분석 대시보드는 v1 미배포(2단계 Reflex 예정) — 메뉴 자동 숨김.

```
[브라우저] ──HTTPS──> [web: Caddy] ─┬─ 정적 프론트(dist) + /seed-images
                                    ├─ /api/*    ─> [backend: Spring :8080]
                                    └─ /uploads/* ─> [backend: Spring :8080]
                                                       └─ [mysql :3306 (내부망)]
```

## 구성 파일
| 파일 | 역할 |
|---|---|
| `docker-compose.prod.yml` | mysql + backend + web(Caddy) |
| `deploy/web.Dockerfile` | 프론트 `vite build` → Caddy 서빙 + 프록시 |
| `deploy/Caddyfile` | 정적 서빙 + `/api`·`/uploads` 프록시 + 자동 HTTPS |
| `.env.prod.example` | 운영 환경변수 템플릿 |
| `.github/workflows/deploy.yml` | main 푸시 시 VM 자동 재배포 |

## 1. 사전 준비 (1회)
1. **Oracle Cloud Always Free VM**(ARM/arm64 권장, Ubuntu) 생성, 22/80/443 포트 개방
2. VM에 **Docker + compose 플러그인** 설치
3. **DuckDNS** 무료 서브도메인 발급(예: `baro-farm.duckdns.org`) → VM 공인 IP로 A레코드
4. VM에서 레포 클론:
   ```bash
   git clone https://lab.ssafy.com/dlehduslee/15pjt_lees.git ~/15pjt_lees
   cd ~/15pjt_lees
   cp .env.prod.example .env   # 값 채우기 (DOMAIN, 비번, JWT, API 키들)
   ```

## 2. 첫 배포
```bash
cd ~/15pjt_lees
docker compose -f docker-compose.prod.yml up -d --build
```
- 최초 1회 MySQL이 시드 5종 자동 적재(개발과 동일 데이터). Caddy가 DuckDNS 도메인으로 Let's Encrypt 인증서 자동 발급.
- 확인: `https://<도메인>` 접속.

## 3. 자동 배포 (GitHub Actions)
GitHub 레포(미러)에 아래 **Secrets** 등록 → `main` 푸시 시 자동 재배포:
| Secret | 값 |
|---|---|
| `VM_HOST` | VM 공인 IP |
| `VM_USER` | SSH 사용자(예: ubuntu) |
| `VM_SSH_KEY` | VM 접속 개인키(PEM 전체) |
| `VM_APP_DIR` | (선택) 레포 경로, 기본 `~/15pjt_lees` |

> Actions는 GitHub에서 돌아가니 **GitHub 미러로도 push**해야 트리거됨. VM은 `git pull`로 최신 main을 받음(VM 레포의 origin이 최신 main을 가리키게 둘 것).

## 주의 / 트러블슈팅
- **GMS(AI) 망**: VM에서 `curl -I https://gms.ssafy.io` 안 되면 AI 추천가는 규칙기반 폴백. 필요 시 `.env`의 `AI_BASE_URL/AI_API_KEY`를 실제 OpenAI로 교체.
- **비밀값**: 운영에선 `MYSQL_ROOT_PASSWORD`·`JWT_SECRET`을 반드시 강한 값으로(`openssl rand -base64 48`).
- **인증서**: `caddy-data` 볼륨에 저장돼 재배포해도 재발급 안 함. 도메인 바꾸면 `.env`의 DOMAIN만 교체.
- **데이터 초기화**: 시드를 다시 적재하려면 `docker compose -f docker-compose.prod.yml down -v`(⚠️ DB·업로드 삭제) 후 재기동.
- **2단계 대시보드(Reflex)**: 준비되면 compose에 `dashboard` 서비스 + Caddy 서브도메인 추가, 프론트 `VITE_DASHBOARD_ENABLED=true` + iframe URL 교체.
