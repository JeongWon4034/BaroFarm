package com.freshgrowth.order;

import com.freshgrowth.common.ApiResponse;
import com.freshgrowth.order.dto.OrderRequest;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1")
public class OrderController {
    private final OrderService orderService;

    public OrderController(OrderService orderService) {
        this.orderService = orderService;
    }

    @PostMapping("/orders")
    public ApiResponse<?> create(@RequestHeader("X-USER-ID") Long buyerId,
                                 @Valid @RequestBody OrderRequest request) {
        return ApiResponse.ok("주문이 완료되었습니다.", orderService.create(buyerId, request));
    }

    @GetMapping("/orders/my")
    public ApiResponse<?> findMyOrders(@RequestHeader("X-USER-ID") Long buyerId) {
        return ApiResponse.ok("내 주문 내역을 조회했습니다.", orderService.findMyOrders(buyerId));
    }

    @GetMapping("/orders/{orderId}")
    public ApiResponse<?> findById(@PathVariable Long orderId) {
        return ApiResponse.ok("주문 상세 정보를 조회했습니다.", orderService.findById(orderId));
    }

    @GetMapping("/seller/orders")
    public ApiResponse<?> findSellerOrders(@RequestHeader("X-USER-ID") Long sellerId) {
        return ApiResponse.ok("판매 내역을 조회했습니다.", orderService.findSellerOrders(sellerId));
    }
}
