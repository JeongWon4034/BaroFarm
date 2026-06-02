# FreshGrowth REST API 설계서

## 1. 문서 개요

본 문서는 **FreshGrowth — 신선식품 직거래 마켓 & 데이터 기반 판매 운영 서비스**의 REST API 설계 내용을 정의한다.

FreshGrowth는 Vue 기반 프론트엔드와 Spring Boot 백엔드가 JSON 형식으로 통신하는 구조를 가진다.  
백엔드는 **Spring Boot + MyBatis + MySQL** 기반으로 구현하며, 초기 제출 범위에서는 MongoDB와 Kafka를 사용하지 않는다.

본 API 설계서는 다음 내용을 포함한다.

- REST API 공통 규칙
- 인증 방식 및 권한 정책
- 공통 응답 형식
- 공통 에러 응답 형식
- 기능별 API 목록
- 주요 API 요청/응답 예시
- 화면별 API 매핑
- MySQL 테이블 매핑

---

## 2. API 설계 원칙

### 2.1 기본 원칙

| 항목 | 원칙 |
|---|---|
| 통신 형식 | JSON |
| URI 규칙 | `/api/v1` prefix 사용 |
| HTTP Method | GET, POST, PUT, DELETE 사용 |
| 응답 형식 | 공통 응답 객체 사용 |
| 인증 방식 | 초기 구현은 세션 또는 JWT 중 선택 가능, 설계 기준은 JWT |
| API 문서화 | Swagger/OpenAPI 적용 |
| DB 접근 | MyBatis Mapper XML을 통한 SQL 실행 |
| 데이터 저장소 | MySQL |

---

### 2.2 HTTP Method 사용 기준

| Method | 용도 | 예시 |
|---|---|---|
| GET | 데이터 조회 | 상품 목록 조회, 주문 내역 조회 |
| POST | 데이터 생성 | 회원가입, 로그인, 상품 등록, 주문 생성 |
| PUT | 데이터 전체 또는 주요 정보 수정 | 상품 수정, 회원 정보 수정, 리뷰 수정 |
| DELETE | 데이터 삭제 또는 비활성화 | 상품 삭제, 리뷰 삭제, 회원 탈퇴 |

---

### 2.3 HTTP 상태 코드 정책

| 상태 코드 | 의미 | 사용 상황 |
|---|---|---|
| 200 OK | 요청 성공 | 조회, 수정, 삭제 성공 |
| 201 Created | 생성 성공 | 회원가입, 상품 등록, 주문 생성, 리뷰 작성 |
| 400 Bad Request | 잘못된 요청 | 입력값 누락, 형식 오류, 재고 부족 |
| 401 Unauthorized | 인증 실패 | 로그인하지 않은 사용자 |
| 403 Forbidden | 권한 없음 | 다른 판매자의 상품 수정 시도 |
| 404 Not Found | 리소스 없음 | 존재하지 않는 상품, 주문, 리뷰 조회 |
| 409 Conflict | 충돌 | 중복 이메일, 중복 리뷰 작성 |
| 500 Internal Server Error | 서버 오류 | 처리 중 예상하지 못한 오류 |

---

## 3. 공통 응답 형식

### 3.1 성공 응답

```json
{
  "success": true,
  "message": "요청이 성공적으로 처리되었습니다.",
  "data": {}
}
```

### 3.2 목록 조회 응답

```json
{
  "success": true,
  "message": "상품 목록을 조회했습니다.",
  "data": {
    "content": [],
    "page": 0,
    "size": 10,
    "totalElements": 100,
    "totalPages": 10,
    "last": false
  }
}
```

### 3.3 실패 응답

```json
{
  "success": false,
  "message": "요청 처리에 실패했습니다.",
  "error": {
    "code": "PRODUCT_NOT_FOUND",
    "detail": "존재하지 않는 상품입니다."
  }
}
```

---

## 4. 인증 및 권한 정책

### 4.1 사용자 역할

| 역할 | 설명 |
|---|---|
| PUBLIC | 인증 없이 접근 가능 |
| USER | 로그인한 사용자 |
| BUYER | 구매자 |
| SELLER | 판매자 |

### 4.2 인증 헤더

JWT 방식을 사용할 경우 인증이 필요한 요청에는 아래 헤더를 포함한다.

```http
Authorization: Bearer {accessToken}
```

### 4.3 권한 적용 기준

| 기능 | 권한 |
|---|---|
| 상품 목록 조회 | PUBLIC |
| 상품 상세 조회 | PUBLIC |
| 회원가입 / 로그인 | PUBLIC |
| 내 정보 조회 / 수정 / 탈퇴 | USER |
| 상품 등록 / 수정 / 삭제 | SELLER |
| 주문 생성 | BUYER |
| 내 주문 내역 조회 | BUYER |
| 판매 내역 조회 | SELLER |
| 리뷰 작성 / 수정 / 삭제 | BUYER |
| 판매자 분석 API | SELLER |
| 추천 API | PUBLIC 또는 BUYER |

---

## 5. API 목록 요약

## 5.1 Auth API

| Method | URI | 설명 | 권한 |
|---|---|---|---|
| POST | `/api/v1/auth/signup` | 회원가입 | PUBLIC |
| POST | `/api/v1/auth/login` | 로그인 | PUBLIC |
| POST | `/api/v1/auth/logout` | 로그아웃 | USER |
| POST | `/api/v1/auth/refresh` | Access Token 재발급 | USER |

---

## 5.2 User API

| Method | URI | 설명 | 권한 |
|---|---|---|---|
| GET | `/api/v1/users/me` | 내 정보 조회 | USER |
| PUT | `/api/v1/users/me` | 내 정보 수정 | USER |
| DELETE | `/api/v1/users/me` | 회원 탈퇴 또는 비활성화 | USER |

---

## 5.3 Product API

| Method | URI | 설명 | 권한 |
|---|---|---|---|
| GET | `/api/v1/products` | 상품 목록 조회 | PUBLIC |
| GET | `/api/v1/products/{productId}` | 상품 상세 조회 | PUBLIC |
| POST | `/api/v1/products` | 상품 등록 | SELLER |
| PUT | `/api/v1/products/{productId}` | 상품 수정 | SELLER |
| DELETE | `/api/v1/products/{productId}` | 상품 삭제 | SELLER |
| GET | `/api/v1/seller/products` | 판매자 본인 상품 목록 조회 | SELLER |

