package com.freshgrowth.coupon;

import com.freshgrowth.common.AppException;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;

@Service
public class CouponService {
    private static final int VALID_DAYS = 30; // 발급 후 유효기간(일)

    private final CouponMapper couponMapper;

    public CouponService(CouponMapper couponMapper) {
        this.couponMapper = couponMapper;
    }

    /** 챌린지 완료 보상으로 쿠폰 발급. */
    public void issueForChallenge(Long userId, Long challengeId, int discountRate) {
        Coupon c = new Coupon();
        c.setUserId(userId);
        c.setSourceChallengeId(challengeId);
        c.setDiscountRate(discountRate);
        c.setExpiresAt(LocalDateTime.now().plusDays(VALID_DAYS));
        couponMapper.insert(c);
    }

    public List<Coupon> findMyCoupons(Long userId) {
        return couponMapper.findByUser(userId);
    }

    /** 결제 시 쿠폰 검증(소유·ISSUED·미만료). 유효하지 않으면 예외. */
    public Coupon requireUsable(Long couponId, Long userId) {
        Coupon c = couponMapper.findUsableByIdAndUser(couponId, userId);
        if (c == null) {
            throw new AppException(HttpStatus.BAD_REQUEST, "COUPON_INVALID", "사용할 수 없는 쿠폰입니다.");
        }
        return c;
    }

    /** 쿠폰 사용 처리(주문 확정 후). status='ISSUED' 조건으로 중복 사용 차단. */
    public void markUsed(Long couponId, Long orderId) {
        if (couponMapper.markUsed(couponId, orderId) == 0) {
            throw new AppException(HttpStatus.BAD_REQUEST, "COUPON_ALREADY_USED", "이미 사용된 쿠폰입니다.");
        }
    }
}
