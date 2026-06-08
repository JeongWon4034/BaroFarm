package com.freshgrowth.product.ai.dto;

/**
 * 추천가 응답: 추천 가격 + 데이터 근거(basis) + 추천 이유(reason) + KAMIS 시세 상세.
 * source: KAMIS(시세 매칭) | CATALOG(자체 통계 폴백) | NONE(근거 없음)
 */
public class PriceSuggestion {
    private Integer suggestedPrice;
    private String source;
    private String basis;
    private String reason;

    // KAMIS 시세 근거
    private String marketItem;
    private String marketUnit;
    private Integer marketPrice;
    private Integer marketMonthAgo;
    private Integer marketYearAgo;
    private String marketChange;

    // 자체 카탈로그 보조
    private Long catalogCount;
    private Integer catalogAvg;

    public Integer getSuggestedPrice() { return suggestedPrice; }
    public void setSuggestedPrice(Integer suggestedPrice) { this.suggestedPrice = suggestedPrice; }
    public String getSource() { return source; }
    public void setSource(String source) { this.source = source; }
    public String getBasis() { return basis; }
    public void setBasis(String basis) { this.basis = basis; }
    public String getReason() { return reason; }
    public void setReason(String reason) { this.reason = reason; }
    public String getMarketItem() { return marketItem; }
    public void setMarketItem(String marketItem) { this.marketItem = marketItem; }
    public String getMarketUnit() { return marketUnit; }
    public void setMarketUnit(String marketUnit) { this.marketUnit = marketUnit; }
    public Integer getMarketPrice() { return marketPrice; }
    public void setMarketPrice(Integer marketPrice) { this.marketPrice = marketPrice; }
    public Integer getMarketMonthAgo() { return marketMonthAgo; }
    public void setMarketMonthAgo(Integer marketMonthAgo) { this.marketMonthAgo = marketMonthAgo; }
    public Integer getMarketYearAgo() { return marketYearAgo; }
    public void setMarketYearAgo(Integer marketYearAgo) { this.marketYearAgo = marketYearAgo; }
    public String getMarketChange() { return marketChange; }
    public void setMarketChange(String marketChange) { this.marketChange = marketChange; }
    public Long getCatalogCount() { return catalogCount; }
    public void setCatalogCount(Long catalogCount) { this.catalogCount = catalogCount; }
    public Integer getCatalogAvg() { return catalogAvg; }
    public void setCatalogAvg(Integer catalogAvg) { this.catalogAvg = catalogAvg; }
}
