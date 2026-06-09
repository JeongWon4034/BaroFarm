package com.freshgrowth.order.ai;

import com.freshgrowth.common.ApiResponse;
import com.freshgrowth.common.auth.LoginRequired;
import com.freshgrowth.common.auth.LoginUser;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/orders/ai")
public class BuyerInsightController {
    private final BuyerInsightService buyerInsightService;

    public BuyerInsightController(BuyerInsightService buyerInsightService) {
        this.buyerInsightService = buyerInsightService;
    }

    /** 내 구매 분석 AI 인사이트 (로그인 사용자 본인 주문 기준). */
    @LoginRequired
    @GetMapping("/insight")
    public ApiResponse<?> insight(@LoginUser Long buyerId) {
        return ApiResponse.ok("구매 분석 인사이트를 생성했습니다.", buyerInsightService.generate(buyerId));
    }
}
