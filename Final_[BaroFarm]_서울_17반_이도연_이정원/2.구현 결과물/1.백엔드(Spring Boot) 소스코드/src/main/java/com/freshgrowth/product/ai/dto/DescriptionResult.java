package com.freshgrowth.product.ai.dto;

import java.util.List;

/** AI 설명 + 프롬프트에 실제로 넣은 도메인 데이터(usedContext)를 함께 반환 */
public class DescriptionResult {
    private String description;
    private List<String> usedContext;

    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    public List<String> getUsedContext() { return usedContext; }
    public void setUsedContext(List<String> usedContext) { this.usedContext = usedContext; }
}
