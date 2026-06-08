package com.freshgrowth.review;

import com.freshgrowth.common.ApiResponse;
import com.freshgrowth.review.dto.ReviewRequest;
import com.freshgrowth.review.dto.ReviewUpdateRequest;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1")
public class ReviewController {
    private final ReviewService reviewService;

    public ReviewController(ReviewService reviewService) {
        this.reviewService = reviewService;
    }

    @PostMapping("/reviews")
    public ApiResponse<?> create(@Valid @RequestBody ReviewRequest request) {
        return ApiResponse.ok("리뷰가 작성되었습니다.", reviewService.create(request));
    }

    @GetMapping("/products/{productId}/reviews")
    public ApiResponse<?> findByProductId(@PathVariable Long productId) {
        return ApiResponse.ok("상품별 리뷰 목록을 조회했습니다.", reviewService.findByProductId(productId));
    }

    @PutMapping("/reviews/{reviewId}")
    public ApiResponse<?> update(@PathVariable Long reviewId,
                                 @Valid @RequestBody ReviewUpdateRequest request) {
        return ApiResponse.ok("리뷰가 수정되었습니다.", reviewService.update(reviewId, request));
    }

    @DeleteMapping("/reviews/{reviewId}")
    public ApiResponse<Void> delete(@PathVariable Long reviewId) {
        reviewService.delete(reviewId);
        return ApiResponse.ok("리뷰가 삭제되었습니다.", null);
    }
}
