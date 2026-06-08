package com.freshgrowth.product.ai;

import com.freshgrowth.common.ApiResponse;
import com.freshgrowth.common.auth.LoginRequired;
import com.freshgrowth.product.ai.dto.DescriptionRequest;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/v1/products/ai")
public class AiController {
    private final ProductAiService productAiService;

    public AiController(ProductAiService productAiService) {
        this.productAiService = productAiService;
    }

    @LoginRequired(role = "SELLER")
    @PostMapping("/description")
    public ApiResponse<?> description(@Valid @RequestBody DescriptionRequest request) {
        String description = productAiService.generateDescription(request.getName(), request.getCategory());
        return ApiResponse.ok("AI 상품 설명을 생성했습니다.", Map.of("description", description));
    }

    @LoginRequired(role = "SELLER")
    @GetMapping("/price-suggestion")
    public ApiResponse<?> priceSuggestion(@RequestParam String category) {
        return ApiResponse.ok("추천가를 산출했습니다.", productAiService.suggestPrice(category));
    }
}
