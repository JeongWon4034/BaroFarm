package com.freshgrowth.product;

import com.freshgrowth.product.ai.dto.PriceStats;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import java.util.List;

@Mapper
public interface ProductMapper {
    void insert(Product product);
    Product findById(@Param("productId") Long productId);
    List<Product> findAll(@Param("offset") int offset, @Param("size") int size,
                          @Param("keyword") String keyword, @Param("category") String category,
                          @Param("sort") String sort);
    long countAll(@Param("keyword") String keyword, @Param("category") String category);
    List<Product> findBySellerId(@Param("sellerId") Long sellerId);
    List<Product> findSameNameOthers(@Param("name") String name, @Param("productId") Long productId);
    int update(Product product);
    int delete(@Param("productId") Long productId, @Param("sellerId") Long sellerId);
    int decreaseStock(@Param("productId") Long productId, @Param("quantity") int quantity);
    PriceStats findCategoryPriceStats(@Param("category") String category);
}
