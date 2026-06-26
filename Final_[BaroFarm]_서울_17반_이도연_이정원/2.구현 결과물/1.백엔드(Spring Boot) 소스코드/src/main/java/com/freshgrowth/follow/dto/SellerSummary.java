package com.freshgrowth.follow.dto;

/**
 * 판매자 공개 요약: 이름·팔로워수·상품수 + (조회자 기준) 내 팔로우 여부.
 */
public class SellerSummary {
    private Long sellerId;
    private String name;
    private long followerCount;
    private long productCount;
    private boolean isFollowing;

    public Long getSellerId() { return sellerId; }
    public void setSellerId(Long sellerId) { this.sellerId = sellerId; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public long getFollowerCount() { return followerCount; }
    public void setFollowerCount(long followerCount) { this.followerCount = followerCount; }
    public long getProductCount() { return productCount; }
    public void setProductCount(long productCount) { this.productCount = productCount; }
    public boolean getIsFollowing() { return isFollowing; }
    public void setIsFollowing(boolean isFollowing) { this.isFollowing = isFollowing; }
}
