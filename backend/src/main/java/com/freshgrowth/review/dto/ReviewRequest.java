package com.freshgrowth.review.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;

public class ReviewRequest {
    @NotNull
    private Long orderId;
    @NotNull @Min(1) @Max(5)
    private Integer rating;
    private String content;

    public Long getOrderId() { return orderId; }
    public Integer getRating() { return rating; }
    public String getContent() { return content; }
}
