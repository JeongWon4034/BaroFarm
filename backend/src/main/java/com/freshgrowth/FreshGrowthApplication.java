package com.freshgrowth;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@MapperScan("com.freshgrowth")
@SpringBootApplication
public class FreshGrowthApplication {
    public static void main(String[] args) {
        SpringApplication.run(FreshGrowthApplication.class, args);
    }
}
