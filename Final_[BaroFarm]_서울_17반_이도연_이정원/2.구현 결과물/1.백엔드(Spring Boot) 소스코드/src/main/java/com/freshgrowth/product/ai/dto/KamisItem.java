package com.freshgrowth.product.ai.dto;

/** KAMIS 소매 품목 1건 (파싱 결과) */
public class KamisItem {
    private String category;   // category_name (식량작물/채소류/과일류/축산물/수산물/특용작물)
    private String itemName;   // item_name 예: "상추/청"
    private String unit;       // unit 예: "100g"
    private Integer price;     // dpr1 당일 소매가
    private Integer monthAgo;  // dpr3 1개월 전
    private Integer yearAgo;   // dpr4 1년 전
    private String changeRate; // value 등락률(%)

    public String getCategory() { return category; }
    public void setCategory(String category) { this.category = category; }
    public String getItemName() { return itemName; }
    public void setItemName(String itemName) { this.itemName = itemName; }
    public String getUnit() { return unit; }
    public void setUnit(String unit) { this.unit = unit; }
    public Integer getPrice() { return price; }
    public void setPrice(Integer price) { this.price = price; }
    public Integer getMonthAgo() { return monthAgo; }
    public void setMonthAgo(Integer monthAgo) { this.monthAgo = monthAgo; }
    public Integer getYearAgo() { return yearAgo; }
    public void setYearAgo(Integer yearAgo) { this.yearAgo = yearAgo; }
    public String getChangeRate() { return changeRate; }
    public void setChangeRate(String changeRate) { this.changeRate = changeRate; }
}
