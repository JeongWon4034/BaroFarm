package com.freshgrowth.comment.dto;

import jakarta.validation.constraints.NotBlank;

public class CommentRequest {
    @NotBlank
    private String content;

    // 답글이면 부모 댓글 id, 일반 댓글이면 null
    private Long parentId;

    public String getContent() { return content; }
    public Long getParentId() { return parentId; }
}
