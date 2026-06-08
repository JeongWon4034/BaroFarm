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
        if (user == null || !passwordMatches(request.getPassword(), user.getPassword())) {
            throw new AppException(HttpStatus.UNAUTHORIZED, "LOGIN_FAILED", "이메일 또는 비밀번호가 올바르지 않습니다.");
        }
        String token = jwtProvider.generate(user.getUserId(), user.getRole());
        return new LoginResponse(token, new UserResponse(user));
    }

    // BCrypt 해시면 검증, 아니면(시드 평문 계정) 평문 비교로 호환
    private boolean passwordMatches(String raw, String stored) {
        if (stored == null) {
            return false;
        }
        if (stored.startsWith("$2")) {
            return passwordEncoder.matches(raw, stored);
        }
        return stored.equals(raw);
    }

    @Transactional
    public UserResponse updateProfile(Long userId, com.freshgrowth.user.dto.ProfileUpdateRequest request) {
        User user = userMapper.findById(userId);
        if (user == null) {
            throw new AppException(HttpStatus.NOT_FOUND, "USER_NOT_FOUND", "사용자를 찾을 수 없습니다.");
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
    public void deactivate(Long userId) {
        if (userMapper.deactivate(userId) == 0) {
            throw new AppException(HttpStatus.NOT_FOUND, "USER_NOT_FOUND", "사용자를 찾을 수 없습니다.");
        }
    }
}
