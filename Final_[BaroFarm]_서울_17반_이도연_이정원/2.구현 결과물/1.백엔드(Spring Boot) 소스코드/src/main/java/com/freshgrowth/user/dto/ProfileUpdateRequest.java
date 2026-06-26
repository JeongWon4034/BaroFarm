package com.freshgrowth.user.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public class ProfileUpdateRequest {
    @NotBlank
    @Size(max = 50, message = "이름은 50자 이하여야 합니다.")
    private String name;
    @Size(max = 200, message = "소개는 200자 이하여야 합니다.")
    private String intro;
    @Size(max = 20)
    private String phone;
    private String profileImage; // base64 data URL (선택)

    public String getName() { return name; }
    public String getIntro() { return intro; }
    public String getPhone() { return phone; }
    public String getProfileImage() { return profileImage; }
}
