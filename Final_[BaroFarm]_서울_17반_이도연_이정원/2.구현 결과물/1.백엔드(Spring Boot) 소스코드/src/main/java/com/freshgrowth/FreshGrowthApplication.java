package com.freshgrowth;

import org.apache.ibatis.annotations.Mapper;
import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

// @Mapper 가 붙은 인터페이스만 매퍼로 등록한다.
// (EventSink 같은 일반 비즈니스 인터페이스가 매퍼로 오인 등록되는 것을 방지)
@MapperScan(value = "com.freshgrowth", annotationClass = Mapper.class)
@SpringBootApplication
@EnableScheduling
public class FreshGrowthApplication {
    public static void main(String[] args) {
        SpringApplication.run(FreshGrowthApplication.class, args);
    }
}