---

## 5.4 Order API

| Method | URI | 설명 | 권한 |
|---|---|---|---|
| POST | `/api/v1/orders` | 주문 생성 | BUYER |
| GET | `/api/v1/orders/my` | 내 주문 내역 조회 | BUYER |
| GET | `/api/v1/orders/{orderId}` | 주문 상세 조회 | BUYER |
| GET | `/api/v1/seller/orders` | 판매 내역 조회 | SELLER |

---

## 5.5 Review API

| Method | URI | 설명 | 권한 |
|---|---|---|---|
| POST | `/api/v1/reviews` | 리뷰 작성 | BUYER |
| GET | `/api/v1/products/{productId}/reviews` | 상품별 리뷰 목록 조회 | PUBLIC |
| PUT | `/api/v1/reviews/{reviewId}` | 리뷰 수정 | BUYER |
| DELETE | `/api/v1/reviews/{reviewId}` | 리뷰 삭제 | BUYER |

---

## 5.6 Behavior Log API

| Method | URI | 설명 | 권한 |
|---|---|---|---|
| POST | `/api/v1/logs` | 행동 로그 저장 | PUBLIC / USER |
| GET | `/api/v1/logs/my` | 내 행동 로그 조회 | USER |

---

## 5.7 Analytics API

| Method | URI | 설명 | 권한 |
|---|---|---|---|
| GET | `/api/v1/analytics/funnel` | 퍼널 전환율 조회 | SELLER |
| GET | `/api/v1/analytics/ab-test` | A/B 테스트 결과 조회 | SELLER |
| GET | `/api/v1/analytics/sales-summary` | 상품별 판매 지표 조회 | SELLER |
| GET | `/api/v1/analytics/dashboard-summary` | 판매자 대시보드 요약 지표 조회 | SELLER |
| GET | `/api/v1/analytics/demand-forecast` | 수요 예측 결과 조회 | SELLER |
| GET | `/api/v1/analytics/spoilage-risk` | 폐기 위험 상품 조회 | SELLER |

---

## 5.8 Recommendation API

| Method | URI | 설명 | 권한 |
|---|---|---|---|
| GET | `/api/v1/recommendations/products` | 소비자 맞춤 상품 추천 | BUYER |
| GET | `/api/v1/recommendations/popular` | 인기 상품 추천 | PUBLIC |

---

# 6. API 상세 설계

## 6.1 Auth API

### 6.1.1 회원가입

| 항목 | 내용 |
|---|---|
| Method | POST |
| URI | `/api/v1/auth/signup` |
| 설명 | 구매자 또는 판매자 회원가입 |
| 권한 | PUBLIC |
| 관련 테이블 | `users` |

#### Request Body

```json
{
  "email": "buyer@example.com",
  "password": "1234",
  "name": "김도연",
  "role": "BUYER"
}
```

#### Response Body

```json
{
  "success": true,
  "message": "회원가입이 완료되었습니다.",
  "data": {
    "userId": 1,
    "email": "buyer@example.com",
    "name": "김도연",
    "role": "BUYER",
    "status": "ACTIVE"
  }
}
```

#### 예외

| 상태 코드 | 에러 코드 | 설명 |
|---|---|---|
| 400 | INVALID_INPUT | 필수 입력값 누락 |
| 409 | DUPLICATED_EMAIL | 이미 사용 중인 이메일 |

---

### 6.1.2 로그인

| 항목 | 내용 |
|---|---|
| Method | POST |
| URI | `/api/v1/auth/login` |
| 설명 | 이메일과 비밀번호로 로그인 |
| 권한 | PUBLIC |
| 관련 테이블 | `users` |

#### Request Body

```json
{
  "email": "buyer@example.com",
  "password": "1234"
}
```

#### Response Body

```json
{
  "success": true,
  "message": "로그인에 성공했습니다.",
  "data": {
    "accessToken": "jwt-access-token",
    "refreshToken": "jwt-refresh-token",
    "user": {
      "userId": 1,
      "email": "buyer@example.com",
      "name": "김도연",
      "role": "BUYER"
    }
  }
}
```

---

### 6.1.3 로그아웃

| 항목 | 내용 |
|---|---|
| Method | POST |
| URI | `/api/v1/auth/logout` |
| 설명 | 로그인 상태 종료 |
| 권한 | USER |

#### Response Body

```json
{
  "success": true,
  "message": "로그아웃되었습니다.",
  "data": null
}
```

---

## 6.2 User API

### 6.2.1 내 정보 조회

| 항목 | 내용 |
|---|---|
| Method | GET |
| URI | `/api/v1/users/me` |
| 설명 | 로그인한 사용자의 회원 정보 조회 |
| 권한 | USER |
| 관련 테이블 | `users` |

#### Response Body

```json
{
  "success": true,
  "message": "내 정보를 조회했습니다.",
  "data": {
    "userId": 1,
    "email": "buyer@example.com",
    "name": "김도연",
    "role": "BUYER",
    "status": "ACTIVE",
    "createdAt": "2026-05-22T10:00:00"
  }
}
```

---

### 6.2.2 내 정보 수정

| 항목 | 내용 |
|---|---|
| Method | PUT |
| URI | `/api/v1/users/me` |
| 설명 | 로그인한 사용자의 이름 또는 비밀번호 수정 |
| 권한 | USER |
| 관련 테이블 | `users` |

#### Request Body

```json
{
  "name": "김도연",
  "password": "new-password"
}
```

#### Response Body

```json
{
  "success": true,
  "message": "회원 정보가 수정되었습니다.",
  "data": {
    "userId": 1,
    "email": "buyer@example.com",
    "name": "김도연",
    "role": "BUYER",
    "status": "ACTIVE"
  }
}
```

---

### 6.2.3 회원 탈퇴

| 항목 | 내용 |
|---|---|
| Method | DELETE |
| URI | `/api/v1/users/me` |
| 설명 | 회원 상태를 비활성화 처리 |
| 권한 | USER |
| 관련 테이블 | `users` |

#### Response Body

```json
{
  "success": true,
  "message": "회원 탈퇴가 완료되었습니다.",
  "data": null
}
```

---

## 6.3 Product API

