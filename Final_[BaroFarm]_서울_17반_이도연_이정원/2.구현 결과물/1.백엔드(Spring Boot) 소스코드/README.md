# FreshGrowth Backend - Maven Basic CRUD

이 프로젝트는 STS에서 열기 쉬운 **Maven 기반 Spring Boot 프로젝트**입니다.

## 기술 스택

- Java 17
- Spring Boot 3.3.5
- Maven
- MyBatis
- MySQL
- Swagger

## 구현 범위

진짜 기본 CRUD 중심으로만 구현했습니다.

- 회원가입 / 로그인 / 내 정보 조회 / 회원 비활성화
- 상품 등록 / 목록 조회 / 상세 조회 / 수정 / 삭제
- 주문 생성 / 내 주문 조회 / 판매자 주문 조회
- 리뷰 작성 / 상품별 리뷰 조회 / 수정 / 삭제
- Swagger
- CORS
- 공통 응답 / 공통 예외 처리

## STS 실행 순서

### 1. MySQL DB 생성

```sql
CREATE DATABASE freshgrowth CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. 테이블 생성

`src/main/resources/schema.sql` 내용을 MySQL Workbench에서 실행하세요.

### 3. DB 계정 수정

`src/main/resources/application.yml`에서 본인 MySQL 비밀번호로 바꾸세요.

```yaml
spring:
  datasource:
    username: root
    password: 1234
```

### 4. STS에서 Import

```text
File > Import > Maven > Existing Maven Projects
```

이 프로젝트 폴더를 선택하세요.

### 5. 실행

`FreshGrowthApplication.java` 우클릭 후 `Run As > Spring Boot App`

### 6. Swagger 접속

```text
http://localhost:8080/swagger-ui.html
```

## 테스트용 샘플 계정

schema.sql 실행 시 자동 생성됩니다.

| 역할 | userId | email | password |
|---|---:|---|---|
| 판매자 | 1 | seller@example.com | 1234 |
| 구매자 | 2 | buyer@example.com | 1234 |

## 헤더 사용법

아직 JWT는 구현하지 않았습니다.  
테스트용으로 `X-USER-ID` 헤더를 사용합니다.

판매자 API:

```http
X-USER-ID: 1
```

구매자 API:

```http
X-USER-ID: 2
```

## 가장 먼저 테스트할 API

```http
GET http://localhost:8080/api/v1/products
```

이 응답이 오면 DB 연결과 MyBatis 설정은 정상입니다.
