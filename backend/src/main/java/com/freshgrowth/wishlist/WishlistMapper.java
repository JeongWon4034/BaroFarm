package com.freshgrowth.wishlist;

import com.freshgrowth.product.Product;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface WishlistMapper {
    int insert(@Param("userId") Long userId, @Param("productId") Long productId);
    int delete(@Param("userId") Long userId, @Param("productId") Long productId);
    List<Product> findWishedProducts(@Param("userId") Long userId);
}