### 6.3.1 상품 목록 조회

| 항목 | 내용 |
|---|---|
| Method | GET |
| URI | `/api/v1/products?page=0&size=10&category=vegetable&keyword=상추` |
| 설명 | 상품 목록을 페이지네이션으로 조회 |
| 권한 | PUBLIC |
| 관련 테이블 | `products`, `reviews` |

#### Query Parameter

| 이름 | 타입 | 필수 | 설명 |
|---|---|---|---|
| page | int | N | 페이지 번호, 기본값 0 |
| size | int | N | 페이지 크기, 기본값 10 |
| category | string | N | 카테고리 |
| keyword | string | N | 검색어 |
| sort | string | N | 정렬 기준, 예: `latest`, `priceAsc`, `priceDesc` |

#### Response Body

```json
{
  "success": true,
  "message": "상품 목록을 조회했습니다.",
  "data": {
    "content": [
      {
        "productId": 1,
        "sellerId": 2,
        "name": "무농약 청상추",
        "price": 3900,
        "stockQty": 42,
        "thumbnailUrl": "https://cdn.example.com/lettuce.png",
        "category": "vegetable",
        "averageRating": 4.7,
        "reviewCount": 12
      }
    ],
    "page": 0,
    "size": 10,
    "totalElements": 100,
    "totalPages": 10,
    "last": false
  }
}
```

---

### 6.3.2 상품 상세 조회

| 항목 | 내용 |
|---|---|
| Method | GET |
| URI | `/api/v1/products/{productId}` |
| 설명 | 상품 ID로 상세 정보 조회 |
| 권한 | PUBLIC |
| 관련 테이블 | `products`, `users`, `reviews` |

#### Path Variable

| 이름 | 타입 | 설명 |
|---|---|---|
| productId | Long | 상품 ID |

#### Response Body

```json
{
  "success": true,
  "message": "상품 상세 정보를 조회했습니다.",
  "data": {
    "productId": 1,
    "sellerId": 2,
    "sellerName": "도연농장",
    "name": "무농약 청상추",
    "description": "아침에 수확한 신선한 청상추입니다.",
    "price": 3900,
    "stockQty": 42,
    "thumbnailUrl": "https://cdn.example.com/lettuce.png",
    "category": "vegetable",
    "expirationDate": "2026-05-30",
    "abVariant": "A",
    "averageRating": 4.7,
    "reviewCount": 12,
    "createdAt": "2026-05-22T10:00:00"
  }
}
```

---

### 6.3.3 상품 등록

| 항목 | 내용 |
|---|---|
| Method | POST |
| URI | `/api/v1/products` |
| 설명 | 판매자가 상품 등록 |
| 권한 | SELLER |
| 관련 테이블 | `products` |

#### Request Body

```json
{
  "name": "무농약 청상추",
  "description": "아침에 수확한 신선한 청상추입니다.",
  "price": 3900,
  "stockQty": 42,
  "thumbnailUrl": "https://cdn.example.com/lettuce.png",
  "category": "vegetable",
  "expirationDate": "2026-05-30",
  "abVariant": "A"
}
```

#### Response Body

```json
{
  "success": true,
  "message": "상품이 등록되었습니다.",
  "data": {
    "productId": 1,
    "name": "무농약 청상추",
    "price": 3900,
    "stockQty": 42
  }
}
```

---

### 6.3.4 상품 수정

| 항목 | 내용 |
|---|---|
| Method | PUT |
| URI | `/api/v1/products/{productId}` |
| 설명 | 판매자가 본인 상품 정보 수정 |
| 권한 | SELLER |
| 관련 테이블 | `products` |

#### Request Body

```json
{
  "name": "무농약 청상추 500g",
  "description": "신선하게 포장한 청상추입니다.",
  "price": 4200,
  "stockQty": 30,
  "thumbnailUrl": "https://cdn.example.com/lettuce-new.png",
  "category": "vegetable",
  "expirationDate": "2026-05-31",
  "abVariant": "B"
}
```

---

### 6.3.5 상품 삭제

| 항목 | 내용 |
|---|---|
| Method | DELETE |
| URI | `/api/v1/products/{productId}` |
| 설명 | 판매자가 본인 상품 삭제 |
| 권한 | SELLER |
| 관련 테이블 | `products` |

#### Response Body

```json
{
  "success": true,
  "message": "상품이 삭제되었습니다.",
  "data": null
}
```

---

### 6.3.6 판매자 상품 목록 조회

| 항목 | 내용 |
|---|---|
| Method | GET |
| URI | `/api/v1/seller/products` |
| 설명 | 로그인한 판매자가 본인 상품 목록 조회 |
| 권한 | SELLER |
| 관련 테이블 | `products` |

---

## 6.4 Order API

### 6.4.1 주문 생성

| 항목 | 내용 |
|---|---|
| Method | POST |
| URI | `/api/v1/orders` |
| 설명 | 구매자가 상품을 주문한다. 결제는 Mock 처리한다. |
| 권한 | BUYER |
| 관련 테이블 | `orders`, `products`, `behavior_logs` |

#### Request Body

```json
{
  "productId": 1,
  "quantity": 2
}
```

#### 처리 규칙

| 규칙 | 설명 |
|---|---|
| 재고 확인 | 상품 재고가 주문 수량보다 적으면 주문 실패 |
| 총 가격 계산 | `상품 가격 × 주문 수량` |
| 주문 상태 | `COMPLETED`로 저장 |
| 재고 차감 | 주문 성공 시 상품 재고 차감 |
| 로그 저장 | 주문 완료 시 `complete_order` 로그 저장 가능 |

#### Response Body

```json
{
  "success": true,
  "message": "주문이 완료되었습니다.",
  "data": {
    "orderId": 10,
    "productId": 1,
    "productName": "무농약 청상추",
    "quantity": 2,
    "totalPrice": 7800,
    "status": "COMPLETED",
    "orderDate": "2026-05-22T11:30:00"
  }
}
```

---

### 6.4.2 내 주문 내역 조회

| 항목 | 내용 |
|---|---|
| Method | GET |
| URI | `/api/v1/orders/my?page=0&size=10` |
| 설명 | 구매자가 자신의 주문 내역 조회 |
| 권한 | BUYER |
| 관련 테이블 | `orders`, `products` |

---

