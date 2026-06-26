package com.freshgrowth.product.ai.dto;

/** 동일 카테고리 가격 통계 (추천가 산출 근거) */
public class PriceStats {
    private long cnt;
    private double avgPrice;
    private int minPrice;
    private int maxPrice;

    public long getCnt() { return cnt; }
    public void setCnt(long cnt) { this.cnt = cnt; }
    public double getAvgPrice() { return avgPrice; }
    public void setAvgPrice(double avgPrice) { this.avgPrice = avgPrice; }
    public int getMinPrice() { return minPrice; }
    public void setMinPrice(int minPrice) { this.minPrice = minPrice; }
    public int getMaxPrice() { return maxPrice; }
    public void setMaxPrice(int maxPrice) { this.maxPrice = maxPrice; }
}
