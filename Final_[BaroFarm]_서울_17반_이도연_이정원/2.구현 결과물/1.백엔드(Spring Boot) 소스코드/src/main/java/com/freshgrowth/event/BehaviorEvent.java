package com.freshgrowth.event;

import java.time.LocalDateTime;

/**
 * 행동 로그 1건 (Layer 2 원천 데이터).
 * 퍼널·코호트·A/B 분석과 AI 수요예측 피처의 출발점이다.
 * user_id / product_id 는 비로그인·비상품 이벤트를 허용하기 위해 nullable.
 */
public class BehaviorEvent {
    private Long logId;
    private String sessionId;      // 1회 방문 세션 — 퍼널 분석 기준 키
    private Long userId;           // 비로그인 시 null
    private String eventType;      // view_home / click_product / view_detail / click_checkout / complete_order
    private Long productId;        // 이벤트 대상 상품 (없으면 null)
    private String abTestGroup;    // A_GROUP / B_GROUP
    private String deviceType;     // PC_WEB / MOBILE_WEB
    private Integer stayDuration;  // 페이지 체류 시간(초)
    private LocalDateTime occurredAt;
    private LocalDateTime createdAt;

    public Long getLogId() { return logId; }
    public void setLogId(Long logId) { this.logId = logId; }
    public String getSessionId() { return sessionId; }
    public void setSessionId(String sessionId) { this.sessionId = sessionId; }
    public Long getUserId() { return userId; }
    public void setUserId(Long userId) { this.userId = userId; }
    public String getEventType() { return eventType; }
    public void setEventType(String eventType) { this.eventType = eventType; }
    public Long getProductId() { return productId; }
    public void setProductId(Long productId) { this.productId = productId; }
    public String getAbTestGroup() { return abTestGroup; }
    public void setAbTestGroup(String abTestGroup) { this.abTestGroup = abTestGroup; }
    public String getDeviceType() { return deviceType; }
    public void setDeviceType(String deviceType) { this.deviceType = deviceType; }
    public Integer getStayDuration() { return stayDuration; }
    public void setStayDuration(Integer stayDuration) { this.stayDuration = stayDuration; }
    public LocalDateTime getOccurredAt() { return occurredAt; }
    public void setOccurredAt(LocalDateTime occurredAt) { this.occurredAt = occurredAt; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
}
