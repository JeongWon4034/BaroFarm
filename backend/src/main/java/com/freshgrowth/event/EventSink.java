package com.freshgrowth.event;

/**
 * 행동 이벤트의 저장처 추상화 — 수집(emit·수신)과 적재 방식을 분리하는 이음새.
 * <p>
 * 현재 기본 구현은 {@link MySqlEventSink}(MySQL 테이블 적재)이며,
 * 추후 트래픽이 커지거나 스트리밍이 필요하면 이 인터페이스의 구현체만
 * MongoDB 적재 / Kafka producer 로 교체한다. Controller·Service 는 건드리지 않는다.
 */
public interface EventSink {
    void save(BehaviorEvent event);
}
