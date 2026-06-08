package com.freshgrowth.wishlist.dto;

import jakarta.validation.constraints.NotNull;

public class WishlistRequest {
    @NotNull
    private Long productId;

    public Long getProductId() { return productId; }
}
