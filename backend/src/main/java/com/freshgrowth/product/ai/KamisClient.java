package com.freshgrowth.product.ai;

import com.freshgrowth.common.AppException;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

import java.net.URI;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;

/**
 * KAMIS(농수산물유통정보, aT) 시세 API 호출.
 * 인증키(cert-key) + 인증ID(cert-id) 방식이며 둘 다 application-local.yml에서 주입(로그 비노출).
 * 실제 응답 구조 확인 후 파싱을 붙인다 — 우선 raw 조회용.
 */
@Component
public class KamisClient {
    private final String baseUrl;
    private final String certKey;
    private final String certId;
    private final boolean configured;
    private final RestClient rest = RestClient.create();

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

    /** KAMIS action 호출 → raw JSON. extraParams는 "&key=value" 형태로 이어붙임. */
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

    private String enc(String value) {
        return value == null ? "" : URLEncoder.encode(value, StandardCharsets.UTF_8);
    }
}
