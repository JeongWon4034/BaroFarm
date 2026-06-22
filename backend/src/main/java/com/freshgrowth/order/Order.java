package com.freshgrowth.order;

import java.time.LocalDateTime;

public class Order {
    private Long orderId;
    private Long buyerId;
    private Long sellerId;         // 상품 판매자 — 주문 상태 변경 권한 검증용
    private Long productId;
    private Long lotId;            // 구매한 폐기기간 옵션(lot). 상품단위·레거시 구매는 null
    private String productName;
    private String category;
    private Integer quantity;
    private Integer totalPrice;
    private String status;
    private LocalDateTime orderDate;
    private Long reviewId; // 이 주문에 작성된 리뷰 id (없으면 null) — 리뷰 작성 여부 판별용

    public Long getOrderId() { return orderId; }
    public void setOrderId(Long orderId) { this.orderId = orderId; }
    public Long getBuyerId() { return buyerId; }
    public void setBuyerId(Long buyerId) { this.buyerId = buyerId; }
    public Long getSellerId() { return sellerId; }
    public void setSellerId(Long sellerId) { this.sellerId = sellerId; }
    public Long getProductId() { return productId; }
    public void setProductId(Long productId) { this.productId = productId; }
    public Long getLotId() { return lotId; }
    public void setLotId(Long lotId) { this.lotId = lotId; }
    public String getProductName() { return productName; }
    public void setProductName(String productName) { this.productName = productName; }
    public String getCategory() { return category; }
    public void setCategory(String category) { this.category = category; }
    public Integer getQuantity() { return quantity; }
    public void setQuantity(Integer quantity) { this.quantity = quantity; }
    public Integer getTotalPrice() { return totalPrice; }
    public void setTotalPrice(Integer totalPrice) { this.totalPrice = totalPrice; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    public LocalDateTime getOrderDate() { return orderDate; }
    public void setOrderDate(LocalDateTime orderDate) { this.orderDate = orderDate; }
    public Long getReviewId() { return reviewId; }
    public void setReviewId(Long reviewId) { this.reviewId = reviewId; }
}
