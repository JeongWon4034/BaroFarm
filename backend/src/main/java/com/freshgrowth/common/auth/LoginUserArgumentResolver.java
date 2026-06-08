package com.freshgrowth.common.auth;

import com.freshgrowth.common.AppException;
import org.springframework.core.MethodParameter;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Component;
import org.springframework.web.bind.support.WebDataBinderFactory;
import org.springframework.web.context.request.NativeWebRequest;
import org.springframework.web.context.request.RequestAttributes;
import org.springframework.web.method.support.HandlerMethodArgumentResolver;
import org.springframework.web.method.support.ModelAndViewContainer;

/**
 * @LoginUser Long userId 파라미터에 AuthInterceptor가 검증해둔 userId를 주입한다.
 */
@Component
public class LoginUserArgumentResolver implements HandlerMethodArgumentResolver {

    @Override
    public boolean supportsParameter(MethodParameter parameter) {
        return parameter.hasParameterAnnotation(LoginUser.class)
                && parameter.getParameterType().equals(Long.class);
    }

    @Override
    public Object resolveArgument(MethodParameter parameter, ModelAndViewContainer mavContainer,
                                  NativeWebRequest webRequest, WebDataBinderFactory binderFactory) {
        Object userId = webRequest.getAttribute(AuthInterceptor.USER_ID_ATTR, RequestAttributes.SCOPE_REQUEST);
        if (userId == null) {
            // @LoginUser는 @LoginRequired와 함께 써야 한다. 누락 시에도 안전하게 401.
            throw new AppException(HttpStatus.UNAUTHORIZED, "UNAUTHORIZED", "로그인이 필요합니다.");
        }
        return userId;
    }
}