### 6.4.3 주문 상세 조회

| 항목 | 내용 |
|---|---|
| Method | GET |
| URI | `/api/v1/orders/{orderId}` |
| 설명 | 주문 ID 기준 상세 조회 |
| 권한 | BUYER |
| 관련 테이블 | `orders`, `products` |

---

### 6.4.4 판매 내역 조회

| 항목 | 내용 |
|---|---|
| Method | GET |
| URI | `/api/v1/seller/orders?page=0&size=10` |
| 설명 | 판매자가 본인 상품에 대한 주문 내역 조회 |
| 권한 | SELLER |
| 관련 테이블 | `orders`, `products`, `users` |

---

## 6.5 Review API

### 6.5.1 리뷰 작성

| 항목 | 내용 |
|---|---|
| Method | POST |
| URI | `/api/v1/reviews` |
| 설명 | 구매 완료된 주문에 대해 리뷰 작성 |
| 권한 | BUYER |
| 관련 테이블 | `reviews`, `orders` |

#### Request Body

```json
{
  "orderId": 10,
  "rating": 5,
  "content": "상추가 정말 신선하고 배송도 빨랐어요."
}
```

#### 처리 규칙

| 규칙 | 설명 |
|---|---|
| 구매 여부 확인 | 로그인한 사용자의 주문인지 확인 |
| 주문 상태 확인 | 주문 상태가 `COMPLETED`인지 확인 |
| 중복 리뷰 방지 | 하나의 주문에는 하나의 리뷰만 작성 가능 |
| 평점 범위 | 1~5 사이의 정수만 허용 |

#### Response Body

```json
{
  "success": true,
  "message": "리뷰가 작성되었습니다.",
  "data": {
    "reviewId": 3,
    "orderId": 10,
    "rating": 5,
    "content": "상추가 정말 신선하고 배송도 빨랐어요.",
    "createdAt": "2026-05-22T12:00:00"
  }
}
```

---

### 6.5.2 상품별 리뷰 목록 조회

| 항목 | 내용 |
|---|---|
| Method | GET |
| URI | `/api/v1/products/{productId}/reviews?page=0&size=10` |
| 설명 | 상품 상세 화면에서 리뷰 목록 조회 |
| 권한 | PUBLIC |
| 관련 테이블 | `reviews`, `orders`, `users` |

---

### 6.5.3 리뷰 수정

| 항목 | 내용 |
|---|---|
| Method | PUT |
| URI | `/api/v1/reviews/{reviewId}` |
| 설명 | 리뷰 작성자가 본인 리뷰 수정 |
| 권한 | BUYER |
| 관련 테이블 | `reviews` |

#### Request Body

```json
{
  "rating": 4,
  "content": "상품은 신선했지만 포장이 조금 아쉬웠어요."
}
```

---

### 6.5.4 리뷰 삭제

| 항목 | 내용 |
|---|---|
| Method | DELETE |
| URI | `/api/v1/reviews/{reviewId}` |
| 설명 | 리뷰 작성자가 본인 리뷰 삭제 |
| 권한 | BUYER |
| 관련 테이블 | `reviews` |

---

## 6.6 Behavior Log API

### 6.6.1 행동 로그 저장

| 항목 | 내용 |
|---|---|
| Method | POST |
| URI | `/api/v1/logs` |
| 설명 | Vue 화면에서 발생한 사용자 행동 이벤트를 MySQL에 저장 |
| 권한 | PUBLIC / USER |
| 관련 테이블 | `behavior_logs` |

#### Request Body

```json
{
  "sessionId": "sess_abc123",
  "eventType": "click_product",
  "productId": 1,
  "abTestGroup": "B_GROUP",
  "deviceType": "PC_WEB",
  "stayDuration": 35
}
```

#### 이벤트 타입

| eventType | 설명 |
|---|---|
| view_home | 홈 화면 방문 |
| click_product | 상품 카드 클릭 |
| view_detail | 상품 상세 조회 |
| click_checkout | 주문 버튼 클릭 |
| complete_order | 주문 완료 |

#### Response Body

```json
{
  "success": true,
  "message": "행동 로그가 저장되었습니다.",
  "data": {
    "logId": 1001
  }
}
```

---

### 6.6.2 내 행동 로그 조회

| 항목 | 내용 |
|---|---|
| Method | GET |
| URI | `/api/v1/logs/my` |
| 설명 | 로그인한 사용자의 행동 로그 조회 |
| 권한 | USER |
| 관련 테이블 | `behavior_logs` |

---

## 6.7 Analytics API

### 6.7.1 퍼널 전환율 조회

| 항목 | 내용 |
|---|---|
| Method | GET |
| URI | `/api/v1/analytics/funnel?startDate=2026-05-01&endDate=2026-05-22` |
| 설명 | 홈 방문부터 주문 완료까지 단계별 전환율 조회 |
| 권한 | SELLER |
| 관련 테이블 | `behavior_logs` |

#### Response Body

```json
{
  "success": true,
  "message": "퍼널 전환율을 조회했습니다.",
  "data": {
    "steps": [
      {
        "eventType": "view_home",
        "count": 10000,
        "conversionRate": 100.0
      },
      {
        "eventType": "click_product",
        "count": 6500,
        "conversionRate": 65.0
      },
      {
        "eventType": "view_detail",
        "count": 4200,
        "conversionRate": 42.0
      },
      {
        "eventType": "click_checkout",
        "count": 1800,
        "conversionRate": 18.0
      },
      {
        "eventType": "complete_order",
        "count": 1080,
        "conversionRate": 10.8
      }
    ]
  }
}
```

---

### 6.7.2 A/B 테스트 결과 조회

| 항목 | 내용 |
|---|---|
| Method | GET |
| URI | `/api/v1/analytics/ab-test?startDate=2026-05-01&endDate=2026-05-22` |
| 설명 | A/B 그룹별 전환 성과 조회 |
| 권한 | SELLER |
| 관련 테이블 | `behavior_logs`, `orders` |

#### Response Body

```json
{
  "success": true,
  "message": "A/B 테스트 결과를 조회했습니다.",
  "data": {
    "groups": [
      {
        "group": "A_GROUP",
        "viewCount": 5000,
        "orderCount": 210,
        "conversionRate": 4.2
      },
      {
        "group": "B_GROUP",
        "viewCount": 5200,
        "orderCount": 302,
        "conversionRate": 5.81
      }
    ]
  }
}
```

