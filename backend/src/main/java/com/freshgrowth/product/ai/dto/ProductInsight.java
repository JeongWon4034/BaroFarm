package com.freshgrowth.product.ai.dto;

/**
 * 판매자 상품 표의 한 줄 인사이트 — KAMIS 기준 소매가 · 현재 판매가 · 추천 판매가 + 판매 정체 신호.
 * 표 로드 시 한 번에 계산(LLM 미사용, KAMIS 캐시 조회만). 정체 상품의 구체적 행동 추천은 hover 시 별도 호출.
 */
public class ProductInsight {
    private Long productId;
    private Integer kamisPrice;   // KAMIS 기준 소매가(매칭 시), 없으면 null
    private String kamisItem;     // 매칭된 KAMIS 품목명
    private String kamisUnit;     // KAMIS 단위
    private Integer currentPrice;  // 현재 판매가(할인 적용가 우선)
    private Integer recommendedPrice; // 추천 판매가(규칙 기반)
    private Integer daysSinceLastSale; // 마지막 판매 후 경과일(판매 이력 없으면 null)
    private Integer daysListed;    // 등록 후 경과일
    private boolean neverSold;     // 한 번도 안 팔림
    private boolean stale;         // 판매 정체(일정 기간 미판매 + 재고 있음) → 행동 추천 대상

    public Long getProductId() { return productId; }
    public void setProductId(Long productId) { this.productId = productId; }
    public Integer getKamisPrice() { return kamisPrice; }
    public void setKamisPrice(Integer kamisPrice) { this.kamisPrice = kamisPrice; }
    public String getKamisItem() { return kamisItem; }
    public void setKamisItem(String kamisItem) { this.kamisItem = kamisItem; }
    public String getKamisUnit() { return kamisUnit; }
    public void setKamisUnit(String kamisUnit) { this.kamisUnit = kamisUnit; }
    public Integer getCurrentPrice() { return currentPrice; }
    public void setCurrentPrice(Integer currentPrice) { this.currentPrice = currentPrice; }
    public Integer getRecommendedPrice() { return recommendedPrice; }
    public void setRecommendedPrice(Integer recommendedPrice) { this.recommendedPrice = recommendedPrice; }
    public Integer getDaysSinceLastSale() { return daysSinceLastSale; }
    public void setDaysSinceLastSale(Integer daysSinceLastSale) { this.daysSinceLastSale = daysSinceLastSale; }
    public Integer getDaysListed() { return daysListed; }
    public void setDaysListed(Integer daysListed) { this.daysListed = daysListed; }
    public boolean isNeverSold() { return neverSold; }
    public void setNeverSold(boolean neverSold) { this.neverSold = neverSold; }
    public boolean isStale() { return stale; }
    public void setStale(boolean stale) { this.stale = stale; }
}
