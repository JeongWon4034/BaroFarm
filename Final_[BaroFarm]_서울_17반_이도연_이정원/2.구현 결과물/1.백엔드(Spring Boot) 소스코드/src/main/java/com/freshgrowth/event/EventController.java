package com.freshgrowth.event;

import com.freshgrowth.common.ApiResponse;
import com.freshgrowth.common.auth.JwtProvider;
import com.freshgrowth.event.dto.EventRequest;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;

/**
 * 행동 로그 수집 엔드포인트 — 공개(@LoginRequired 없음).
 * 비로그인 방문자도 퍼널 이벤트를 발생시키므로 인증은 선택적으로만 처리한다.
 */
@RestController
@RequestMapping("/api/v1")
public class EventController {
    private final EventService eventService;
    private final JwtProvider jwtProvider;

    public EventController(EventService eventService, JwtProvider jwtProvider) {
        this.eventService = eventService;
        this.jwtProvider = jwtProvider;
    }

    @PostMapping("/events")
    public ApiResponse<?> collect(@Valid @RequestBody EventRequest request,
                                  @RequestHeader(value = "Authorization", required = false) String authorization) {
        Long userId = jwtProvider.optionalUserId(authorization);
        eventService.record(request, userId);
        return ApiResponse.ok("이벤트를 수집했습니다.", null);
    }
}
