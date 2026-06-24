package com.freshgrowth.order;

import com.freshgrowth.common.ApiResponse;
import com.freshgrowth.common.auth.LoginRequired;
import com.freshgrowth.common.auth.LoginUser;
import com.freshgrowth.order.dto.OrderRequest;
import com.freshgrowth.order.dto.OrderStatusRequest;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1")
public class OrderController {
    private final OrderService orderService;

    public OrderController(OrderService orderService) {
        this.orderService = orderService;
    }

    @LoginRequired(role = "BUYER")
    @PostMapping("/orders")
    public ApiResponse<?> create(@LoginUser Long buyerId,
                                 @Valid @RequestBody OrderRequest request) {
        return ApiResponse.ok("주문이 완료되었습니다.", orderService.create(buyerId, request));
    }

    @LoginRequired
    @GetMapping("/orders/my")
    public ApiResponse<?> findMyOrders(@LoginUser Long buyerId) {
        return ApiResponse.ok("내 주문 내역을 조회했습니다.", orderService.findMyOrders(buyerId));
    }

    @LoginRequired
    @GetMapping("/orders/{orderId}")
    public ApiResponse<?> findById(@PathVariable Long orderId) {
        return ApiResponse.ok("주문 상세 정보를 조회했습니다.", orderService.findById(orderId));
    }

    @LoginRequired(role = "SELLER")
    @GetMapping("/seller/orders")
    public ApiResponse<?> findSellerOrders(@LoginUser Long sellerId) {
        return ApiResponse.ok("판매 내역을 조회했습니다.", orderService.findSellerOrders(sellerId));
    }

    @LoginRequired(role = "SELLER")
    @PatchMapping("/seller/orders/{orderId}/status")
    public ApiResponse<?> updateStatus(@LoginUser Long sellerId,
                                       @PathVariable Long orderId,
                                       @Valid @RequestBody OrderStatusRequest request) {
        return ApiResponse.ok("주문 상태를 변경했습니다.",
                orderService.updateStatus(sellerId, orderId, request.getStatus()));
    }
}
