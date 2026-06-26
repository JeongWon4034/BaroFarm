package com.freshgrowth.post;

import com.freshgrowth.common.ApiResponse;
import com.freshgrowth.common.auth.LoginRequired;
import com.freshgrowth.common.auth.LoginUser;
import com.freshgrowth.post.dto.PostRequest;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1")
public class PostController {
    private final PostService postService;

    public PostController(PostService postService) {
        this.postService = postService;
    }

    @GetMapping("/posts")
    public ApiResponse<?> findAll(@RequestParam(defaultValue = "0") int page,
                                  @RequestParam(defaultValue = "10") int size,
                                  @RequestParam(required = false) String keyword,
                                  @RequestParam(required = false) String sort,
                                  @RequestParam(required = false) String category) {
        return ApiResponse.ok("게시글 목록을 조회했습니다.", postService.findAll(page, size, keyword, sort, category));
    }

    @GetMapping("/posts/{postId}")
    public ApiResponse<?> findById(@PathVariable Long postId) {
        return ApiResponse.ok("게시글을 조회했습니다.", postService.findById(postId));
    }

    @LoginRequired
    @PostMapping("/posts")
    public ApiResponse<?> create(@LoginUser Long authorId, @Valid @RequestBody PostRequest request) {
        return ApiResponse.ok("게시글이 작성되었습니다.", postService.create(authorId, request));
    }

    @LoginRequired
    @PutMapping("/posts/{postId}")
    public ApiResponse<?> update(@LoginUser Long authorId, @PathVariable Long postId,
                                 @Valid @RequestBody PostRequest request) {
        return ApiResponse.ok("게시글이 수정되었습니다.", postService.update(authorId, postId, request));
    }

    @LoginRequired
    @DeleteMapping("/posts/{postId}")
    public ApiResponse<Void> delete(@LoginUser Long authorId, @PathVariable Long postId) {
        postService.delete(authorId, postId);
        return ApiResponse.ok("게시글이 삭제되었습니다.", null);
    }
}
