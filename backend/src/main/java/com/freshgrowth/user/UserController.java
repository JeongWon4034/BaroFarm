package com.freshgrowth.user;

import com.freshgrowth.common.ApiResponse;
import com.freshgrowth.user.dto.LoginRequest;
import com.freshgrowth.user.dto.SignupRequest;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1")
public class UserController {
    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
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

    @PostMapping("/auth/logout")
    public ApiResponse<Void> logout() {
        return ApiResponse.ok("로그아웃되었습니다.", null);
    }

    @GetMapping("/users/me")
    public ApiResponse<?> me(@RequestHeader("X-USER-ID") Long userId) {
        return ApiResponse.ok("내 정보를 조회했습니다.", userService.findMe(userId));
    }

    @DeleteMapping("/users/me")
    public ApiResponse<Void> deactivate(@RequestHeader("X-USER-ID") Long userId) {
        userService.deactivate(userId);
        return ApiResponse.ok("회원 탈퇴가 완료되었습니다.", null);
    }
}
