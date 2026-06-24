package com.freshgrowth.coupon;

import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface CouponMapper {
    void insert(Coupon coupon);
    List<Coupon> findByUser(@Param("userId") Long userId);
    // 결제 사용 검증용 — 소유 + ISSUED + 미만료인 쿠폰만 반환
    Coupon findUsableByIdAndUser(@Param("couponId") Long couponId, @Param("userId") Long userId);
    int markUsed(@Param("couponId") Long couponId, @Param("orderId") Long orderId);
}
