package com.freshgrowth.product.ai.dto;

/**
 * 판매 정체 상품에 대한 AI 행동 추천(hover 시 호출). 이익 증진 행동 + 추천가를 담는다.
 * engine: LLM | RULE
 */
public class ProductAction {
    private Long productId;
    private Integer currentPrice;
    private Integer kamisPrice;
    private Integer recommendedPrice;
    private Integer daysSinceLastSale;
    private String headline; // 한 줄 요약(예: "9일째 미판매")
    private String action;   // 이익 증진 행동 추천(2~3문장)
    private String engine;

    public Long getProductId() { return productId; }
    public void setProductId(Long productId) { this.productId = productId; }
    public Integer getCurrentPrice() { return currentPrice; }
    public void setCurrentPrice(Integer currentPrice) { this.currentPrice = currentPrice; }
    public Integer getKamisPrice() { return kamisPrice; }
    public void setKamisPrice(Integer kamisPrice) { this.kamisPrice = kamisPrice; }
    public Integer getRecommendedPrice() { return recommendedPrice; }
    public void setRecommendedPrice(Integer recommendedPrice) { this.recommendedPrice = recommendedPrice; }
    public Integer getDaysSinceLastSale() { return daysSinceLastSale; }
    public void setDaysSinceLastSale(Integer daysSinceLastSale) { this.daysSinceLastSale = daysSinceLastSale; }
    public String getHeadline() { return headline; }
    public void setHeadline(String headline) { this.headline = headline; }
    public String getAction() { return action; }
    public void setAction(String action) { this.action = action; }
    public String getEngine() { return engine; }
    public void setEngine(String engine) { this.engine = engine; }
}
