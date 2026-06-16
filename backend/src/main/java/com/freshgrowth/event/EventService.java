package com.freshgrowth.event;

import com.freshgrowth.event.dto.EventRequest;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;

@Service
public class EventService {
    private final EventSink eventSink;

    public EventService(EventSink eventSink) {
        this.eventSink = eventSink;
    }

    /**
     * 행동 이벤트 1건 수집. userId 는 선택적 인증 결과(비로그인 시 null).
     * 발생 시각은 서버에서 stamp 한다(클라이언트 시계 불신).
     */
    public void record(EventRequest request, Long userId) {
        BehaviorEvent event = new BehaviorEvent();
        event.setSessionId(request.getSessionId());
        event.setUserId(userId);
        event.setEventType(request.getEventType());
        event.setProductId(request.getProductId());
        event.setAbTestGroup(request.getAbTestGroup());
        event.setDeviceType(request.getDeviceType());
        event.setStayDuration(request.getStayDuration());
        event.setOccurredAt(LocalDateTime.now());
        eventSink.save(event);
    }
}
