package com.freshgrowth.common;

import org.springframework.dao.DataIntegrityViolationException;
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

    // FK 등 DB 참조 무결성 위반(예: 작성 직전 게시글·부모 댓글이 삭제됨) → 409로 명확히 안내
    @ExceptionHandler(DataIntegrityViolationException.class)
    public ResponseEntity<ApiResponse<Void>> handleIntegrity(DataIntegrityViolationException e) {
        return ResponseEntity.status(HttpStatus.CONFLICT)
                .body(ApiResponse.fail("요청 처리에 실패했습니다.", "DATA_INTEGRITY_VIOLATION",
                        "관련 게시글이나 댓글이 변경·삭제되어 처리할 수 없어요. 새로고침 후 다시 시도해 주세요."));
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ApiResponse<Void>> handleException(Exception e) {
        return ResponseEntity.internalServerError()
                .body(ApiResponse.fail("요청 처리에 실패했습니다.", "INTERNAL_SERVER_ERROR", e.getMessage()));
    }
}
