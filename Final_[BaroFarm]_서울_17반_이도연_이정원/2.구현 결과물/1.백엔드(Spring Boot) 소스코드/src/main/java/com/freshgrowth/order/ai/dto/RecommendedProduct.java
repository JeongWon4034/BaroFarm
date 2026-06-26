package com.freshgrowth.order.ai.dto;

/**
 * AI가 실제 카탈로그에서 고른 추천 상품.
 * LLM이 상품명을 지어내지 않고 실제 product_id를 참조하므로, 프론트에서 상세 이동·장바구니가 가능하다.
 */
public class RecommendedProduct {
    private Long productId;
    private String name;
    private String category;
    private Integer price;            // 정가
    private Integer discountedPrice;  // 마감임박 할인가(있을 때만, 없으면 null)
    private String thumbnailUrl;
    private String reason;            // AI가 단 추천 이유(한 줄)

    public RecommendedProduct() {}

    public RecommendedProduct(Long productId, String name, String category, Integer price,
                              Integer discountedPrice, String thumbnailUrl, String reason) {
        this.productId = productId;
        this.name = name;
        this.category = category;
        this.price = price;
        this.discountedPrice = discountedPrice;
        this.thumbnailUrl = thumbnailUrl;
        this.reason = reason;
    }

    public Long getProductId() { return productId; }
    public void setProductId(Long productId) { this.productId = productId; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getCategory() { return category; }
    public void setCategory(String category) { this.category = category; }
    public Integer getPrice() { return price; }
    public void setPrice(Integer price) { this.price = price; }
    public Integer getDiscountedPrice() { return discountedPrice; }
    public void setDiscountedPrice(Integer discountedPrice) { this.discountedPrice = discountedPrice; }
    public String getThumbnailUrl() { return thumbnailUrl; }
    public void setThumbnailUrl(String thumbnailUrl) { this.thumbnailUrl = thumbnailUrl; }
    public String getReason() { return reason; }
    public void setReason(String reason) { this.reason = reason; }
}
