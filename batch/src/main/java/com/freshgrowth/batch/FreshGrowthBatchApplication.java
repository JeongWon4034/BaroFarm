package com.freshgrowth.batch;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication
@MapperScan("com.freshgrowth.batch.dao")
@EnableScheduling
public class FreshGrowthBatchApplication {

    public static void main(String[] args) {
        SpringApplication.run(FreshGrowthBatchApplication.class, args);
    }
}
