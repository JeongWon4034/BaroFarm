package com.freshgrowth;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@MapperScan("com.freshgrowth")
@SpringBootApplication
@EnableScheduling
public class FreshGrowthApplication {
    public static void main(String[] args) {
        SpringApplication.run(FreshGrowthApplication.class, args);
    }
}
