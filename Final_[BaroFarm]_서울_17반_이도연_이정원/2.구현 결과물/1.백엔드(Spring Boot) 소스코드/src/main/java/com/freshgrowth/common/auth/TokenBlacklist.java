package com.freshgrowth.common.auth;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.LocalDateTime;

/**
 * 로그아웃·탈퇴 토큰 무효화 — DB(invalidated_tokens) 기반.
 * - 재시작·다중 인스턴스에서도 무효화 이력 유지
 * - 토큰 원문 대신 SHA-256 해시만 저장
 * - 매시간 만료된 행 자동 정리 (@Scheduled)
 */
@Component
public class TokenBlacklist {

    private final JdbcTemplate jdbc;
    private final JwtProvider jwtProvider;

    public TokenBlacklist(JdbcTemplate jdbc, JwtProvider jwtProvider) {
        this.jdbc = jdbc;
        this.jwtProvider = jwtProvider;
    }

    /** 토큰을 블랙리스트에 등록 (로그아웃·탈퇴 시 호출). */
    public void add(String token) {
        String hash = sha256(token);
        LocalDateTime expiresAt = expirationOf(token);
        jdbc.update(
            "INSERT IGNORE INTO invalidated_tokens(token_hash, expires_at) VALUES (?, ?)",
            hash, expiresAt
        );
    }

    /** 토큰이 무효화 목록에 있는지 확인. */
    public boolean contains(String token) {
        String hash = sha256(token);
        Integer count = jdbc.queryForObject(
            "SELECT COUNT(*) FROM invalidated_tokens WHERE token_hash = ? AND expires_at > NOW()",
            Integer.class, hash
        );
        return count != null && count > 0;
    }

    /** 만료된 블랙리스트 항목 정리 — 매시간 실행. */
    @Scheduled(fixedRate = 3_600_000)
    public void purgeExpired() {
        int deleted = jdbc.update("DELETE FROM invalidated_tokens WHERE expires_at <= NOW()");
        if (deleted > 0) {
            System.out.printf("[TokenBlacklist] 만료 토큰 %d건 정리%n", deleted);
        }
    }

    private LocalDateTime expirationOf(String token) {
        try {
            return jwtProvider.getExpiration(token);
        } catch (Exception e) {
            // 파싱 불가 토큰이면 현재 시각 + JWT 기본 만료(24h)로 보정
            return LocalDateTime.now().plusHours(24);
        }
    }

    private static String sha256(String input) {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            byte[] bytes = md.digest(input.getBytes(StandardCharsets.UTF_8));
            StringBuilder sb = new StringBuilder();
            for (byte b : bytes) {
                sb.append(String.format("%02x", b));
            }
            return sb.toString();
        } catch (NoSuchAlgorithmException e) {
            throw new IllegalStateException("SHA-256 unavailable", e);
        }
    }
}
