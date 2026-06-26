package com.freshgrowth.order;

import com.freshgrowth.common.AppException;
import org.springframework.http.HttpStatus;

/**
 * 주문 처리 상태 — 판매자가 정방향으로만 전이시킨다.
 * PENDING(결제완료·확인대기) → CONFIRMED(주문확인) → SHIPPING(배송중) → COMPLETED(배송완료).
 * 역방향·건너뛰기·취소는 허용하지 않는다(요구사항: 정방향 4단계).
 */
public enum OrderStatus {
    PENDING, CONFIRMED, SHIPPING, COMPLETED;

    /** 다음 단계(마지막 COMPLETED 는 null). */
    public OrderStatus next() {
        switch (this) {
            case PENDING:   return CONFIRMED;
            case CONFIRMED: return SHIPPING;
            case SHIPPING:  return COMPLETED;
            default:        return null;
        }
    }

    /** 문자열 → enum. 알 수 없는 값이면 400. */
    public static OrderStatus from(String raw) {
        try {
            return OrderStatus.valueOf(raw);
        } catch (IllegalArgumentException | NullPointerException e) {
            throw new AppException(HttpStatus.BAD_REQUEST, "INVALID_ORDER_STATUS",
                    "알 수 없는 주문 상태입니다: " + raw);
        }
    }
}