---

### 6.7.3 상품별 판매 지표 조회

| 항목 | 내용 |
|---|---|
| Method | GET |
| URI | `/api/v1/analytics/sales-summary?startDate=2026-05-01&endDate=2026-05-22` |
| 설명 | 판매자 상품별 주문 수량, 매출, 리뷰 수, 평균 평점 조회 |
| 권한 | SELLER |
| 관련 테이블 | `orders`, `products`, `reviews` |

---

### 6.7.4 판매자 대시보드 요약 지표 조회

| 항목 | 내용 |
|---|---|
| Method | GET |
| URI | `/api/v1/analytics/dashboard-summary` |
| 설명 | 오늘 매출, 주문 수, 전환율, 폐기 위험 상품 수 조회 |
| 권한 | SELLER |
| 관련 테이블 | `orders`, `products`, `behavior_logs`, `demand_forecasts` |

---

### 6.7.5 수요 예측 결과 조회

| 항목 | 내용 |
|---|---|
| Method | GET |
| URI | `/api/v1/analytics/demand-forecast?productId=1` |
| 설명 | 상품별 수요 예측 결과 조회 |
| 권한 | SELLER |
| 관련 테이블 | `demand_forecasts`, `products` |

---

### 6.7.6 폐기 위험 상품 조회

| 항목 | 내용 |
|---|---|
| Method | GET |
| URI | `/api/v1/analytics/spoilage-risk` |
| 설명 | 폐기 위험도가 높은 상품 목록 조회 |
| 권한 | SELLER |
| 관련 테이블 | `demand_forecasts`, `products` |

---

## 6.8 Recommendation API

### 6.8.1 소비자 맞춤 상품 추천

| 항목 | 내용 |
|---|---|
| Method | GET |
| URI | `/api/v1/recommendations/products` |
| 설명 | 로그인한 사용자의 행동 로그와 주문 이력 기반 맞춤 상품 추천 |
| 권한 | BUYER |
| 관련 테이블 | `recommendation_results`, `behavior_logs`, `orders`, `products` |

#### Response Body

```json
{
  "success": true,
  "message": "맞춤 상품 추천 결과를 조회했습니다.",
  "data": [
    {
      "productId": 3,
      "name": "새벽 딸기",
      "price": 12900,
      "thumbnailUrl": "https://cdn.example.com/strawberry.png",
      "recommendReason": "최근 과일 카테고리를 자주 조회했습니다.",
      "score": 0.92
    }
  ]
}
```

---

### 6.8.2 인기 상품 추천

| 항목 | 내용 |
|---|---|
| Method | GET |
| URI | `/api/v1/recommendations/popular` |
| 설명 | 주문 수, 조회 수 기준 인기 상품 추천 |
| 권한 | PUBLIC |
| 관련 테이블 | `behavior_logs`, `orders`, `products` |

---

# 7. 화면별 API 매핑

| 화면 | 사용자 유형 | 사용 API |
|---|---|---|
| 홈 화면 | 소비자 | `GET /api/v1/products`, `POST /api/v1/logs`, `GET /api/v1/recommendations/popular` |
| 상품 상세 화면 | 소비자 | `GET /api/v1/products/{productId}`, `GET /api/v1/products/{productId}/reviews`, `POST /api/v1/logs` |
| 주문 완료 화면 | 소비자 | `POST /api/v1/orders`, `POST /api/v1/logs` |
| 마이페이지 | 소비자 | `GET /api/v1/users/me`, `GET /api/v1/orders/my`, `POST /api/v1/reviews` |
| 추천 상품 영역 | 소비자 | `GET /api/v1/recommendations/products`, `GET /api/v1/recommendations/popular` |
| 판매자 상품 관리 화면 | 판매자 | `GET /api/v1/seller/products`, `POST /api/v1/products`, `PUT /api/v1/products/{productId}`, `DELETE /api/v1/products/{productId}` |
| 판매 내역 화면 | 판매자 | `GET /api/v1/seller/orders`, `GET /api/v1/analytics/sales-summary` |
| 판매자 대시보드 | 판매자 | `GET /api/v1/analytics/dashboard-summary`, `GET /api/v1/analytics/funnel`, `GET /api/v1/analytics/ab-test`, `GET /api/v1/analytics/demand-forecast`, `GET /api/v1/analytics/spoilage-risk` |
| Streamlit 분석 대시보드 | 관리자/분석 | MySQL 데이터 직접 조회 또는 Analytics API 활용 |

---

# 8. MySQL 테이블 매핑

| API 그룹 | 주요 테이블 |
|---|---|
| Auth / User | `users` |
| Product | `products`, `reviews` |
| Order | `orders`, `products` |
| Review | `reviews`, `orders`, `users` |
| Behavior Log | `behavior_logs` |
| Analytics | `behavior_logs`, `orders`, `products`, `reviews`, `demand_forecasts` |
| Recommendation | `recommendation_results`, `behavior_logs`, `orders`, `products` |
| External Data | `raw_price_data`, `raw_weather_data`, `raw_calendar_data`, `raw_search_trend_data` |

---

# 9. 공통 에러 코드

| 에러 코드 | 설명 | HTTP 상태 코드 |
|---|---|---|
| INVALID_INPUT | 입력값이 올바르지 않음 | 400 |
| UNAUTHORIZED | 인증이 필요함 | 401 |
| FORBIDDEN | 접근 권한이 없음 | 403 |
| USER_NOT_FOUND | 사용자를 찾을 수 없음 | 404 |
| PRODUCT_NOT_FOUND | 상품을 찾을 수 없음 | 404 |
| ORDER_NOT_FOUND | 주문을 찾을 수 없음 | 404 |
| REVIEW_NOT_FOUND | 리뷰를 찾을 수 없음 | 404 |
| DUPLICATED_EMAIL | 중복된 이메일 | 409 |
| DUPLICATED_REVIEW | 이미 리뷰를 작성한 주문 | 409 |
| OUT_OF_STOCK | 재고 부족 | 400 |
| INTERNAL_SERVER_ERROR | 서버 내부 오류 | 500 |

---

# 10. Swagger 문서화 계획

Swagger/OpenAPI를 활용하여 다음 내용을 자동 문서화한다.

