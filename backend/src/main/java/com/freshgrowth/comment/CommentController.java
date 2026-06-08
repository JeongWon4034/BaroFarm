package com.freshgrowth.comment;

import com.freshgrowth.comment.dto.CommentRequest;
import com.freshgrowth.common.ApiResponse;
import com.freshgrowth.common.auth.LoginRequired;
import com.freshgrowth.common.auth.LoginUser;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1")
public class CommentController {
    private final CommentService commentService;

    public CommentController(CommentService commentService) {
        this.commentService = commentService;
    }

    @GetMapping("/posts/{postId}/comments")
    public ApiResponse<?> findByPost(@PathVariable Long postId) {
        return ApiResponse.ok("댓글 목록을 조회했습니다.", commentService.findByPost(postId));
    }

    @LoginRequired
    @PostMapping("/posts/{postId}/comments")
    public ApiResponse<?> create(@LoginUser Long authorId, @PathVariable Long postId,
                                 @Valid @RequestBody CommentRequest request) {
        return ApiResponse.ok("댓글이 작성되었습니다.", commentService.create(authorId, postId, request));
    }

    @LoginRequired
    @PutMapping("/comments/{commentId}")
    public ApiResponse<?> update(@LoginUser Long authorId, @PathVariable Long commentId,
                                 @Valid @RequestBody CommentRequest request) {
        return ApiResponse.ok("댓글이 수정되었습니다.", commentService.update(authorId, commentId, request));
    }

    @LoginRequired
    @DeleteMapping("/comments/{commentId}")
    public ApiResponse<Void> delete(@LoginUser Long authorId, @PathVariable Long commentId) {
        commentService.delete(authorId, commentId);
        return ApiResponse.ok("댓글이 삭제되었습니다.", null);
    }
}
