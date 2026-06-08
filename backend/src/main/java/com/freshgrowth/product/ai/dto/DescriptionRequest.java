package com.freshgrowth.product.ai.dto;

import jakarta.validation.constraints.NotBlank;

public class DescriptionRequest {
    @NotBlank
    private String name;
    private String category;

    public String getName() { return name; }
    public String getCategory() { return category; }
}
