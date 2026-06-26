package com.freshgrowth.common.auth;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * 이 핸들러는 인증(X-USER-ID)이 필요함을 표시한다.
 * role 을 지정하면 해당 역할만 접근 가능(아니면 403).
 */
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface LoginRequired {
    String role() default ""; // "" = 역할 무관, "SELLER" | "BUYER"
}
