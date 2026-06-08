package com.freshgrowth.product.ai;

import com.freshgrowth.common.ApiResponse;
import com.freshgrowth.common.auth.LoginRequired;
import com.freshgrowth.common.auth.LoginUser;
import com.freshgrowth.product.ai.dto.DescriptionRequest;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/v1/products/ai")
public class AiController {
    private final ProductAiService productAiService;
    private final KamisClient kamisClient;

    public AiController(ProductAiService productAiService, KamisClient kamisClient) {
        this.productAiService = productAiService;
        this.kamisClient = kamisClient;
    }

    // KAMIS 시세 응답 구조 확인용(임시). 키 넣은 뒤 실제 응답 보고 추천가에 엮을 예정.
    @LoginRequired(role = "SELLER")
    @GetMapping("/kamis-debug")
    public ApiResponse<?> kamisDebug(@RequestParam(defaultValue = "dailySalesList") String action) {
        return ApiResponse.ok("KAMIS 시세 raw 응답", kamisClient.fetch(action, ""));
    }

    @LoginRequired(role = "SELLER")
    @PostMapping("/description")
    public ApiResponse<?> description(@Valid @RequestBody DescriptionRequest request) {
        return ApiResponse.ok("AI 상품 설명을 생성했습니다.",
                productAiService.generateDescription(request.getName(), request.getCategory(),
                        request.getExpirationDate(), request.getStockQty()));
    }

    @LoginRequired(role = "SELLER")
    @GetMapping("/seller-report")
    public ApiResponse<?> sellerReport(@LoginUser Long sellerId) {
        return ApiResponse.ok("판매자 AI 요약 리포트", productAiService.generateSellerReport(sellerId));
    }

    @LoginRequired(role = "SELLER")
    @GetMapping("/price-suggestion")
    public ApiResponse<?> priceSuggestion(@RequestParam(defaultValue = "") String name,
                                          @RequestParam String category) {
        return ApiResponse.ok("추천가를 산출했습니다.", productAiService.suggestPrice(name, category));
    }
}
