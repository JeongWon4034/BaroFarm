package com.freshgrowth.common;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.MissingRequestHeaderException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@RestControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(AppException.class)
    public ResponseEntity<ApiResponse<Void>> handleAppException(AppException e) {
        return ResponseEntity.status(e.getStatus())
                .body(ApiResponse.fail("요청 처리에 실패했습니다.", e.getCode(), e.getMessage()));
    }

    // 인증 헤더 누락 등 → 401로 일관 처리(안전망)
    @ExceptionHandler(MissingRequestHeaderException.class)
    public ResponseEntity<ApiResponse<Void>> handleMissingHeader(MissingRequestHeaderException e) {
        return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                .body(ApiResponse.fail("요청 처리에 실패했습니다.", "UNAUTHORIZED", "로그인이 필요합니다."));
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ApiResponse<Void>> handleValidation(MethodArgumentNotValidException e) {
        String detail = e.getBindingResult().getFieldErrors().stream()
                .findFirst()
                .map(error -> error.getField() + ": " + error.getDefaultMessage())
                .orElse("입력값이 올바르지 않습니다.");
        return ResponseEntity.badRequest()
                .body(ApiResponse.fail("요청 처리에 실패했습니다.", "INVALID_INPUT", detail));
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ApiResponse<Void>> handleException(Exception e) {
        return ResponseEntity.internalServerError()
                .body(ApiResponse.fail("요청 처리에 실패했습니다.", "INTERNAL_SERVER_ERROR", e.getMessage()));
    }
}