| 항목 | 설명 |
|---|---|
| API 그룹 | Auth, User, Product, Order, Review, Log, Analytics, Recommendation |
| 요청 파라미터 | Path Variable, Query Parameter, Request Body |
| 응답 구조 | 공통 응답 형식 |
| 에러 응답 | 공통 에러 응답 형식 |
| 인증 정보 | Authorization Header |
| 테스트 | Swagger UI에서 API 직접 테스트 가능 |

Swagger 접속 경로는 다음과 같이 설정한다.

```text
http://localhost:8080/swagger-ui.html
```

또는 SpringDoc 설정에 따라 다음 경로를 사용할 수 있다.

```text
http://localhost:8080/swagger-ui/index.html
```

---

# 11. 비고

- 본 API 설계서는 초기 제출 기준이며, 구현 과정에서 URI와 요청/응답 필드는 일부 조정될 수 있다.
- 초기 제출 범위에서는 MySQL만 사용한다.
- 행동 로그, 분석 결과, AI 결과도 MySQL 테이블에 저장한다.
- MongoDB와 Kafka는 초기 구현 범위에서 제외하고, 추후 대용량 로그 처리 또는 확장 구조가 필요한 경우 도입을 검토한다.
- 인증은 설계상 JWT를 기준으로 작성했지만, 시간 제약이 있는 경우 세션 기반 로그인 또는 Mock 인증 방식으로 단순화할 수 있다.

---

# 12. ERD 및 테이블 구조 설계

## 12.1 ERD 설계 기준

FreshGrowth의 데이터는 초기 제출 범위에서 모두 **MySQL**에 저장한다.  
회원, 상품, 주문, 리뷰는 기본 서비스 운영 데이터이며, 행동 로그와 AI 분석 결과 역시 MySQL 테이블로 관리한다.

```text
┌──────────────────────┐
│        users         │
├──────────────────────┤
│ user_id        PK    │
│ role                 │
│ email                │
│ password             │
│ name                 │
│ status               │
│ created_at           │
└──────────┬───────────┘
           │ 1
           │
           │ N
┌──────────▼───────────┐
│      products        │
├──────────────────────┤
│ product_id     PK    │
│ seller_id      FK    │
│ name                 │
│ description          │
│ category             │
│ price                │
│ stock_qty            │
│ thumbnail_url        │
│ expiration_date      │
│ ab_variant           │
│ created_at           │
│ updated_at           │
└──────────┬───────────┘
           │ 1
           │
           │ N
┌──────────▼───────────┐
│       orders         │
├──────────────────────┤
│ order_id       PK    │
│ buyer_id       FK    │
│ product_id     FK    │
│ quantity             │
│ total_price          │
│ status               │
│ order_date           │
└──────────┬───────────┘
           │ 1
           │
           │ 0..1
┌──────────▼───────────┐
│       reviews        │
├──────────────────────┤
│ review_id      PK    │
│ order_id       FK    │
│ rating               │
│ content              │
│ created_at           │
│ updated_at           │
└──────────────────────┘


┌──────────────────────┐
│    behavior_logs     │
├──────────────────────┤
│ log_id         PK    │
│ user_id        FK    │
│ session_id           │
│ event_type           │
│ product_id     FK    │
│ ab_test_group        │
│ device_type          │
│ stay_duration        │
│ created_at           │
└──────────────────────┘


┌──────────────────────┐
│   demand_forecasts   │
├──────────────────────┤
│ forecast_id    PK    │
│ product_id     FK    │
│ forecast_date        │
│ predicted_qty        │
│ spoilage_risk        │
│ created_at           │
└──────────────────────┘


┌──────────────────────────┐
│ recommendation_results   │
├──────────────────────────┤
│ recommendation_id  PK    │
│ user_id            FK    │
│ product_id         FK    │
│ score                    │
│ recommend_reason         │
│ created_at               │
└──────────────────────────┘
```

---

## 12.2 핵심 테이블 관계

| 관계 | 설명 |
|---|---|
| `users` 1 : N `products` | 판매자 한 명은 여러 상품을 등록할 수 있다. |
| `users` 1 : N `orders` | 구매자 한 명은 여러 주문을 생성할 수 있다. |
| `products` 1 : N `orders` | 하나의 상품은 여러 번 주문될 수 있다. |
| `orders` 1 : 0..1 `reviews` | 하나의 주문에는 최대 하나의 리뷰만 작성할 수 있다. |
| `users` 1 : N `behavior_logs` | 로그인 사용자의 행동 로그를 사용자 기준으로 저장할 수 있다. |
| `products` 1 : N `behavior_logs` | 특정 상품 클릭, 상세 조회, 주문 이벤트를 상품 기준으로 추적할 수 있다. |
| `products` 1 : N `demand_forecasts` | 상품별 날짜 단위 수요 예측 결과를 저장한다. |
| `users` 1 : N `recommendation_results` | 사용자별 개인화 추천 결과를 저장한다. |
| `products` 1 : N `recommendation_results` | 추천된 상품과 추천 점수를 저장한다. |

---

## 12.3 테이블 정의서

### 12.3.1 users

| 컬럼명 | 타입 | 제약조건 | 설명 |
|---|---|---|---|
| user_id | BIGINT | PK, AUTO_INCREMENT | 회원 ID |
| role | VARCHAR(10) | NOT NULL | `BUYER`, `SELLER` |
| email | VARCHAR(100) | NOT NULL, UNIQUE | 로그인 이메일 |
| password | VARCHAR(255) | NOT NULL | 암호화된 비밀번호 |
| name | VARCHAR(50) | NOT NULL | 회원 이름 |
| status | VARCHAR(20) | NOT NULL, DEFAULT `ACTIVE` | 회원 상태 |
| created_at | DATETIME | NOT NULL | 가입 일시 |

---

### 12.3.2 products

