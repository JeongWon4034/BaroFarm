package com.freshgrowth.challenge;

import com.freshgrowth.common.ApiResponse;
import com.freshgrowth.common.auth.LoginRequired;
import com.freshgrowth.common.auth.LoginUser;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1")
public class ChallengeController {
    private final ChallengeService challengeService;

    public ChallengeController(ChallengeService challengeService) {
        this.challengeService = challengeService;
    }

    @GetMapping("/challenges")
    public ApiResponse<?> findAll() {
        return ApiResponse.ok("챌린지 목록을 조회했습니다.", challengeService.findAll());
    }

    @GetMapping("/challenges/{challengeId}")
    public ApiResponse<?> findById(@PathVariable Long challengeId) {
        return ApiResponse.ok("챌린지를 조회했습니다.", challengeService.findById(challengeId));
    }

    @LoginRequired
    @PostMapping("/challenges/{challengeId}/join")
    public ApiResponse<?> join(@LoginUser Long userId, @PathVariable Long challengeId) {
        return ApiResponse.ok("챌린지에 참여했습니다.", challengeService.join(userId, challengeId));
    }

    @LoginRequired
    @GetMapping("/me/challenges")
    public ApiResponse<?> myChallenges(@LoginUser Long userId) {
        return ApiResponse.ok("내 챌린지를 조회했습니다.", challengeService.findMyChallenges(userId));
    }
}
