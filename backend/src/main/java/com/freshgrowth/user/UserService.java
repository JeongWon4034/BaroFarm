package com.freshgrowth.user;

import com.freshgrowth.common.AppException;
import com.freshgrowth.user.dto.LoginRequest;
import com.freshgrowth.user.dto.SignupRequest;
import com.freshgrowth.user.dto.UserResponse;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class UserService {
    private final UserMapper userMapper;

    public UserService(UserMapper userMapper) {
        this.userMapper = userMapper;
    }

    @Transactional
    public UserResponse signup(SignupRequest request) {
        if (userMapper.findByEmail(request.getEmail()) != null) {
            throw new AppException(HttpStatus.CONFLICT, "DUPLICATED_EMAIL", "이미 사용 중인 이메일입니다.");
        }

        User user = new User();
        user.setEmail(request.getEmail());
        user.setPassword(request.getPassword());
        user.setName(request.getName());
        user.setRole(request.getRole());
        user.setStatus("ACTIVE");
        userMapper.insert(user);

        return new UserResponse(userMapper.findById(user.getUserId()));
    }

    public UserResponse login(LoginRequest request) {
        User user = userMapper.findByEmail(request.getEmail());
        if (user == null || !user.getPassword().equals(request.getPassword())) {
            throw new AppException(HttpStatus.UNAUTHORIZED, "LOGIN_FAILED", "이메일 또는 비밀번호가 올바르지 않습니다.");
        }
        return new UserResponse(user);
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
