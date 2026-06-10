package com.freshgrowth.user;

import com.freshgrowth.common.AppException;
import com.freshgrowth.common.auth.JwtProvider;
import com.freshgrowth.user.dto.LoginRequest;
import com.freshgrowth.user.dto.LoginResponse;
import com.freshgrowth.user.dto.SignupRequest;
import com.freshgrowth.user.dto.UserResponse;
import org.springframework.http.HttpStatus;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class UserService {
    private final UserMapper userMapper;
    private final JwtProvider jwtProvider;
    private final BCryptPasswordEncoder passwordEncoder = new BCryptPasswordEncoder();

    public UserService(UserMapper userMapper, JwtProvider jwtProvider) {
        this.userMapper = userMapper;
        this.jwtProvider = jwtProvider;
    }

    @Transactional
    public UserResponse signup(SignupRequest request) {
        if (userMapper.findByEmail(request.getEmail()) != null) {
            throw new AppException(HttpStatus.CONFLICT, "DUPLICATED_EMAIL", "이미 사용 중인 이메일입니다.");
        }
        if (userMapper.existsByName(request.getName())) {
            throw new AppException(HttpStatus.CONFLICT, "DUPLICATED_NAME", "이미 사용 중인 닉네임입니다.");
        }

        User user = new User();
        user.setEmail(request.getEmail());
        user.setPassword(passwordEncoder.encode(request.getPassword())); // BCrypt 해싱 저장
        user.setName(request.getName());
        user.setRole(request.getRole());
        user.setStatus("ACTIVE");
        userMapper.insert(user);

        return new UserResponse(userMapper.findById(user.getUserId()));
    }

    public LoginResponse login(LoginRequest request) {
        User user = userMapper.findByEmail(request.getEmail());
        if (user == null || !passwordEncoder.matches(request.getPassword(), user.getPassword())) {
            throw new AppException(HttpStatus.UNAUTHORIZED, "LOGIN_FAILED", "이메일 또는 비밀번호가 올바르지 않습니다.");
        }
        if ("INACTIVE".equals(user.getStatus())) {
            throw new AppException(HttpStatus.UNAUTHORIZED, "ACCOUNT_INACTIVE", "탈퇴하거나 비활성화된 계정입니다.");
        }
        String token = jwtProvider.generate(user.getUserId(), user.getRole());
        return new LoginResponse(token, new UserResponse(user));
    }

    @Transactional
    public UserResponse updateProfile(Long userId, com.freshgrowth.user.dto.ProfileUpdateRequest request) {
        // userId는 JWT에서 추출된 값 — 본인 프로필만 수정 가능
        User user = userMapper.findById(userId);
        if (user == null) {
            throw new AppException(HttpStatus.NOT_FOUND, "USER_NOT_FOUND", "사용자를 찾을 수 없습니다.");
        }
        // 닉네임 변경 시 타인과 중복 여부 확인
        if (request.getName() != null && !request.getName().equals(user.getName())
                && userMapper.existsByName(request.getName())) {
            throw new AppException(HttpStatus.CONFLICT, "DUPLICATED_NAME", "이미 사용 중인 닉네임입니다.");
        }
        user.setName(request.getName());
        user.setIntro(request.getIntro());
        user.setPhone(request.getPhone());
        user.setProfileImage(request.getProfileImage());
        userMapper.updateProfile(user);
        return new UserResponse(userMapper.findById(userId));
    }

    public UserResponse findMe(Long userId) {
        User user = userMapper.findById(userId);
        if (user == null) {
            throw new AppException(HttpStatus.NOT_FOUND, "USER_NOT_FOUND", "사용자를 찾을 수 없습니다.");
        }
        return new UserResponse(user);
    }

    @Transactional
    public void deactivate(Long userId, String password) {
        User user = userMapper.findById(userId);
        if (user == null) {
            throw new AppException(HttpStatus.NOT_FOUND, "USER_NOT_FOUND", "사용자를 찾을 수 없습니다.");
        }
        if (!passwordEncoder.matches(password, user.getPassword())) {
            throw new AppException(HttpStatus.UNAUTHORIZED, "WRONG_PASSWORD", "비밀번호가 올바르지 않습니다.");
        }
        userMapper.deactivate(userId);
    }
}
