package com.freshgrowth.product.ai.dto;

import java.util.List;

/**
 * 추천가 응답: 추천 가격 + 데이터 근거(basis) + 추천 이유(reason) + KAMIS 원가 시세 + 경쟁 소매가.
 * source: KAMIS(시세 매칭) | CATALOG(자체 통계 폴백) | NONE(근거 없음)
 * engine: LLM(AI가 원가·경쟁가 종합) | RULE(결정형 산식)
 */
public class PriceSuggestion {
    private Integer suggestedPrice;
    private String source;
    private String engine;
    private String basis;
    private String reason;
    private String sellUnit;   // 추천가가 기준으로 삼은 판매 단위(입력값 또는 AI 추론)
    private String unitBasis;   // AI가 경쟁가를 어떻게 단위 정규화했는지 근거(당근식 투명성)

    // KAMIS 시세 근거(원가성)
    private String marketItem;
    private String marketUnit;
    private Integer marketPrice;
    private Integer marketMonthAgo;
    private Integer marketYearAgo;
    private String marketChange;

    // 네이버 쇼핑 경쟁 소매가 근거
    private Integer competitorLow;
    private Integer competitorAvg;
    private Integer competitorHigh;
    private Integer competitorCount;
    private List<CompetitorPrice> competitors;

    // 자체 카탈로그 보조
    private Long catalogCount;
    private Integer catalogAvg;

    public Integer getSuggestedPrice() { return suggestedPrice; }
    public void setSuggestedPrice(Integer suggestedPrice) { this.suggestedPrice = suggestedPrice; }
    public String getSource() { return source; }
    public void setSource(String source) { this.source = source; }
    public String getEngine() { return engine; }
    public void setEngine(String engine) { this.engine = engine; }
    public String getBasis() { return basis; }
    public void setBasis(String basis) { this.basis = basis; }
    public String getReason() { return reason; }
    public void setReason(String reason) { this.reason = reason; }
    public String getSellUnit() { return sellUnit; }
    public void setSellUnit(String sellUnit) { this.sellUnit = sellUnit; }
    public String getUnitBasis() { return unitBasis; }
    public void setUnitBasis(String unitBasis) { this.unitBasis = unitBasis; }
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
    public Integer getCompetitorLow() { return competitorLow; }
    public void setCompetitorLow(Integer competitorLow) { this.competitorLow = competitorLow; }
    public Integer getCompetitorAvg() { return competitorAvg; }
    public void setCompetitorAvg(Integer competitorAvg) { this.competitorAvg = competitorAvg; }
    public Integer getCompetitorHigh() { return competitorHigh; }
    public void setCompetitorHigh(Integer competitorHigh) { this.competitorHigh = competitorHigh; }
    public Integer getCompetitorCount() { return competitorCount; }
    public void setCompetitorCount(Integer competitorCount) { this.competitorCount = competitorCount; }
    public List<CompetitorPrice> getCompetitors() { return competitors; }
    public void setCompetitors(List<CompetitorPrice> competitors) { this.competitors = competitors; }
    public Long getCatalogCount() { return catalogCount; }
    public void setCatalogCount(Long catalogCount) { this.catalogCount = catalogCount; }
    public Integer getCatalogAvg() { return catalogAvg; }
    public void setCatalogAvg(Integer catalogAvg) { this.catalogAvg = catalogAvg; }
}
