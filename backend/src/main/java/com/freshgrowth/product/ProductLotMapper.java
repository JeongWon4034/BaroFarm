package com.freshgrowth.product;

import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import java.util.List;

@Mapper
public interface ProductLotMapper {
    void insert(ProductLot lot);
    ProductLot findById(@Param("lotId") Long lotId);
    List<ProductLot> findByProductId(@Param("productId") Long productId);
    int decreaseStock(@Param("lotId") Long lotId, @Param("quantity") int quantity);
}
