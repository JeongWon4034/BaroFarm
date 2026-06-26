package com.freshgrowth.post.ai.dto;

import java.time.LocalDate;
import java.util.List;

/**
 * 게시판 상단 'AI 식료품 트렌드 카드'에 내려줄 데이터.
 * available=false 면 (AI/KAMIS 미설정 등) 프론트에서 카드를 숨긴다.
 */
public class MarketTrend {
    private boolean available;     // 카드 노출 여부
    private String summary;        // LLM이 생성한 트렌드 분석 글
    private List<TrendItem> risers;  // 한 달 전 대비 많이 오른 품목
    private List<TrendItem> fallers; // 한 달 전 대비 많이 내린 품목
    private String basis;          // 데이터 근거(예: KAMIS 소매 시세 · 한 달 전 대비 · N개 품목)
    private LocalDate generatedOn; // 생성일(하루 1회 캐시)

    public boolean isAvailable() { return available; }
    public void setAvailable(boolean available) { this.available = available; }
    public String getSummary() { return summary; }
    public void setSummary(String summary) { this.summary = summary; }
    public List<TrendItem> getRisers() { return risers; }
    public void setRisers(List<TrendItem> risers) { this.risers = risers; }
    public List<TrendItem> getFallers() { return fallers; }
    public void setFallers(List<TrendItem> fallers) { this.fallers = fallers; }
    public String getBasis() { return basis; }
    public void setBasis(String basis) { this.basis = basis; }
    public LocalDate getGeneratedOn() { return generatedOn; }
    public void setGeneratedOn(LocalDate generatedOn) { this.generatedOn = generatedOn; }
}
