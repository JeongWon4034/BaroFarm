package com.freshgrowth.product.ai.dto;

/** 추천가 응답: 빠른 판매 추천가 + 참고 범위 + 산출 근거 */
public class PriceSuggestion {
    private Integer suggestedPrice;
    private Integer low;
    private Integer high;
    private String basis;

    public Integer getSuggestedPrice() { return suggestedPrice; }
    public void setSuggestedPrice(Integer suggestedPrice) { this.suggestedPrice = suggestedPrice; }
    public Integer getLow() { return low; }
    public void setLow(Integer low) { this.low = low; }
    public Integer getHigh() { return high; }
    public void setHigh(Integer high) { this.high = high; }
    public String getBasis() { return basis; }
    public void setBasis(String basis) { this.basis = basis; }
}
