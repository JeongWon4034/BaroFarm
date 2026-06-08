package com.freshgrowth.common.auth;

import com.freshgrowth.common.AppException;
import com.freshgrowth.user.User;
import com.freshgrowth.user.UserMapper;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Component;
import org.springframework.web.method.HandlerMethod;
import org.springframework.web.servlet.HandlerInterceptor;

/**
 * JWT 기반 인증/인가를 한곳에서 처리한다.
 * - @LoginRequired 없는 핸들러는 공개(통과)
 * - 있으면 Authorization: Bearer 토큰 검증 → 누락/위조/만료/블랙리스트면 401
 * - role 지정 시 역할 불일치면 403
 * 통과하면 userId 를 request 속성에 넣어 LoginUserArgumentResolver 가 주입한다.
 */
@Component
public class AuthInterceptor implements HandlerInterceptor {
    public static final String USER_ID_ATTR = "authUserId";

    private final UserMapper userMapper;
    private final JwtProvider jwtProvider;
    private final TokenBlacklist tokenBlacklist;

    public AuthInterceptor(UserMapper userMapper, JwtProvider jwtProvider, TokenBlacklist tokenBlacklist) {
        this.userMapper = userMapper;
        this.jwtProvider = jwtProvider;
        this.tokenBlacklist = tokenBlacklist;
    }

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) {
        if (!(handler instanceof HandlerMethod handlerMethod)) {
            return true;
        }
        LoginRequired loginRequired = handlerMethod.getMethodAnnotation(LoginRequired.class);
        if (loginRequired == null) {
            return true; // 공개 엔드포인트
        }

        String header = request.getHeader("Authorization");
        if (header == null || !header.startsWith("Bearer ")) {
            throw new AppException(HttpStatus.UNAUTHORIZED, "UNAUTHORIZED", "로그인이 필요합니다.");
        }
        String token = header.substring(7).trim();

        if (tokenBlacklist.contains(token)) {
            throw new AppException(HttpStatus.UNAUTHORIZED, "TOKEN_INVALIDATED", "로그아웃된 토큰입니다. 다시 로그인해주세요.");
        }

        Long userId;
        try {
            userId = jwtProvider.getUserId(token);
        } catch (Exception e) {
            throw new AppException(HttpStatus.UNAUTHORIZED, "UNAUTHORIZED", "유효하지 않거나 만료된 토큰입니다.");
        }

        User user = userMapper.findById(userId);
        if (user == null) {
            throw new AppException(HttpStatus.UNAUTHORIZED, "UNAUTHORIZED", "존재하지 않는 사용자입니다.");
        }

        String requiredRole = loginRequired.role();
        if (!requiredRole.isEmpty() && !requiredRole.equals(user.getRole())) {
            throw new AppException(HttpStatus.FORBIDDEN, "FORBIDDEN", "접근 권한이 없습니다.");
        }

        request.setAttribute(USER_ID_ATTR, userId);
        return true;
    }
}
