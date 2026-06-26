package com.freshgrowth.review.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;

public class ReviewUpdateRequest {
    @NotNull @Min(1) @Max(5)
    private Integer rating;
    private String content;

    public Integer getRating() { return rating; }
    public String getContent() { return content; }
}
