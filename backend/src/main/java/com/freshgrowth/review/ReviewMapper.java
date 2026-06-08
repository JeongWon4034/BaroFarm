package com.freshgrowth.review;

import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import java.util.List;

@Mapper
public interface ReviewMapper {
    void insert(Review review);
    Review findById(@Param("reviewId") Long reviewId);
    Review findByOrderId(@Param("orderId") Long orderId);
    List<Review> findByProductId(@Param("productId") Long productId);
    int update(@Param("reviewId") Long reviewId, @Param("rating") Integer rating, @Param("content") String content);
    int delete(@Param("reviewId") Long reviewId);
}
