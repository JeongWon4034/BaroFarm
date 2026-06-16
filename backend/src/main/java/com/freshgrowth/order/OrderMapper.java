package com.freshgrowth.order;

import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import java.util.List;

@Mapper
public interface OrderMapper {
    void insert(Order order);
    Order findById(@Param("orderId") Long orderId);
    List<Order> findByBuyerId(@Param("buyerId") Long buyerId);
    List<Order> findBySellerId(@Param("sellerId") Long sellerId);
    int updateStatus(@Param("orderId") Long orderId, @Param("status") String status);
}
