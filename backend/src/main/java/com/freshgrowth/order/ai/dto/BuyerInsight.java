package com.freshgrowth.order.ai.dto;

import java.util.List;

/** 구매자 '내 구매 분석' 대시보드용 AI 인사이트 (요약 + 추천 + 참고 데이터). */
public class BuyerInsight {
    private String summary;                  // LLM이 생성한 구매 패턴 한두 문단 요약
    private List<String> recommendations;    // LLM이 생성한 다음 장보기 추천 상품 3개
    private String spendingType;             // LLM이 분류한 소비 성향 라벨 (예: "신선채소 마니아")
    private List<String> usedData;           // AI가 참고한 집계 데이터(투명성 표시용)

    public String getSummary() { return summary; }
    public void setSummary(String summary) { this.summary = summary; }
    public List<String> getRecommendations() { return recommendations; }
    public void setRecommendations(List<String> recommendations) { this.recommendations = recommendations; }
    public String getSpendingType() { return spendingType; }
    public void setSpendingType(String spendingType) { this.spendingType = spendingType; }
    public List<String> getUsedData() { return usedData; }
    public void setUsedData(List<String> usedData) { this.usedData = usedData; }
}
