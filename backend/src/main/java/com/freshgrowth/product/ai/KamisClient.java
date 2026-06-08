package com.freshgrowth.product.ai;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.freshgrowth.common.AppException;
import com.freshgrowth.product.ai.dto.KamisItem;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

import java.net.URI;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

/**
 * KAMIS(농수산물유통정보, aT) 시세 API 호출.
 * 인증키(cert-key) + 인증ID(cert-id) 방식이며 둘 다 application-local.yml에서 주입(로그 비노출).
 * dailySalesList(소매/도매 일별)를 1시간 캐시하여 소매(01)만 파싱해 제공한다.
 */
@Component
public class KamisClient {
    private static final long TTL_MS = 60 * 60 * 1000L; // 1시간

    private final String baseUrl;
    private final String certKey;
    private final String certId;
    private final boolean configured;
    private final RestClient rest = RestClient.create();
    private final ObjectMapper om = new ObjectMapper();

    private volatile List<KamisItem> cache;
    private volatile long cachedAt;

    public KamisClient(@Value("${kamis.base-url:}") String baseUrl,
                       @Value("${kamis.cert-key:}") String certKey,
                       @Value("${kamis.cert-id:}") String certId) {
        this.baseUrl = baseUrl;
        this.certKey = certKey == null ? "" : certKey.trim();
        this.certId = certId == null ? "" : certId.trim();
        this.configured = baseUrl != null && !baseUrl.isBlank()
                && !this.certKey.isBlank() && !this.certKey.startsWith("<")
                && !this.certId.isBlank() && !this.certId.startsWith("<");
    }

    public boolean isConfigured() {
        return configured;
    }

    /** 소매 일별 시세 목록(캐시). */
    public List<KamisItem> getDailyRetail() {
        long now = System.currentTimeMillis();
        List<KamisItem> c = cache;
        if (c != null && now - cachedAt < TTL_MS) {
            return c;
        }
        List<KamisItem> parsed = parse(fetch("dailySalesList", ""));
        cache = parsed;
        cachedAt = now;
        return parsed;
    }

    /** KAMIS action 호출 → raw JSON (점검/확장용). */
    public String fetch(String action, String extraParams) {
        if (!configured) {
            throw new AppException(HttpStatus.SERVICE_UNAVAILABLE, "KAMIS_NOT_CONFIGURED",
                    "KAMIS 인증키/ID가 설정되지 않았습니다. application-local.yml에 kamis.cert-key / cert-id를 넣어주세요.");
        }
        String full = baseUrl
                + "?action=" + enc(action)
                + "&p_cert_key=" + enc(certKey)
                + "&p_cert_id=" + enc(certId)
                + "&p_returntype=json"
                + (extraParams == null ? "" : extraParams);
        try {
            return rest.get().uri(URI.create(full)).retrieve().body(String.class);
        } catch (Exception e) {
            throw new AppException(HttpStatus.BAD_GATEWAY, "KAMIS_ERROR", "KAMIS 시세 호출에 실패했습니다.");
        }
    }

    private List<KamisItem> parse(String json) {
        List<KamisItem> list = new ArrayList<>();
        try {
            JsonNode price = om.readTree(json).get("price");
            if (price == null || !price.isArray()) {
                return list;
            }
            for (JsonNode n : price) {
                if (!"01".equals(text(n, "product_cls_code"))) {
                    continue; // 소매만
                }
                KamisItem it = new KamisItem();
                it.setCategory(text(n, "category_name"));
                it.setItemName(text(n, "item_name"));
                it.setUnit(text(n, "unit"));
                it.setPrice(num(text(n, "dpr1")));
                it.setMonthAgo(num(text(n, "dpr3")));
                it.setYearAgo(num(text(n, "dpr4")));
                it.setChangeRate(text(n, "value"));
                if (it.getPrice() != null) {
                    list.add(it);
                }
            }
        } catch (Exception ignore) {
            // 파싱 실패 시 빈 목록 → 추천가는 자체 통계로 폴백
        }
        return list;
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
