package com.freshgrowth.event.dto;

import jakarta.validation.constraints.NotBlank;

/**
 * 프론트 track() 이 보내는 행동 이벤트 페이로드.
 * 발생 시각은 클라이언트 시계를 신뢰하지 않고 서버에서 stamp 한다.
 */
public class EventRequest {
    @NotBlank
    private String sessionId;
    @NotBlank
    private String eventType;
    private Long productId;
    private String abTestGroup;
    private String deviceType;
    private Integer stayDuration;

    public String getSessionId() { return sessionId; }
    public void setSessionId(String sessionId) { this.sessionId = sessionId; }
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
}
