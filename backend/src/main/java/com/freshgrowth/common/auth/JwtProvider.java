package com.freshgrowth.common.auth;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.util.Date;

/** JWT 발급/검증. HS256, userId(subject) + role 클레임. */
@Component
public class JwtProvider {
    private final SecretKey key;
    private final long expiryMs;

    public JwtProvider(@Value("${jwt.secret}") String secret,
                       @Value("${jwt.expiry-ms:86400000}") long expiryMs) {
        this.key = Keys.hmacShaKeyFor(secret.getBytes(StandardCharsets.UTF_8));
        this.expiryMs = expiryMs;
    }

    public String generate(Long userId, String role) {
        long now = System.currentTimeMillis();
        return Jwts.builder()
                .subject(String.valueOf(userId))
                .claim("role", role)
                .issuedAt(new Date(now))
                .expiration(new Date(now + expiryMs))
                .signWith(key)
                .compact();
    }

    public Long getUserId(String token) {
        Claims claims = Jwts.parser().verifyWith(key).build()
                .parseSignedClaims(token).getPayload();
        return Long.valueOf(claims.getSubject());
    }

    /** 토큰의 만료시각 반환 (블랙리스트 expires_at 저장용) */
    public java.time.LocalDateTime getExpiration(String token) {
        Claims claims = Jwts.parser().verifyWith(key).build()
                .parseSignedClaims(token).getPayload();
        return claims.getExpiration().toInstant()
                .atZone(java.time.ZoneId.systemDefault()).toLocalDateTime();
    }

    /** Authorization 헤더에서 userId 추출(없거나 무효면 null) — 선택적 인증용 */
    public Long optionalUserId(String authHeader) {
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            return null;
        }
        try {
            return getUserId(authHeader.substring(7));
        } catch (Exception e) {
            return null;
        }
    }
}
