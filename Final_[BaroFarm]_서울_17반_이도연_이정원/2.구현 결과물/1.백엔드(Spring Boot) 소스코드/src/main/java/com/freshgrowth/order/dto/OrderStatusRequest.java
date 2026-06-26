package com.freshgrowth.order.dto;

import jakarta.validation.constraints.NotBlank;

/**
 * 판매자 주문 상태 변경 요청 — 전이 목표 상태(다음 단계)를 담는다.
 * 전이 규칙(정방향 1단계) 검증은 서버에서 수행한다(클라이언트 신뢰 안 함).
 */
public class OrderStatusRequest {
    @NotBlank
    private String status;

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
}
