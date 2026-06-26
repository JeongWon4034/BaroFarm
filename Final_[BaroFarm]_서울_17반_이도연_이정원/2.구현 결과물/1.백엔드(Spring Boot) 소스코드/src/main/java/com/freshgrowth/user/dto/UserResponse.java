package com.freshgrowth.user.dto;

import com.freshgrowth.user.User;
import java.time.LocalDateTime;

public class UserResponse {
    private Long userId;
    private String email;
    private String name;
    private String role;
    private String intro;
    private String phone;
    private String profileImage;
    private String status;
    private LocalDateTime createdAt;

    public UserResponse(User user) {
        this.userId = user.getUserId();
        this.email = user.getEmail();
        this.name = user.getName();
        this.role = user.getRole();
        this.intro = user.getIntro();
        this.phone = user.getPhone();
        this.profileImage = user.getProfileImage();
        this.status = user.getStatus();
        this.createdAt = user.getCreatedAt();
    }

    public Long getUserId() { return userId; }
    public String getEmail() { return email; }
    public String getName() { return name; }
    public String getRole() { return role; }
    public String getIntro() { return intro; }
    public String getPhone() { return phone; }
    public String getProfileImage() { return profileImage; }
    public String getStatus() { return status; }
    public LocalDateTime getCreatedAt() { return createdAt; }
}
