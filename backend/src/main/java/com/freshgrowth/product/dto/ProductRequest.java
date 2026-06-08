package com.freshgrowth.product.dto;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import java.time.LocalDate;

public class ProductRequest {
    @NotBlank
    private String name;
    private String description;
    private String category;
    @NotNull @Min(0)
    private Integer price;
    @NotNull @Min(0)
    private Integer stockQty;
    private String thumbnailUrl;
    private LocalDate expirationDate;

    public String getName() { return name; }
    public String getDescription() { return description; }
    public String getCategory() { return category; }
    public Integer getPrice() { return price; }
    public Integer getStockQty() { return stockQty; }
    public String getThumbnailUrl() { return thumbnailUrl; }
    public LocalDate getExpirationDate() { return expirationDate; }
}
