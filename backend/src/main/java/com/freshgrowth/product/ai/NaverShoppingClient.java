package com.freshgrowth.product.ai;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.freshgrowth.product.ai.dto.CompetitorPrice;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

import java.net.URI;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 네이버 쇼핑 검색 API 호출. 상품명으로 검색해 컬리 등 여러 몰의 유사상품 최저가(lprice)를 받아
 * '경쟁 소매가' 근거로 쓴다. client-id/secret은 application-local.yml에서 주입(로그 비노출).
 * 같은 쿼리는 30분 캐시(경쟁 소매가는 분 단위로 안 변함, 호출 한도 절약).
 */
@Component
public class NaverShoppingClient {
    private static final long TTL_MS = 30 * 60 * 1000L; // 30분
    private static final int DISPLAY = 20;              // 한 쿼리당 최대 수집 건수

    private final String baseUrl;
    private final String clientId;
    private final String clientSecret;
    private final boolean configured;
    private final RestClient rest = RestClient.create();
    private final ObjectMapper om = new ObjectMapper();

    private final Map<String, Cached> cache = new ConcurrentHashMap<>();

    private record Cached(List<CompetitorPrice> items, long at) {}

    public NaverShoppingClient(@Value("${naver.shopping.base-url:}") String baseUrl,
                               @Value("${naver.shopping.client-id:}") String clientId,
                               @Value("${naver.shopping.client-secret:}") String clientSecret) {
        this.baseUrl = baseUrl;
        this.clientId = clientId == null ? "" : clientId.trim();
        this.clientSecret = clientSecret == null ? "" : clientSecret.trim();
        this.configured = baseUrl != null && !baseUrl.isBlank()
                && !this.clientId.isBlank() && !this.clientId.startsWith("<")
                && !this.clientSecret.isBlank() && !this.clientSecret.startsWith("<");
    }

    public boolean isConfigured() {
        return configured;
    }

    /** 상품명으로 유사상품 검색 → 최저가순 결과(캐시). 미설정·실패 시 빈 목록. */
    public List<CompetitorPrice> search(String query) {
        if (!configured || query == null || query.isBlank()) {
            return List.of();
        }
        String key = query.trim();
        long now = System.currentTimeMillis();
        Cached c = cache.get(key);
        if (c != null && now - c.at() < TTL_MS) {
            return c.items();
        }
        List<CompetitorPrice> parsed = parse(fetch(key));
        cache.put(key, new Cached(parsed, now));
        return parsed;
    }

    private String fetch(String query) {
        String url = baseUrl
                + "?query=" + enc(query)
                + "&display=" + DISPLAY
                + "&sort=sim"; // 정확도순(유사상품 우선)
        try {
            return rest.get()
                    .uri(URI.create(url))
                    .header("X-Naver-Client-Id", clientId)
                    .header("X-Naver-Client-Secret", clientSecret)
                    .retrieve()
                    .body(String.class);
        } catch (Exception e) {
            // 키/한도/네트워크 오류는 치명적 아님 → 경쟁가 없이 KAMIS만으로 폴백
            return null;
        }
    }

    private List<CompetitorPrice> parse(String json) {
        List<CompetitorPrice> list = new ArrayList<>();
        if (json == null) {
            return list;
        }
        try {
            JsonNode items = om.readTree(json).get("items");
            if (items == null || !items.isArray()) {
                return list;
            }
            for (JsonNode n : items) {
                Integer price = num(text(n, "lprice"));
                if (price == null || price <= 0) {
                    continue;
                }
                list.add(new CompetitorPrice(
                        stripTags(text(n, "title")),
                        text(n, "mallName"),
                        price,
                        text(n, "link"),
                        text(n, "image"),
                        text(n, "brand")));
            }
        } catch (Exception ignore) {
            // 파싱 실패 → 빈 목록
        }
        return list;
    }

    /** 네이버 title은 <b>검색어</b> 식 태그를 포함 → 제거. */
    private static String stripTags(String s) {
        return s == null ? null : s.replaceAll("<[^>]+>", "").trim();
    }

    private String text(JsonNode n, String field) {
        JsonNode v = n.get(field);
        return v == null ? null : v.asText();
    }

    private Integer num(String s) {
        if (s == null) {
            return null;
        }
        String cleaned = s.replaceAll("[,\\s]", "");
        if (cleaned.isEmpty() || cleaned.equals("-")) {
            return null;
        }
        try {
            return Integer.parseInt(cleaned);
        } catch (NumberFormatException e) {
            return null;
        }
    }

    private String enc(String value) {
        return value == null ? "" : URLEncoder.encode(value, StandardCharsets.UTF_8);
    }
}
