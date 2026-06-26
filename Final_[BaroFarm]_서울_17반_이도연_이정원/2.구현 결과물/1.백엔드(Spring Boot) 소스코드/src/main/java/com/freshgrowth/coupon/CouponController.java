package com.freshgrowth.coupon;

import com.freshgrowth.common.ApiResponse;
import com.freshgrowth.common.auth.LoginRequired;
import com.freshgrowth.common.auth.LoginUser;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1")
public class CouponController {
    private final CouponService couponService;

    public CouponController(CouponService couponService) {
        this.couponService = couponService;
    }

    @LoginRequired
    @GetMapping("/coupons")
    public ApiResponse<?> myCoupons(@LoginUser Long userId) {
        return ApiResponse.ok("내 쿠폰을 조회했습니다.", couponService.findMyCoupons(userId));
    }
}
