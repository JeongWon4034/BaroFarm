package com.freshgrowth.common;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class SwaggerConfig {
    @Bean
    public OpenAPI openAPI() {
        return new OpenAPI().info(new Info()
                .title("FreshGrowth Basic CRUD API")
                .description("Spring Boot + MyBatis + MySQL 기본 CRUD API")
                .version("v1"));
    }
}
