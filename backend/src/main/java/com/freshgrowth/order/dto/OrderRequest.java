package com.freshgrowth.order.dto;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;

public class OrderRequest {
    @NotNull
    private Long productId;
    private Long lotId;          // 폐기기간 옵션 선택(권장). null 이면 상품단위(레거시) 구매
    @NotNull @Min(1)
    private Integer quantity;

    public Long getProductId() { return productId; }
    public Long getLotId() { return lotId; }
    public Integer getQuantity() { return quantity; }
}
