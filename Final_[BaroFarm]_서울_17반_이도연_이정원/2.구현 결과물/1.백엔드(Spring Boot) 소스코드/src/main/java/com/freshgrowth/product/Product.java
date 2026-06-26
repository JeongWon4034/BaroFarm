package com.freshgrowth.product;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

public class Product {
    private Long productId;
    private Long sellerId;
    private String name;
    private String description;
    private String category;
    private Integer price;
    private Integer stockQty;
    private String thumbnailUrl;
    private LocalDate expirationDate;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    private String sellerName;       // 판매처명(판매처 비교 등에서 join으로 채움)

    // --- 폐기위험·동적가격 엔진 산출값 (DB 비저장, 조회 시 WastePricingEngine이 계산) ---
    private Integer daysToExpiry;    // 유통기한까지 남은 일수 (음수면 경과)
    private String riskLevel;        // HIGH | MEDIUM | LOW | EXPIRED
    private Double riskScore;        // 0.0 ~ 1.0
    private Integer discountRate;    // 추천 할인율(%)
    private Integer discountedPrice; // 동적 할인가

    // --- 리뷰 통계 (조회 시 reviews 집계) ---
    private Integer reviewCount;     // 리뷰 수
    private Double avgRating;        // 평균 별점(소수1자리), 리뷰 없으면 null

    // --- 폐기기간 옵션(lot) ---
    private Integer lotCount;        // 묶인 lot 수(0이면 단일상품·레거시). 목록 카드의 "옵션 N개" 배지용
    private List<ProductLot> lots;   // 상세조회 시 채워지는 폐기기간별 옵션 목록

    public Long getProductId() { return productId; }
    public void setProductId(Long productId) { this.productId = productId; }
    public Long getSellerId() { return sellerId; }
    public void setSellerId(Long sellerId) { this.sellerId = sellerId; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    public String getCategory() { return category; }
    public void setCategory(String category) { this.category = category; }
    public Integer getPrice() { return price; }
    public void setPrice(Integer price) { this.price = price; }
    public Integer getStockQty() { return stockQty; }
    public void setStockQty(Integer stockQty) { this.stockQty = stockQty; }
    public String getThumbnailUrl() { return thumbnailUrl; }
    public void setThumbnailUrl(String thumbnailUrl) { this.thumbnailUrl = thumbnailUrl; }
    public LocalDate getExpirationDate() { return expirationDate; }
    public void setExpirationDate(LocalDate expirationDate) { this.expirationDate = expirationDate; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
    public LocalDateTime getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(LocalDateTime updatedAt) { this.updatedAt = updatedAt; }
    public String getSellerName() { return sellerName; }
    public void setSellerName(String sellerName) { this.sellerName = sellerName; }
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
    public Integer getReviewCount() { return reviewCount; }
    public void setReviewCount(Integer reviewCount) { this.reviewCount = reviewCount; }
    public Double getAvgRating() { return avgRating; }
    public void setAvgRating(Double avgRating) { this.avgRating = avgRating; }
    public Integer getLotCount() { return lotCount; }
    public void setLotCount(Integer lotCount) { this.lotCount = lotCount; }
    public List<ProductLot> getLots() { return lots; }
    public void setLots(List<ProductLot> lots) { this.lots = lots; }
}
