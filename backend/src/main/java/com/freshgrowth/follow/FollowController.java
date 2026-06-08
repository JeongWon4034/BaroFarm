package com.freshgrowth.follow;

import com.freshgrowth.common.ApiResponse;
import com.freshgrowth.common.auth.LoginRequired;
import com.freshgrowth.common.auth.LoginUser;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1")
public class FollowController {
    private final FollowService followService;

    public FollowController(FollowService followService) {
        this.followService = followService;
    }

    @LoginRequired(role = "BUYER")
    @PostMapping("/follow/{sellerId}")
    public ApiResponse<?> follow(@LoginUser Long buyerId, @PathVariable Long sellerId) {
        followService.follow(buyerId, sellerId);
        return ApiResponse.ok("판매자를 팔로우했습니다.", null);
    }

    @LoginRequired(role = "BUYER")
    @DeleteMapping("/follow/{sellerId}")
    public ApiResponse<?> unfollow(@LoginUser Long buyerId, @PathVariable Long sellerId) {
        followService.unfollow(buyerId, sellerId);
        return ApiResponse.ok("팔로우를 취소했습니다.", null);
    }

    @LoginRequired(role = "BUYER")
    @GetMapping("/follow/following")
    public ApiResponse<?> following(@LoginUser Long buyerId) {
        return ApiResponse.ok("팔로우한 판매자 목록을 조회했습니다.", followService.findFollowing(buyerId));
    }

    // 판매자 공개 요약 (+ 로그인 시 내 팔로우 여부). 누구나 조회 가능.
    @GetMapping("/sellers/{sellerId}")
    public ApiResponse<?> seller(@PathVariable Long sellerId,
                                 @RequestHeader(value = "X-USER-ID", required = false) Long viewerId) {
        return ApiResponse.ok("판매자 정보를 조회했습니다.", followService.getSellerSummary(sellerId, viewerId));
    }
}
