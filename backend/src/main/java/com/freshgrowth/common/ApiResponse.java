package com.freshgrowth.common;

public class ApiResponse<T> {
    private boolean success;
    private String message;
    private T data;
    private ErrorData error;

    private ApiResponse(boolean success, String message, T data, ErrorData error) {
        this.success = success;
        this.message = message;
        this.data = data;
        this.error = error;
    }

    public static <T> ApiResponse<T> ok(String message, T data) {
        return new ApiResponse<>(true, message, data, null);
    }

    public static ApiResponse<Void> fail(String message, String code, String detail) {
        return new ApiResponse<>(false, message, null, new ErrorData(code, detail));
    }

    public boolean isSuccess() { return success; }
    public String getMessage() { return message; }
    public T getData() { return data; }
    public ErrorData getError() { return error; }

    public static class ErrorData {
        private String code;
        private String detail;

        public ErrorData(String code, String detail) {
            this.code = code;
            this.detail = detail;
        }

        public String getCode() { return code; }
        public String getDetail() { return detail; }
    }
}
