# 🥬 BaroFarm(바로팜)

> **산지 직거래 신선식품 마켓 + 마감임박 상품 AI 폐기예측·동적 떨이가**
> 농가와 소비자를 직접 잇고, **마감임박 상품을 AI가 폐기 전에 떨이 할인가로 연결**하는 문제 해결형 이커머스
>
> 2026 SSAFY 공통 프로젝트 (서울 17기) · 이도연 · 이정원

[![Java](https://img.shields.io/badge/Java-17-007396?logo=openjdk&logoColor=white)](https://openjdk.org/)
[![Spring Boot](https://img.shields.io/badge/Spring_Boot-3.3.5-6DB33F?logo=springboot&logoColor=white)](https://spring.io/projects/spring-boot)
![MyBatis](https://img.shields.io/badge/MyBatis-SQL_Mapper-B31B1B)
[![Vue](https://img.shields.io/badge/Vue.js-3.5-4FC08D?logo=vuedotjs&logoColor=white)](https://vuejs.org/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?logo=mysql&logoColor=white)](https://www.mysql.com/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![OpenAI](https://img.shields.io/badge/LLM-gpt--4o-412991?logo=openai&logoColor=white)](https://openai.com/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

🔗 **라이브 서비스**: https://barofarm.duckdns.org

---

## 📌 목차

1. [프로젝트 개요](#1-프로젝트-개요)
2. [핵심 차별점](#2-핵심-차별점)
3. [시스템 아키텍처](#3-시스템-아키텍처)
4. [기술 스택](#4-기술-스택)
5. [AI·데이터 활용 (3-Layer)](#5-ai데이터-활용-3-layer)
6. [ERD](#6-erd)
7. [주요 기능](#7-주요-기능)
8. [화면 구성](#8-화면-구성)
9. [프로젝트 구조](#9-프로젝트-구조)
10. [로컬 실행 방법](#10-로컬-실행-방법)
11. [시연 계정](#11-시연-계정)

---

## 1. 프로젝트 개요

**BaroFarm(바로팜)**은 농가(판매자)와 소비자를 직접 잇는 산지 직거래 마켓입니다.
신선식품 유통의 고질적 문제인 **판매자의 폐기 손실**과 **소비자의 높은 가격**을 동시에 해결하는 것이 핵심입니다.

> 마감임박 상품을 AI가 폐기되기 전에 **동적 할인가**로 연결하여,
> 버려질 재고를 합리적 가격의 상품으로 전환합니다.

| 항목 | 내용 |
|------|------|
| 해결 문제 | 신선식품 유통 폐기 손실(판매자) + 비싼 신선식품 가격(소비자) |
| 핵심 가치 | ① 판매자: 폐기 손실↓·재고 회전↑  ② 구매자: 신선식품을 더 저렴하게 |
| 사용자 | 구매자(Buyer) · 판매자(Seller) · 관리자(Admin) |
| 개발 규모 | 백엔드 컨트롤러 16개 · REST 47 엔드포인트 · 화면 29개 · DB 14테이블 |

---

## 2. 핵심 차별점

| # | 기능 | 설명 |
|---|------|------|
| 1 | **마감임박 동적 할인 엔진** | 유통기한 D-day × 재고 → 폐기위험 점수·할인율(최대 60%)을 서버에서 권위 있게 실시간 산출 (`WastePricingEngine`). 같은 품목을 유통기한·가격이 다른 여러 `lot`으로 분리 판매 |
| 2 | **AI 추천 판매가** | KAMIS 실시세 + 네이버쇼핑 경쟁가를 LLM(gpt-4o)이 묶음단위(2kg·500g·4팩)까지 정규화해 판매단위 추천가 산출 (실패 시 산식 폴백) |
| 3 | **멀티 판매처 가격 비교** | 동일 품목을 파는 여러 농가의 가격·D-day를 한 화면에서 비교 |
| 4 | **판매자 분석 대시보드** | Reflex/Streamlit 대시보드 — 공급망 최적화·매출·수요 예측 + 생성형 AI 종합 분석 |
| 5 | **데이터 정합성 원칙** | "가짜 수치 금지" — 할인·절약액·추천은 모두 실제 데이터/계산 기반, AI 추천은 DB 실재 상품 안에서만(할루시네이션 차단) |

---

## 3. 시스템 아키텍처

3-Tier 구조(Vue SPA — Spring Boot REST — MySQL)이며, 분석 영역은 동일 DB를 읽는 별도 서비스로 분리됩니다.

```
┌──────────────────────────────────────────────────────────────┐
│   Vue 3 SPA (소비자/판매자 UI · Pinia · Vue Router · Vite)     │
└───────────────────────────┬──────────────────────────────────┘
                            │ REST API (JSON / JWT)
┌───────────────────────────▼──────────────────────────────────┐
│   Spring Boot 3.3.5  (Controller → Service → Mapper)          │
│   인증(JWT·BCrypt) · 상품/주문 · 소셜 · 챌린지/쿠폰            │
│   AI 추천가(KAMIS+네이버+gpt-4o) · WastePricingEngine          │
└───────────────────────────┬──────────────────────────────────┘
                            │
┌───────────────────────────▼──────────────────────────────────┐
│   MySQL 8.0  (14 테이블 · 외래키 19개 · 3NF)                   │
└───────────────────────────┬──────────────────────────────────┘
                            │ 동일 DB 읽기
┌───────────────────────────▼──────────────────────────────────┐
│   분석 대시보드 (Reflex / Streamlit · Python)                 │
│   scikit-learn 예측 · 공급망 최적화 · 생성형 AI 종합 분석     │
└──────────────────────────────────────────────────────────────┘

배포: Docker Compose · Caddy(자동 HTTPS) · DuckDNS · 클라우드 VM
```

---

## 4. 기술 스택

| 영역 | 스택 |
|------|------|
| **Frontend** | Vue 3.5 (SPA) · Vue Router · Pinia · Vite 5 · Axios |
| **Backend** | Java 17 · Spring Boot 3.3.5 · MyBatis · JWT(jjwt) · BCrypt · Maven |
| **Database** | MySQL 8.0 (14 테이블) |
| **Data/AI** | Reflex · Streamlit · scikit-learn · pandas · plotly · OpenAI(gpt-4o / gpt-4o-mini) |
| **외부 API** | KAMIS 농수산물 시세 · 네이버쇼핑 검색 · GMS(OpenAI 호환 LLM) · 식약처 레시피 |
| **Infra** | Docker Compose · Caddy(자동 HTTPS) · DuckDNS · 클라우드 VM |

---

## 5. AI·데이터 활용 (3-Layer)

AI를 한 덩어리가 아니라 **역할별로 적합한 기술**을 골라 적용했습니다.

| 층 | 무엇 | 기술 | 위치 |
|----|------|------|------|
| ① **규칙 기반 엔진** | 마감임박 동적 할인 | 유통기한 D-day × 재고 → 위험점수·할인율 산식 | `WastePricingEngine` |
| ② **전통 ML** | 매출/수요 예측, 고객 세그먼트 | scikit-learn — Ridge / LinearRegression / RFM + KMeans | 분석 대시보드 |
| ③ **생성형 AI(LLM)** | AI 추천 판매가, 공급망 종합 분석 | gpt-4o / gpt-4o-mini (OpenAI 호환) | 추천가 엔진 · 대시보드 |

> **신뢰성**: 모든 외부 AI/시세 호출은 실패 시 **규칙 기반 폴백**으로 자동 전환되어 서비스가 끊기지 않습니다(NFR-5).
> **데이터**: 상품·가격은 KAMIS 실시세 기반, 주문·구매자는 현실적 분포의 합성 시드(구매자 1.5천 · 주문 1만). 데이터값이 아니라 **로직·파이프라인**이 실데이터에서 그대로 동작하도록 설계.

### 분석 대시보드 ML 모델

| 모델 | 알고리즘 | 산출물 |
|------|----------|--------|
| 매출 예측 | Ridge Regression | 기간별 예상 매출 |
| 수요 예측 | LinearRegression | 품목별 예상 수요 |
| 고객 분석 | RFM + KMeans | 고객 세그먼트 |
| 매입 추천 | MinMax 정규화 가중합 | 발주 권장 품목 |
| 계절성 | 월별 집계 | 수요 패턴 |

---

## 6. ERD

> MySQL 8.0 · 스키마 `freshgrowth` (utf8mb4) · **14 테이블 · 외래키 19개 · 3NF**
> DDL 원본: [`backend/src/main/resources/schema.sql`](./backend/src/main/resources/schema.sql)

| 테이블 | 설명 |
|--------|------|
| `users` | 회원 (BUYER/SELLER/ADMIN, BCrypt 비밀번호) |
| `products` | 상품/품목 마스터 (seller_id, 카테고리, 대표 가격·재고) |
| `product_lots` | 폐기기간별 판매 옵션 (유통기한·재고·가격, **동적 할인의 핵심**) |
| `orders` | 주문 (정가 박제 `original_unit_price` → 절약액 추적) |
| `reviews` | 리뷰 (주문 1:1, 별점 1~5) |
| `wishlists` | 찜 (상품·판매처별) |
| `follows` | 농가 팔로우 (자기참조 N:M) |
| `posts` / `comments` | 게시판 / 댓글·대댓글(1-depth) |
| `challenges` / `user_challenges` | 마감임박 절감 챌린지 / 참여 |
| `user_coupons` | 챌린지 보상 쿠폰 |
| `user_behavior_logs` | 퍼널·A/B 행동 로그 (FK 비결합) |
| `invalidated_tokens` | JWT 무효화 블랙리스트 (SHA-256) |

**설계 포인트**
- **품목 ↔ lot 분리**: 같은 품목을 유통기한·가격이 다른 여러 lot으로 판매 — 마감임박 동적 할인의 기반 구조
- **주문 시점 가격 박제**: `total_price`(실결제) + `original_unit_price`(정가) 동시 저장 → 사후 변동과 무관하게 절약액 정확 집계
- **로그/토큰 FK 비결합**: 상품·회원 삭제와 독립적으로 보존

---

## 7. 주요 기능

| 영역 | 기능 |
|------|------|
| **회원·인증** | 이메일·역할 회원가입(비번 8자+2종류 강제) · JWT 로그인/로그아웃 · 토큰 블랙리스트 · 권한 인터셉터(401/403) |
| **상품·탐색** | 카테고리·키워드·정렬·페이징 · lot별 가격/D-day/할인 · 타 판매처 비교 · 마감임박 전용 탭(`/deals`) |
| **주문·결제** | 서버 권위 할인가 재계산 · 재고 차감·EXPIRED 차단 · 쿠폰 합산 상한 · 주문 상태머신(4단계) |
| **소셜** | 찜 · 농가 팔로잉 · 리뷰 · 게시판(5종)·댓글/대댓글 |
| **챌린지·혜택** | 목표형 마감임박 챌린지 · 달성 보상 쿠폰 자동 발급 · 혜택/공지 배너 |
| **AI·데이터** | AI 추천 판매가 · 마감임박 동적 할인 · 판매자 인사이트(14일 추이·정체신호) · 구매 분석 · 분석 대시보드 |

---

## 8. 화면 구성

> Vue 3 SPA · **총 29개 화면** (공개 / 로그인 / 판매자 / 관리자)

- **공개/구매**: 홈 · 상품 상세 · 마감임박 딜 · 베스트 · 혜택및공지 · 소개 · 레시피 상세
- **주문·소셜**: 장바구니 · 주문완료 · 찜 · 팔로잉 · 마이허브 · 마이페이지 · 구매분석 · 쿠폰 · 챌린지
- **커뮤니티**: 게시판 목록/상세 · 글 작성/수정
- **판매자**: 판매자 센터 · 상품 관리(AI 추천가) · 주문 관리 · 판매자 대시보드 · 내 정보 수정
- **관리자/인증**: 운영 분석 · 로그인 · 회원가입(비밀번호 강도미터)

---

## 9. 프로젝트 구조

```
15pjt_lees/
├── frontend/                  # Vue 3 SPA (소비자/판매자 UI)
│   └── src/ ├── api/ ├── router/ ├── stores/(Pinia) ├── views/ └── components/
│
├── backend/                   # Spring Boot 3.3.5 (Maven)
│   └── src/main/java/com/freshgrowth/
│       ├── user/ product/ order/ review/      # 핵심 도메인
│       ├── wishlist/ follow/ post/ comment/   # 소셜·커뮤니티
│       ├── challenge/ coupon/ event/          # 챌린지·혜택
│       ├── product/ai/  product/WastePricingEngine.java   # AI 추천가·동적할인
│       ├── upload/ common/(auth·인터셉터)
│       └── resources/ ├── schema.sql ├── seed_*.sql └── mapper/*.xml
│
├── analytics/                 # Streamlit 분석 대시보드 (scikit-learn)
├── analytics_reflex/          # Reflex 분석 대시보드 (공급망 최적화·AI 종합분석)
├── deploy/                    # Caddy(HTTPS) 운영 배포 구성
└── docker-compose*.yml        # 개발/운영 컨테이너 구성
```

---

## 10. 로컬 실행 방법

### Docker Compose (권장)

```bash
# 전체 스택 (MySQL + Spring + Vue + Streamlit) 기동
docker compose up -d --build

# 접속
#   프론트(Vue)   : http://localhost:5173
#   백엔드(API)   : http://localhost:8080
#   분석(Streamlit): http://localhost:8501
```

### 분석 대시보드(Reflex) 추가 기동

```bash
docker compose -f docker-compose.yml -f docker-compose.reflex.yml up -d --build reflex
#   Reflex 대시보드: http://localhost:3001/?seller_id=1
```

### 환경변수

외부 API 키는 코드에 노출하지 않고 환경변수로 주입합니다(`.env`, git 미추적).

```
AI_BASE_URL / AI_API_KEY / AI_MODEL      # 생성형 AI (OpenAI 호환)
KAMIS_CERT_KEY / KAMIS_CERT_ID           # 농수산물 시세
NAVER_CLIENT_ID / NAVER_CLIENT_SECRET    # 네이버쇼핑 경쟁가
JWT_SECRET                               # JWT 서명
```

---

---

> **문의**: [leewon12381@gmail.com](mailto:leewon12381@gmail.com)