| 컬럼명 | 타입 | 제약조건 | 설명 |
|---|---|---|---|
| product_id | BIGINT | PK, AUTO_INCREMENT | 상품 ID |
| seller_id | BIGINT | FK, NOT NULL | 판매자 ID |
| name | VARCHAR(100) | NOT NULL | 상품명 |
| description | TEXT | NULL | 상품 설명 |
| category | VARCHAR(50) | NULL | 상품 카테고리 |
| price | INT | NOT NULL | 상품 가격 |
| stock_qty | INT | NOT NULL | 재고 수량 |
| thumbnail_url | VARCHAR(500) | NULL | 썸네일 이미지 URL |
| expiration_date | DATE | NULL | 유통기한 |
| ab_variant | VARCHAR(10) | NULL | A/B 테스트 그룹 |
| created_at | DATETIME | NOT NULL | 등록 일시 |
| updated_at | DATETIME | NOT NULL | 수정 일시 |

---

### 12.3.3 orders

| 컬럼명 | 타입 | 제약조건 | 설명 |
|---|---|---|---|
| order_id | BIGINT | PK, AUTO_INCREMENT | 주문 ID |
| buyer_id | BIGINT | FK, NOT NULL | 구매자 ID |
| product_id | BIGINT | FK, NOT NULL | 상품 ID |
| quantity | INT | NOT NULL | 주문 수량 |
| total_price | INT | NOT NULL | 총 주문 금액 |
| status | VARCHAR(20) | NOT NULL | 주문 상태, 기본값 `COMPLETED` |
| order_date | DATETIME | NOT NULL | 주문 일시 |

---

### 12.3.4 reviews

| 컬럼명 | 타입 | 제약조건 | 설명 |
|---|---|---|---|
| review_id | BIGINT | PK, AUTO_INCREMENT | 리뷰 ID |
| order_id | BIGINT | FK, UNIQUE, NOT NULL | 주문 ID |
| rating | INT | NOT NULL | 평점, 1~5 |
| content | TEXT | NULL | 리뷰 내용 |
| created_at | DATETIME | NOT NULL | 작성 일시 |
| updated_at | DATETIME | NULL | 수정 일시 |

---

### 12.3.5 behavior_logs

| 컬럼명 | 타입 | 제약조건 | 설명 |
|---|---|---|---|
| log_id | BIGINT | PK, AUTO_INCREMENT | 로그 ID |
| user_id | BIGINT | FK, NULL | 회원 ID, 비로그인 사용자는 NULL |
| session_id | VARCHAR(100) | NOT NULL | 방문 세션 ID |
| event_type | VARCHAR(50) | NOT NULL | `view_home`, `click_product`, `view_detail`, `click_checkout`, `complete_order` |
| product_id | BIGINT | FK, NULL | 이벤트 대상 상품 ID |
| ab_test_group | VARCHAR(20) | NULL | `A_GROUP`, `B_GROUP` |
| device_type | VARCHAR(20) | NULL | `PC_WEB`, `MOBILE_WEB` |
| stay_duration | INT | NULL | 체류 시간, 초 단위 |
| created_at | DATETIME | NOT NULL | 이벤트 발생 일시 |

---

### 12.3.6 demand_forecasts

| 컬럼명 | 타입 | 제약조건 | 설명 |
|---|---|---|---|
| forecast_id | BIGINT | PK, AUTO_INCREMENT | 예측 결과 ID |
| product_id | BIGINT | FK, NOT NULL | 상품 ID |
| forecast_date | DATE | NOT NULL | 예측 대상 날짜 |
| predicted_qty | INT | NOT NULL | 예측 수요량 |
| spoilage_risk | VARCHAR(20) | NOT NULL | `LOW`, `MEDIUM`, `HIGH` |
| created_at | DATETIME | NOT NULL | 예측 생성 일시 |

---

### 12.3.7 recommendation_results

| 컬럼명 | 타입 | 제약조건 | 설명 |
|---|---|---|---|
| recommendation_id | BIGINT | PK, AUTO_INCREMENT | 추천 결과 ID |
| user_id | BIGINT | FK, NOT NULL | 추천 대상 사용자 ID |
| product_id | BIGINT | FK, NOT NULL | 추천 상품 ID |
| score | DECIMAL(5, 4) | NULL | 추천 점수 |
| recommend_reason | VARCHAR(255) | NULL | 추천 사유 |
| created_at | DATETIME | NOT NULL | 추천 생성 일시 |

---

## 12.4 DDL 예시

```sql
CREATE TABLE users (
    user_id BIGINT NOT NULL AUTO_INCREMENT,
    role VARCHAR(10) NOT NULL COMMENT 'BUYER | SELLER',
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id)
);

CREATE TABLE products (
    product_id BIGINT NOT NULL AUTO_INCREMENT,
    seller_id BIGINT NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    category VARCHAR(50),
    price INT NOT NULL,
    stock_qty INT NOT NULL DEFAULT 0,
    thumbnail_url VARCHAR(500),
    expiration_date DATE,
    ab_variant VARCHAR(10) COMMENT 'A | B',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (product_id),
    FOREIGN KEY (seller_id) REFERENCES users(user_id)
);

CREATE TABLE orders (
    order_id BIGINT NOT NULL AUTO_INCREMENT,
    buyer_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    total_price INT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'COMPLETED',
    order_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (order_id),
    FOREIGN KEY (buyer_id) REFERENCES users(user_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE reviews (
    review_id BIGINT NOT NULL AUTO_INCREMENT,
    order_id BIGINT NOT NULL UNIQUE,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    content TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME,
    PRIMARY KEY (review_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

CREATE TABLE behavior_logs (
    log_id BIGINT NOT NULL AUTO_INCREMENT,
    user_id BIGINT NULL,
    session_id VARCHAR(100) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    product_id BIGINT NULL,
    ab_test_group VARCHAR(20),
    device_type VARCHAR(20),
    stay_duration INT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (log_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE demand_forecasts (
    forecast_id BIGINT NOT NULL AUTO_INCREMENT,
    product_id BIGINT NOT NULL,
    forecast_date DATE NOT NULL,
    predicted_qty INT NOT NULL,
    spoilage_risk VARCHAR(20) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (forecast_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE recommendation_results (
    recommendation_id BIGINT NOT NULL AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    score DECIMAL(5, 4),
    recommend_reason VARCHAR(255),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (recommendation_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
```

---

# 13. 계층 구조 설명

## 13.1 전체 계층 구조

FreshGrowth 백엔드는 Spring Boot 기반 REST API 서버로 구현하며, View 템플릿을 사용하지 않고 Vue 프론트엔드와 JSON으로 통신한다.

