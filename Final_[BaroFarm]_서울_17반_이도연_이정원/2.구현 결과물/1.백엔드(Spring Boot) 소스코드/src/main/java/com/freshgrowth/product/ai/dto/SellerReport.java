package com.freshgrowth.product.ai.dto;

import java.util.List;

/** 판매자 AI 요약 리포트 + 요약에 사용된 도메인 데이터(usedData) */
public class SellerReport {
    private String summary;
    private List<String> usedData;

    public String getSummary() { return summary; }
    public void setSummary(String summary) { this.summary = summary; }
    public List<String> getUsedData() { return usedData; }
    public void setUsedData(List<String> usedData) { this.usedData = usedData; }
}
