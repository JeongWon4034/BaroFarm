package com.freshgrowth.comment.dto;

import jakarta.validation.constraints.NotBlank;

public class CommentRequest {
    @NotBlank
    private String content;

    public String getContent() { return content; }
}
