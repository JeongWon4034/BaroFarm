package com.freshgrowth.order.ai.dto;

import java.util.List;

/** 구매자 '내 구매 분석' 대시보드용 AI 인사이트 (요약 + 참고 데이터). */
public class BuyerInsight {
    private String summary;          // LLM이 생성한 구매 패턴 한두 문단 요약
    private List<String> usedData;   // AI가 참고한 집계 데이터(투명성 표시용)

    public String getSummary() { return summary; }
    public void setSummary(String summary) { this.summary = summary; }
    public List<String> getUsedData() { return usedData; }
    public void setUsedData(List<String> usedData) { this.usedData = usedData; }
}
