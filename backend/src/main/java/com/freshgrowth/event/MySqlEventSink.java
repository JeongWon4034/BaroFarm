package com.freshgrowth.event;

import org.springframework.stereotype.Component;

/**
 * 기본 EventSink — MySQL user_behavior_logs 테이블에 적재.
 * 분석 쿼리(퍼널/AB/체류시간)가 곧장 SQL 로 가능하다.
 */
@Component
public class MySqlEventSink implements EventSink {
    private final EventMapper eventMapper;

    public MySqlEventSink(EventMapper eventMapper) {
        this.eventMapper = eventMapper;
    }

    @Override
    public void save(BehaviorEvent event) {
        eventMapper.insert(event);
    }
}
