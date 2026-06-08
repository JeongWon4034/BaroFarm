package com.freshgrowth.post.ai;

import com.freshgrowth.common.ApiResponse;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/posts/ai")
public class PostAiController {
    private final PostAiService postAiService;

    public PostAiController(PostAiService postAiService) {
        this.postAiService = postAiService;
    }

    /** 게시판 상단 AI 식료품 트렌드 카드 (비로그인도 조회 가능). */
    @GetMapping("/trend")
    public ApiResponse<?> trend() {
        return ApiResponse.ok("식료품 트렌드를 분석했습니다.", postAiService.getMarketTrend());
    }
}
