package com.freshgrowth.user.dto;

import jakarta.validation.constraints.NotBlank;

public class DeactivateRequest {
    @NotBlank(message = "비밀번호를 입력하세요.")
    private String password;

    public String getPassword() { return password; }
}
