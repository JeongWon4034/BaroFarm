package com.freshgrowth.product.ai;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

import java.util.List;
import java.util.Map;

/**
 * 식약처 「조리식품의 레시피 DB」(COOKRCP01) 호출.
 * 실제 요리명·재료·조리단계·완성/단계 이미지를 제공한다.
 * 인증키는 recipe.api-key(env RECIPE_API_KEY)에서 주입. 기본값 'sample'은 5건만 반환(데모용).
 * 전체(약 1,100건)는 foodsafetykorea.go.kr 무료 인증키 발급 후 .env에 넣으면 된다.
 */
@Component
public class RecipeApiClient {
    private final RestClient rest;
    private final String key;

    public RecipeApiClient(
            @Value("${recipe.api-key:sample}") String key,
            @Value("${recipe.base-url:http://openapi.foodsafetykorea.go.kr/api}") String baseUrl) {
        this.key = (key == null || key.isBlank()) ? "sample" : key.trim();
        this.rest = RestClient.builder().baseUrl(baseUrl).build();
    }

    /** start~end 범위의 레시피 행 목록(요리명·재료·단계·이미지 필드 포함). 실패 시 빈 목록. */
    @SuppressWarnings("unchecked")
    public List<Map<String, Object>> fetch(int start, int end) {
        try {
            Map<String, Object> resp = rest.get()
                    .uri("/{key}/COOKRCP01/json/{start}/{end}", key, start, end)
                    .retrieve()
                    .body(Map.class);
            Map<String, Object> root = resp == null ? null : (Map<String, Object>) resp.get("COOKRCP01");
            if (root == null) return List.of();
            List<Map<String, Object>> rows = (List<Map<String, Object>>) root.get("row");
            return rows == null ? List.of() : rows;
        } catch (Exception e) {
            return List.of();
        }
    }
}
