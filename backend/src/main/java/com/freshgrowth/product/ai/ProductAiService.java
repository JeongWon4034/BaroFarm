package com.freshgrowth.product.ai;

import com.freshgrowth.product.ProductMapper;
import com.freshgrowth.product.ai.dto.PriceStats;
import com.freshgrowth.product.ai.dto.PriceSuggestion;
import org.springframework.stereotype.Service;

@Service
public class ProductAiService {
    private final AiClient aiClient;
    private final ProductMapper productMapper;

    public ProductAiService(AiClient aiClient, ProductMapper productMapper) {
        this.aiClient = aiClient;
        this.productMapper = productMapper;
    }

    /** 생성형 AI 상품 설명 (GMS) */
    public String generateDescription(String name, String category) {
        String system = "너는 신선식품 산지직거래 마켓의 카피라이터다. "
                + "상품의 신선함과 매력을 살린 2~3문장의 한국어 상품 설명을 작성한다. "
                + "과장된 표현과 이모지는 쓰지 말고, 구매자가 신뢰할 수 있게 담백하게 쓴다.";
        String user = "상품명: " + name + "\n카테고리: " + (category == null ? "" : category)
                + "\n이 상품의 판매용 상세 설명을 2~3문장으로 작성해줘.";
        return aiClient.chat(system, user, 300);
    }

    /** 추천가 — 동일 카테고리 자체 통계 기반(빠른 판매가). 가락 시세 연동은 차후. */
    public PriceSuggestion suggestPrice(String category) {
        PriceSuggestion s = new PriceSuggestion();
        PriceStats stats = productMapper.findCategoryPriceStats(category);
        if (stats == null || stats.getCnt() == 0) {
            s.setBasis("동일 카테고리 판매 데이터가 아직 없어 추천가를 낼 수 없습니다. 직접 입력해주세요.");
            return s;
        }
        int avg = (int) Math.round(stats.getAvgPrice());
        int suggested = (int) (Math.round(avg * 0.92 / 100.0) * 100); // 평균보다 약 8% 낮게, 100원 단위
        s.setSuggestedPrice(Math.max(suggested, 100));
        s.setLow(stats.getMinPrice());
        s.setHigh(avg);
        s.setBasis("동일 카테고리 상품 " + stats.getCnt() + "개 평균가 "
                + String.format("%,d", avg) + "원 기준, 빠른 판매를 위해 약 8% 낮춘 추천가입니다. (자체 마켓 통계)");
        return s;
    }
}
