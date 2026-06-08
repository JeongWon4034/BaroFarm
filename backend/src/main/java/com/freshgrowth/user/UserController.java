package com.freshgrowth.user;

import com.freshgrowth.common.ApiResponse;
import com.freshgrowth.common.auth.LoginRequired;
import com.freshgrowth.common.auth.LoginUser;
import com.freshgrowth.common.auth.TokenBlacklist;
import com.freshgrowth.user.dto.LoginRequest;
import com.freshgrowth.user.dto.ProfileUpdateRequest;
import com.freshgrowth.user.dto.SignupRequest;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1")
public class UserController {
    private final UserService userService;
    private final TokenBlacklist tokenBlacklist;

    public UserController(UserService userService, TokenBlacklist tokenBlacklist) {
        this.userService = userService;
        this.tokenBlacklist = tokenBlacklist;
    }

    @PostMapping("/auth/signup")
    public ResponseEntity<ApiResponse<?>> signup(@Valid @RequestBody SignupRequest request) {
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.ok("회원가입이 완료되었습니다.", userService.signup(request)));
    }

    @PostMapping("/auth/login")
    public ApiResponse<?> login(@Valid @RequestBody LoginRequest request) {
        return ApiResponse.ok("로그인에 성공했습니다.", userService.login(request));
    }

    // 토큰 무효화(블랙리스트 등록)
    @PostMapping("/auth/logout")
    public ApiResponse<Void> logout(@RequestHeader(value = "Authorization", required = false) String authHeader) {
        if (authHeader != null && authHeader.startsWith("Bearer ")) {
            tokenBlacklist.add(authHeader.substring(7).trim());
        }
        return ApiResponse.ok("로그아웃되었습니다.", null);
    }

    @LoginRequired
    @GetMapping("/users/me")
    public ApiResponse<?> me(@LoginUser Long userId) {
        return ApiResponse.ok("내 정보를 조회했습니다.", userService.findMe(userId));
    }

    @LoginRequired
    @PutMapping("/users/me")
    public ApiResponse<?> updateMe(@LoginUser Long userId,
                                   @Valid @RequestBody ProfileUpdateRequest request) {
        return ApiResponse.ok("프로필을 수정했습니다.", userService.updateProfile(userId, request));
    }

    @LoginRequired
    @DeleteMapping("/users/me")
    public ApiResponse<Void> deactivate(@LoginUser Long userId) {
        userService.deactivate(userId);
        return ApiResponse.ok("회원 탈퇴가 완료되었습니다.", null);
    }
}
