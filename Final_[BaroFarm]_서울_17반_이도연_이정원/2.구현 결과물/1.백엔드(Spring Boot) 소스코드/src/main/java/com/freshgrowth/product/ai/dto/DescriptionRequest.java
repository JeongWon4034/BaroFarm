package com.freshgrowth.product.ai.dto;

import jakarta.validation.constraints.NotBlank;
import java.time.LocalDate;

public class DescriptionRequest {
    @NotBlank
    private String name;
    private String category;
    private LocalDate expirationDate; // 유통기한 → D-day 도메인 데이터
    private Integer stockQty;

    public String getName() { return name; }
    public String getCategory() { return category; }
    public LocalDate getExpirationDate() { return expirationDate; }
    public Integer getStockQty() { return stockQty; }
}
