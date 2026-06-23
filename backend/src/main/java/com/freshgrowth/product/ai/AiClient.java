package com.freshgrowth.product.ai;

import com.freshgrowth.common.AppException;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

import java.util.List;
import java.util.Map;

/**
 * GMS(OpenAI 호환 프록시)를 통해 챗 모델을 호출한다.
 * base-url/api-key/model 은 application-local.yml(또는 환경변수)에서 주입되며 절대 로그에 남기지 않는다.
 */
@Component
public class AiClient {
    private final RestClient rest;
    private final String apiKey;
    private final String model;
    private final boolean configured;

    public AiClient(@Value("${ai.base-url:}") String baseUrl,
                    @Value("${ai.api-key:}") String apiKey,
                    @Value("${ai.model:gpt-4o-mini}") String model) {
        this.apiKey = apiKey == null ? "" : apiKey.trim();
        this.model = model;
        this.configured = baseUrl != null && !baseUrl.isBlank()
                && !this.apiKey.isBlank() && !this.apiKey.startsWith("<");
        this.rest = RestClient.builder().baseUrl(baseUrl == null ? "" : baseUrl.trim()).build();
    }

    public boolean isConfigured() {
        return configured;
    }

    @SuppressWarnings("unchecked")
    public String chat(String systemPrompt, String userPrompt, int maxTokens) {
        if (!configured) {
            throw new AppException(HttpStatus.SERVICE_UNAVAILABLE, "AI_NOT_CONFIGURED",
                    "AI가 설정되지 않았습니다. backend/application-local.yml에 GMS base-url/키를 넣어주세요.");
        }
        Map<String, Object> body = Map.of(
                "model", model,
                "messages", List.of(
                        Map.of("role", "system", "content", systemPrompt),
                        Map.of("role", "user", "content", userPrompt)
                ),
                "temperature", 0.7,
                "max_tokens", maxTokens
        );
        try {
            Map<String, Object> resp = rest.post()
                    .uri("/chat/completions")
                    .header("Authorization", "Bearer " + apiKey)
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(body)
                    .retrieve()
                    .body(Map.class);

            List<Map<String, Object>> choices = resp == null ? null : (List<Map<String, Object>>) resp.get("choices");
            if (choices == null || choices.isEmpty()) {
                throw new AppException(HttpStatus.BAD_GATEWAY, "AI_ERROR", "AI 응답이 비어 있습니다.");
            }
            Map<String, Object> message = (Map<String, Object>) choices.get(0).get("message");
            Object content = message == null ? null : message.get("content");
            if (content == null) {
                throw new AppException(HttpStatus.BAD_GATEWAY, "AI_ERROR", "AI 응답을 해석하지 못했습니다.");
            }
            return content.toString().trim();
        } catch (AppException e) {
            throw e;
        } catch (Exception e) {
            // 키/원문 오류는 노출하지 않는다
            throw new AppException(HttpStatus.BAD_GATEWAY, "AI_ERROR", "AI 호출에 실패했습니다.");
        }
    }

    /**
     * GMS 이미지 생성(gpt-image-1) → data URL(base64) 반환. 실패/미설정 시 null(치명적 아님).
     * 생성은 수 초~십수 초 걸리므로 호출부에서 캐시할 것.
     */
    @SuppressWarnings("unchecked")
    public String generateImage(String prompt) {
        if (!configured) return null;
        Map<String, Object> body = Map.of(
                "model", "gpt-image-1",
                "prompt", prompt,
                "n", 1,
                "size", "1024x1024",
                "quality", "low" // 생성 속도 우선(데모) — 고품질 필요 시 medium/high
        );
        try {
            Map<String, Object> resp = rest.post()
                    .uri("/images/generations")
                    .header("Authorization", "Bearer " + apiKey)
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(body)
                    .retrieve()
                    .body(Map.class);
            List<Map<String, Object>> data = resp == null ? null : (List<Map<String, Object>>) resp.get("data");
            if (data == null || data.isEmpty()) return null;
            Object b64 = data.get(0).get("b64_json");
            return b64 == null ? null : "data:image/png;base64," + b64;
        } catch (Exception e) {
            return null;
        }
    }
}
