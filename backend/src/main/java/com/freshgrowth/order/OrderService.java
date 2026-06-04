package com.freshgrowth.order;

import com.freshgrowth.common.AppException;
import com.freshgrowth.order.dto.OrderRequest;
import com.freshgrowth.product.Product;
import com.freshgrowth.product.ProductMapper;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;

@Service
public class OrderService {
    private final OrderMapper orderMapper;
    private final ProductMapper productMapper;

    public OrderService(OrderMapper orderMapper, ProductMapper productMapper) {
        this.orderMapper = orderMapper;
        this.productMapper = productMapper;
    }

    @Transactional
    public Order create(Long buyerId, OrderRequest request) {
        Product product = productMapper.findById(request.getProductId());
        if (product == null) {
            throw new AppException(HttpStatus.NOT_FOUND, "PRODUCT_NOT_FOUND", "상품을 찾을 수 없습니다.");
        }

        int updated = productMapper.decreaseStock(request.getProductId(), request.getQuantity());
        if (updated == 0) {
            throw new AppException(HttpStatus.BAD_REQUEST, "OUT_OF_STOCK", "재고가 부족합니다.");
        }

        Order order = new Order();
        order.setBuyerId(buyerId);
        order.setProductId(request.getProductId());
        order.setQuantity(request.getQuantity());
        order.setTotalPrice(product.getPrice() * request.getQuantity());
        order.setStatus("COMPLETED");
        orderMapper.insert(order);

        return orderMapper.findById(order.getOrderId());
    }

    public Order findById(Long orderId) {
        Order order = orderMapper.findById(orderId);
        if (order == null) {
            throw new AppException(HttpStatus.NOT_FOUND, "ORDER_NOT_FOUND", "주문을 찾을 수 없습니다.");
        }
        return order;
    }

    public List<Order> findMyOrders(Long buyerId) {
        return orderMapper.findByBuyerId(buyerId);
    }

    public List<Order> findSellerOrders(Long sellerId) {
        return orderMapper.findBySellerId(sellerId);
    }
}
