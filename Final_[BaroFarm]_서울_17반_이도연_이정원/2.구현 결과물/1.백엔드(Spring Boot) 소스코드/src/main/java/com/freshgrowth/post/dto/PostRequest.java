package com.freshgrowth.post.dto;

import jakarta.validation.constraints.NotBlank;

public class PostRequest {
    private String category;
    @NotBlank
    private String title;
    @NotBlank
    private String content;

    public String getCategory() { return category; }
    public String getTitle() { return title; }
    public String getContent() { return content; }
}
