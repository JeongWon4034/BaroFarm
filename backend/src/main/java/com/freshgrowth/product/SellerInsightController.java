package com.freshgrowth.product;

import com.freshgrowth.common.ApiResponse;
import com.freshgrowth.common.auth.LoginRequired;
import com.freshgrowth.common.auth.LoginUser;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1")
public class SellerInsightController {
    private final SellerInsightService sellerInsightService;

    public SellerInsightController(SellerInsightService sellerInsightService) {
        this.sellerInsightService = sellerInsightService;
    }

    // 판매자 상품 표: KAMIS 기준 소매가·현재가·추천가 + 정체 신호 (LLM 미사용, 빠름)
    @LoginRequired(role = "SELLER")
    @GetMapping("/seller/products/insights")
    public ApiResponse<?> insights(@LoginUser Long sellerId) {
        return ApiResponse.ok("상품 인사이트를 조회했습니다.", sellerInsightService.insights(sellerId));
    }

    // 정체 상품 행동 추천 (hover 시 호출, LLM)
    @LoginRequired(role = "SELLER")
    @GetMapping("/seller/products/{productId}/action")
    public ApiResponse<?> action(@LoginUser Long sellerId, @PathVariable Long productId) {
        return ApiResponse.ok("행동 추천을 생성했습니다.", sellerInsightService.action(sellerId, productId));
    }
}
