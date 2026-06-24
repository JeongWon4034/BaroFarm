package com.freshgrowth.coupon;

import java.time.LocalDateTime;

/**
 * 챌린지 완료 보상 쿠폰. 결제 시 1회 사용해 추가 할인을 받는다.
 * 조회 시 challenges 를 조인해 어떤 챌린지 보상인지(title)도 함께 담는다.
 */
public class Coupon {
    private Long couponId;
    private Long userId;
    private Long sourceChallengeId;
    private Integer discountRate;     // 추가 할인율(%)
    private String status;            // ISSUED / USED / EXPIRED
    private LocalDateTime issuedAt;
    private LocalDateTime expiresAt;
    private LocalDateTime usedAt;
    private Long usedOrderId;

    // 조인된 표시용
    private String sourceChallengeTitle;

    public Long getCouponId() { return couponId; }
    public void setCouponId(Long couponId) { this.couponId = couponId; }
    public Long getUserId() { return userId; }
    public void setUserId(Long userId) { this.userId = userId; }
    public Long getSourceChallengeId() { return sourceChallengeId; }
    public void setSourceChallengeId(Long sourceChallengeId) { this.sourceChallengeId = sourceChallengeId; }
    public Integer getDiscountRate() { return discountRate; }
    public void setDiscountRate(Integer discountRate) { this.discountRate = discountRate; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    public LocalDateTime getIssuedAt() { return issuedAt; }
    public void setIssuedAt(LocalDateTime issuedAt) { this.issuedAt = issuedAt; }
    public LocalDateTime getExpiresAt() { return expiresAt; }
    public void setExpiresAt(LocalDateTime expiresAt) { this.expiresAt = expiresAt; }
    public LocalDateTime getUsedAt() { return usedAt; }
    public void setUsedAt(LocalDateTime usedAt) { this.usedAt = usedAt; }
    public Long getUsedOrderId() { return usedOrderId; }
    public void setUsedOrderId(Long usedOrderId) { this.usedOrderId = usedOrderId; }
    public String getSourceChallengeTitle() { return sourceChallengeTitle; }
    public void setSourceChallengeTitle(String sourceChallengeTitle) { this.sourceChallengeTitle = sourceChallengeTitle; }
}
