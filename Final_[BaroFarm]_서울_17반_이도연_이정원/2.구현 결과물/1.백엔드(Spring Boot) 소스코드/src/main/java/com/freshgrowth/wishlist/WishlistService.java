package com.freshgrowth.wishlist;

import com.freshgrowth.common.AppException;
import com.freshgrowth.product.Product;
import com.freshgrowth.product.ProductMapper;
import com.freshgrowth.product.WastePricingEngine;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class WishlistService {
    private final WishlistMapper wishlistMapper;
    private final ProductMapper productMapper;
    private final WastePricingEngine pricingEngine;

    public WishlistService(WishlistMapper wishlistMapper, ProductMapper productMapper, WastePricingEngine pricingEngine) {
        this.wishlistMapper = wishlistMapper;
        this.productMapper = productMapper;
        this.pricingEngine = pricingEngine;
    }

    @Transactional
    public void add(Long userId, Long productId) {
        if (productMapper.findById(productId) == null) {
            throw new AppException(HttpStatus.NOT_FOUND, "PRODUCT_NOT_FOUND", "상품을 찾을 수 없습니다.");
        }
        wishlistMapper.insert(userId, productId);
    }

    @Transactional
    public void remove(Long userId, Long productId) {
        wishlistMapper.delete(userId, productId);
    }

    public List<Product> findMyWishlist(Long userId) {
        List<Product> products = wishlistMapper.findWishedProducts(userId);
        products.forEach(pricingEngine::apply);
        return products;
    }
}
