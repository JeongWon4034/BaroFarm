package com.freshgrowth.common.auth;

import org.springframework.stereotype.Component;

import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

/** 로그아웃된 토큰 무효화(인메모리). 재시작 시 비워짐 — 데모용. */
@Component
public class TokenBlacklist {
    private final Set<String> blacklisted = ConcurrentHashMap.newKeySet();

    public void add(String token) {
        blacklisted.add(token);
    }

    public boolean contains(String token) {
        return blacklisted.contains(token);
    }
}
