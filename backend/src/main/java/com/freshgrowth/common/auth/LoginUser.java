package com.freshgrowth.common.auth;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * 인증된 사용자 id(Long)를 컨트롤러 파라미터로 주입한다.
 * AuthInterceptor가 검증 후 넣어둔 값을 꺼내 쓴다. (@RequestHeader("X-USER-ID") 대체)
 */
@Target(ElementType.PARAMETER)
@Retention(RetentionPolicy.RUNTIME)
public @interface LoginUser {
}
