package com.freshgrowth.wishlist;

import com.freshgrowth.common.ApiResponse;
import com.freshgrowth.common.auth.LoginRequired;
import com.freshgrowth.common.auth.LoginUser;
import com.freshgrowth.wishlist.dto.WishlistRequest;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1")
public class WishlistController {
    private final WishlistService wishlistService;

    public WishlistController(WishlistService wishlistService) {
        this.wishlistService = wishlistService;
    }

    @LoginRequired(role = "BUYER")
    @PostMapping("/wishlist")
    public ApiResponse<?> add(@LoginUser Long userId,
                              @Valid @RequestBody WishlistRequest request) {
        wishlistService.add(userId, request.getProductId());
        return ApiResponse.ok("찜 목록에 추가했습니다.", null);
    }

    @LoginRequired(role = "BUYER")
    @DeleteMapping("/wishlist/{productId}")
    public ApiResponse<?> remove(@LoginUser Long userId,
                                 @PathVariable Long productId) {
        wishlistService.remove(userId, productId);
        return ApiResponse.ok("찜을 해제했습니다.", null);
    }

    @LoginRequired(role = "BUYER")
    @GetMapping("/wishlist")
    public ApiResponse<?> myWishlist(@LoginUser Long userId) {
        return ApiResponse.ok("찜 목록을 조회했습니다.", wishlistService.findMyWishlist(userId));
    }
}
