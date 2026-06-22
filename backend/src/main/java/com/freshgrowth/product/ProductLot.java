package com.freshgrowth.product;

import java.time.LocalDate;
import java.time.LocalDateTime;

/**
 * 폐기기간별 판매 옵션(lot). 같은 품목(products)에 여러 lot 이 매달리며,
 * 각 lot 은 자체 유통기한·재고·정가를 가진다. 떨이가/위험도는 DB 비저장 —
 * 조회 시 {@link WastePricingEngine} 이 계산해 채운다.
 */
public class ProductLot {
    private Long lotId;
    private Long productId;
    private LocalDate expirationDate;
    private Integer stockQty;
    private Integer price;
    private LocalDateTime createdAt;

    // --- 폐기위험·동적가격 엔진 산출값 (DB 비저장) ---
    private Integer daysToExpiry;
    private String riskLevel;        // HIGH | MEDIUM | LOW | EXPIRED
    private Double riskScore;        // 0.0 ~ 1.0
    private Integer discountRate;    // 추천 할인율(%)
    private Integer discountedPrice; // 동적 떨이가

    public Long getLotId() { return lotId; }
    public void setLotId(Long lotId) { this.lotId = lotId; }
    public Long getProductId() { return productId; }
    public void setProductId(Long productId) { this.productId = productId; }
    public LocalDate getExpirationDate() { return expirationDate; }
    public void setExpirationDate(LocalDate expirationDate) { this.expirationDate = expirationDate; }
    public Integer getStockQty() { return stockQty; }
    public void setStockQty(Integer stockQty) { this.stockQty = stockQty; }
    public Integer getPrice() { return price; }
    public void setPrice(Integer price) { this.price = price; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
    public Integer getDaysToExpiry() { return daysToExpiry; }
    public void setDaysToExpiry(Integer daysToExpiry) { this.daysToExpiry = daysToExpiry; }
    public String getRiskLevel() { return riskLevel; }
    public void setRiskLevel(String riskLevel) { this.riskLevel = riskLevel; }
    public Double getRiskScore() { return riskScore; }
    public void setRiskScore(Double riskScore) { this.riskScore = riskScore; }
    public Integer getDiscountRate() { return discountRate; }
    public void setDiscountRate(Integer discountRate) { this.discountRate = discountRate; }
    public Integer getDiscountedPrice() { return discountedPrice; }
    public void setDiscountedPrice(Integer discountedPrice) { this.discountedPrice = discountedPrice; }
}