```text
Vue Frontend
    │
    │ HTTP Request / Response(JSON)
    ▼
Controller
    │
    │ DTO 전달
    ▼
Service
    │
    │ 비즈니스 로직 처리
    ▼
Mapper Interface
    │
    │ MyBatis 호출
    ▼
Mapper XML
    │
    │ SQL 실행
    ▼
MySQL
```

---

## 13.2 계층별 역할

| 계층 | 역할 | 예시 |
|---|---|---|
| Controller | REST API 엔드포인트를 정의하고 요청/응답을 처리한다. | `ProductController`, `OrderController` |
| Service | 비즈니스 로직, 트랜잭션, 권한 검증, 데이터 조합을 담당한다. | `ProductService`, `OrderService` |
| Mapper Interface | Service에서 호출하는 DB 접근 메서드를 정의한다. | `ProductMapper`, `OrderMapper` |
| Mapper XML | 실제 SQL 쿼리를 작성하고 파라미터/결과 매핑을 정의한다. | `ProductMapper.xml` |
| DTO | API 요청/응답 전용 객체로 사용한다. | `ProductCreateRequest`, `ProductResponse` |
| Domain | DB 테이블과 매핑되는 데이터 객체로 사용한다. | `Product`, `Order` |
| Global | 예외 처리, CORS, Swagger, 인증 설정 등 공통 기능을 담당한다. | `GlobalExceptionHandler`, `SwaggerConfig` |

---

## 13.3 도메인별 패키지 구조

```text
backend/src/main/java/com/freshgrowth/
├── domain/
│   ├── user/
│   │   ├── domain/
│   │   │   └── User.java
│   │   ├── dto/
│   │   │   ├── SignupRequest.java
│   │   │   ├── LoginRequest.java
│   │   │   └── UserResponse.java
│   │   ├── mapper/
│   │   │   └── UserMapper.java
│   │   ├── service/
│   │   │   └── UserService.java
│   │   └── controller/
│   │       └── UserController.java
│   │
│   ├── product/
│   │   ├── domain/
│   │   │   └── Product.java
│   │   ├── dto/
│   │   │   ├── ProductCreateRequest.java
│   │   │   ├── ProductUpdateRequest.java
│   │   │   └── ProductResponse.java
│   │   ├── mapper/
│   │   │   └── ProductMapper.java
│   │   ├── service/
│   │   │   └── ProductService.java
│   │   └── controller/
│   │       └── ProductController.java
│   │
│   ├── order/
│   ├── review/
│   ├── log/
│   ├── analytics/
│   └── recommendation/
│
└── global/
    ├── config/
    │   ├── SwaggerConfig.java
    │   ├── WebConfig.java
    │   └── SecurityConfig.java
    ├── exception/
    │   ├── GlobalExceptionHandler.java
    │   └── ErrorCode.java
    └── response/
        └── ApiResponse.java
```

---

## 13.4 Mapper XML 구조

MyBatis는 Mapper Interface와 Mapper XML을 연결하여 SQL을 실행한다.  
Mapper XML은 `src/main/resources/mapper/` 하위에 위치한다.

```text
backend/src/main/resources/mapper/
├── UserMapper.xml
├── ProductMapper.xml
├── OrderMapper.xml
├── ReviewMapper.xml
├── BehaviorLogMapper.xml
├── AnalyticsMapper.xml
└── RecommendationMapper.xml
```

---

## 13.5 요청 처리 흐름 예시

### 상품 목록 조회

```text
1. Vue 홈 화면에서 상품 목록 요청
2. GET /api/v1/products?page=0&size=10
3. ProductController가 요청 파라미터 수신
4. ProductService가 page, size를 offset으로 변환
5. ProductMapper.selectProducts() 호출
6. ProductMapper.xml의 SELECT SQL 실행
7. MySQL products 테이블 조회
8. ProductResponse 목록 반환
9. Controller가 공통 응답 형식으로 JSON 반환
```

### 주문 생성

```text
1. Vue 상품 상세 화면에서 주문하기 클릭
2. POST /api/v1/orders 요청
3. OrderController가 productId, quantity 수신
4. OrderService가 상품 존재 여부와 재고 확인
5. 재고가 충분하면 orders INSERT
6. products.stock_qty 차감 UPDATE
7. behavior_logs에 complete_order 이벤트 저장
8. 주문 결과를 OrderResponse로 반환
```

---

## 13.6 트랜잭션 적용 기준

| 기능 | 트랜잭션 필요 여부 | 이유 |
|---|---|---|
| 회원가입 | 필요 | 회원 정보 저장 중 오류 발생 시 롤백 |
| 상품 등록/수정/삭제 | 필요 | 상품 데이터 변경 |
| 주문 생성 | 필요 | 주문 저장과 재고 차감이 함께 처리되어야 함 |
| 리뷰 작성 | 필요 | 중복 리뷰 검증 후 리뷰 저장 |
| 행동 로그 저장 | 선택 | 로그 저장 실패가 핵심 주문 기능을 막지 않도록 분리 가능 |
| 분석 조회 | 불필요 | 조회 전용 기능 |

---

## 13.7 MyBatis 사용 기준

| 항목 | 적용 방식 |
|---|---|
| 단순 CRUD | Mapper XML에 기본 `SELECT`, `INSERT`, `UPDATE`, `DELETE` 작성 |
| 페이지네이션 | `LIMIT #{size} OFFSET #{offset}` 사용 |
| 조건 검색 | `<where>`, `<if>` 동적 SQL 사용 |
| 판매자별 집계 | `GROUP BY`, `SUM`, `COUNT` 사용 |
| 퍼널 분석 | `behavior_logs`의 `event_type`, `session_id` 기준 집계 |
| A/B 테스트 | `ab_test_group` 기준 전환율 계산 |
| 추천 결과 조회 | `recommendation_results`와 `products` JOIN |

---

## 13.8 제출 범위 기준

초기 제출 범위에서는 다음 계층과 산출물을 우선 구현한다.

```text
Controller
Service
Mapper Interface
Mapper XML
Domain
DTO
GlobalExceptionHandler
SwaggerConfig
README.md
requirements.md
api-spec.md
ERD 및 계층 구조 설명
```

MongoDB와 Kafka는 초기 구현 범위에서 제외하며, 행동 로그와 AI 결과는 MySQL 테이블로 관리한다.
