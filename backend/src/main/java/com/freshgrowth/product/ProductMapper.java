package com.freshgrowth.product;

import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import java.util.List;

@Mapper
public interface ProductMapper {
    void insert(Product product);
    Product findById(@Param("productId") Long productId);
    List<Product> findAll(@Param("offset") int offset, @Param("size") int size);
    long countAll();
    List<Product> findBySellerId(@Param("sellerId") Long sellerId);
    int update(Product product);
    int delete(@Param("productId") Long productId, @Param("sellerId") Long sellerId);
    int decreaseStock(@Param("productId") Long productId, @Param("quantity") int quantity);
}
