# ── 빌드 스테이지 (JDK 21로 빌드; 소스 타겟 17이라 호환) ──────────────
FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /app

# 의존성 먼저 받아 레이어 캐시 (pom 안 바뀌면 재다운로드 안 함)
COPY pom.xml .
RUN mvn -B -q dependency:go-offline

COPY src ./src
RUN mvn -B -q clean package -DskipTests

# ── 실행 스테이지 ────────────────────────────────────────────────
# 반드시 Java 21. Java 25에서는 SB 3.3.5 + jjwt 0.12.6 nested-jar
# ServiceLoader가 깨져 로그인 시 ServiceConfigurationError 발생. (docs/트러블슈팅.md 1번)
FROM eclipse-temurin:21-jre
WORKDIR /app

COPY --from=build /app/target/freshgrowth-backend-0.0.1-SNAPSHOT.jar app.jar

EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
