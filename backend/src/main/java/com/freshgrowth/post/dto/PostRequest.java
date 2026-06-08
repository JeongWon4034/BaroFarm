package com.freshgrowth.post.dto;

import jakarta.validation.constraints.NotBlank;

public class PostRequest {
    @NotBlank
    private String title;
    @NotBlank
    private String content;

    public String getTitle() { return title; }
    public String getContent() { return content; }
}
