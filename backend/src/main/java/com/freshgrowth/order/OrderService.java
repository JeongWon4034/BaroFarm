package com.freshgrowth.order;

import com.freshgrowth.challenge.ChallengeService;
import com.freshgrowth.common.AppException;
import com.freshgrowth.order.dto.OrderRequest;
import com.freshgrowth.product.Product;
import com.freshgrowth.product.ProductMapper;
import com.freshgrowth.product.WastePricingEngine;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;

@Service
public class OrderService {
    private final OrderMapper orderMapper;
    private final ProductMapper productMapper;
    private final WastePricingEngine pricingEngine;
    private final ChallengeService challengeService;

    public OrderService(OrderMapper orderMapper, ProductMapper productMapper,
                        WastePricingEngine pricingEngine, ChallengeService challengeService) {
        this.orderMapper = orderMapper;
        this.productMapper = productMapper;
        this.pricingEngine = pricingEngine;
        this.challengeService = challengeService;
    }

    @Transactional
    public Order create(Long buyerId, OrderRequest request) {
        Product product = productMapper.findById(request.getProductId());
        if (product == null) {
            throw new AppException(HttpStatus.NOT_FOUND, "PRODUCT_NOT_FOUND", "상품을 찾을 수 없습니다.");
        }

        // 폐기위험·떨이가 계산(서버 권위) — 유통기한 지난 상품은 재고 차감 전에 차단한다.
        pricingEngine.apply(product);
        if ("EXPIRED".equals(product.getRiskLevel())) {
            throw new AppException(HttpStatus.BAD_REQUEST, "PRODUCT_EXPIRED", "유통기한이 지나 구매할 수 없는 상품입니다.");
        }

        int updated = productMapper.decreaseStock(request.getProductId(), request.getQuantity());
        if (updated == 0) {
            throw new AppException(HttpStatus.BAD_REQUEST, "OUT_OF_STOCK", "재고가 부족합니다.");
        }

        // 결제 금액은 서버가 동적 떨이가로 재계산한다(클라이언트 가격 신뢰 안 함).
        int unitPrice = product.getDiscountedPrice() != null ? product.getDiscountedPrice() : product.getPrice();

        Order order = new Order();
        order.setBuyerId(buyerId);
        order.setProductId(request.getProductId());
        order.setQuantity(request.getQuantity());
        order.setTotalPrice(unitPrice * request.getQuantity());
        // 주문 시점 정가를 함께 박아둔다 — 이후 상품가가 바뀌어도 절약액/회수 매출을 정확히 산출.
        order.setOriginalUnitPrice(product.getPrice());
        // 결제 직후엔 판매자 확인 대기 상태. 이후 판매자가 CONFIRMED→SHIPPING→COMPLETED 로 전이한다.
        order.setStatus(OrderStatus.PENDING.name());
        orderMapper.insert(order);

        // 마감임박(떨이) 상품 구매면 폐기 절감 챌린지 진행도 반영
        if (product.getDiscountRate() != null && product.getDiscountRate() > 0) {
            challengeService.recordDeadlinePurchase(buyerId);
        }

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

    /**
     * 판매자가 주문 상태를 다음 단계로 전이시킨다.
     * - 본인 상품의 주문만(403), 존재하는 주문만(404)
     * - 전이는 정방향 1단계만 허용(현재 상태의 next() 와 일치해야 함, 아니면 400)
     */
    @Transactional
    public Order updateStatus(Long sellerId, Long orderId, String targetStatusRaw) {
        Order order = orderMapper.findById(orderId);
        if (order == null) {
            throw new AppException(HttpStatus.NOT_FOUND, "ORDER_NOT_FOUND", "주문을 찾을 수 없습니다.");
        }
        if (!sellerId.equals(order.getSellerId())) {
            throw new AppException(HttpStatus.FORBIDDEN, "FORBIDDEN", "본인 상품의 주문만 처리할 수 있습니다.");
        }

        OrderStatus current = OrderStatus.from(order.getStatus());
        OrderStatus target = OrderStatus.from(targetStatusRaw);
        if (target != current.next()) {
            throw new AppException(HttpStatus.BAD_REQUEST, "INVALID_STATUS_TRANSITION",
                    current.name() + " 다음 단계로만 변경할 수 있습니다.");
        }

        orderMapper.updateStatus(orderId, target.name());
        return orderMapper.findById(orderId);
    }
}
