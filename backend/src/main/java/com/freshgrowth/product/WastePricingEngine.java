package com.freshgrowth.product;

import org.springframework.stereotype.Component;

import java.time.LocalDate;
import java.time.temporal.ChronoUnit;

/**
 * 폐기위험 + 동적 떨이가 산출 엔진 (MVP: 규칙 기반).
 *
 * 입력: 유통기한까지 남은 일수(D-day), 재고.
 *   (※ 수요예측 기반 판매속도 반영은 다음 단계 — 주문 데이터가 쌓이면 고도화)
 * 출력: daysToExpiry, riskScore(0~1), riskLevel(HIGH/MEDIUM/LOW/EXPIRED),
 *       discountRate(%), discountedPrice(100원 단위)
 *
 * 가중치/상한은 모두 상수로 분리 — 데모/정책에 따라 조정한다.
 */
@Component
public class WastePricingEngine {

    private static final int SAFE_DAYS = 7;            // 유통기한 7일 이상 남으면 임박도 0
    private static final int HIGH_STOCK = 50;          // 재고 압박 정규화 기준
    private static final double URGENCY_WEIGHT = 0.7;  // 임박도 가중치
    private static final double STOCK_WEIGHT = 0.3;    // 재고압박 가중치
    private static final int MAX_DISCOUNT = 60;        // 최대 할인율(%)
    private static final double DISCOUNT_FLOOR = 0.15; // 위험점수 이 미만이면 정가 유지

    public void apply(Product p) {
        if (p == null || p.getExpirationDate() == null || p.getPrice() == null) {
            return;
        }

        long d = ChronoUnit.DAYS.between(LocalDate.now(), p.getExpirationDate());
        p.setDaysToExpiry((int) d);

        // 이미 유통기한 경과 → 판매 대상 아님
        if (d < 0) {
            p.setRiskLevel("EXPIRED");
            p.setRiskScore(1.0);
            p.setDiscountRate(0);
            p.setDiscountedPrice(p.getPrice());
            return;
        }

        double urgency = clamp((SAFE_DAYS - d) / (double) SAFE_DAYS, 0, 1);
        int stock = p.getStockQty() == null ? 0 : p.getStockQty();
        double stockPressure = clamp(stock / (double) HIGH_STOCK, 0, 1);

        double risk = URGENCY_WEIGHT * urgency + STOCK_WEIGHT * stockPressure;
        p.setRiskScore(round2(risk));
        p.setRiskLevel(risk >= 0.6 ? "HIGH" : risk >= 0.3 ? "MEDIUM" : "LOW");

        int rate = 0;
        if (risk >= DISCOUNT_FLOOR) {
            double scaled = (risk - DISCOUNT_FLOOR) / (1 - DISCOUNT_FLOOR);
            rate = (int) Math.round(clamp(scaled, 0, 1) * MAX_DISCOUNT);
        }
        p.setDiscountRate(rate);

        int discounted = (int) (Math.round(p.getPrice() * (1 - rate / 100.0) / 100.0) * 100);
        p.setDiscountedPrice(Math.max(discounted, 0));
    }

    private static double clamp(double v, double lo, double hi) {
        return Math.max(lo, Math.min(hi, v));
    }

    private static double round2(double v) {
        return Math.round(v * 100) / 100.0;
    }
}
