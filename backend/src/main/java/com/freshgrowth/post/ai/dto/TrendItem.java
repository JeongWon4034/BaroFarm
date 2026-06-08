package com.freshgrowth.post.ai.dto;

/** 트렌드 카드에 표시할 개별 품목의 시세 변동 */
public class TrendItem {
    private String itemName;   // 예: "상추/청"
    private String unit;       // 예: "100g"
    private Integer price;     // 당일 소매가
    private Integer monthAgo;  // 1개월 전 소매가
    private double changePct;  // 한 달 전 대비 등락률(%) — 음수면 하락

    public String getItemName() { return itemName; }
    public void setItemName(String itemName) { this.itemName = itemName; }
    public String getUnit() { return unit; }
    public void setUnit(String unit) { this.unit = unit; }
    public Integer getPrice() { return price; }
    public void setPrice(Integer price) { this.price = price; }
    public Integer getMonthAgo() { return monthAgo; }
    public void setMonthAgo(Integer monthAgo) { this.monthAgo = monthAgo; }
    public double getChangePct() { return changePct; }
    public void setChangePct(double changePct) { this.changePct = changePct; }
}
