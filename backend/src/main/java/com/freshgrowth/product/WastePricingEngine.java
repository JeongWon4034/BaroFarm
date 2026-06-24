package com.freshgrowth.product;

import org.springframework.stereotype.Component;

import java.time.LocalDate;
import java.time.temporal.ChronoUnit;

/**
 * 폐기위험 + 동적 할인가 산출 엔진 (MVP: 규칙 기반).
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
        if (p == null) {
            return;
        }
        Pricing r = compute(p.getExpirationDate(), p.getStockQty(), p.getPrice());
        if (r == null) {
            return;
        }
        p.setDaysToExpiry(r.daysToExpiry);
        p.setRiskLevel(r.riskLevel);
        p.setRiskScore(r.riskScore);
        p.setDiscountRate(r.discountRate);
        p.setDiscountedPrice(r.discountedPrice);
    }

    /** lot(폐기기간 옵션) 단위 동적가격 — Product 와 동일 규칙을 lot 의 유통기한·재고·정가에 적용. */
    public void apply(ProductLot lot) {
        if (lot == null) {
            return;
        }
        Pricing r = compute(lot.getExpirationDate(), lot.getStockQty(), lot.getPrice());
        if (r == null) {
            return;
        }
        lot.setDaysToExpiry(r.daysToExpiry);
        lot.setRiskLevel(r.riskLevel);
        lot.setRiskScore(r.riskScore);
        lot.setDiscountRate(r.discountRate);
        lot.setDiscountedPrice(r.discountedPrice);
    }

    /** 산출값 묶음 (Product/ProductLot 공통 계산 결과). */
    public static final class Pricing {
        public final int daysToExpiry;
        public final String riskLevel;
        public final double riskScore;
        public final int discountRate;
        public final int discountedPrice;
        Pricing(int d, String lvl, double score, int rate, int price) {
            this.daysToExpiry = d; this.riskLevel = lvl; this.riskScore = score;
            this.discountRate = rate; this.discountedPrice = price;
        }
    }

    /** 유통기한·재고·정가만으로 폐기위험/할인가 계산. 입력 부족 시 null. */
    public Pricing compute(LocalDate expirationDate, Integer stockQty, Integer price) {
        if (expirationDate == null || price == null) {
            return null;
        }
        long d = ChronoUnit.DAYS.between(LocalDate.now(), expirationDate);
        if (d < 0) {                                   // 유통기한 경과 → 판매 대상 아님
            return new Pricing((int) d, "EXPIRED", 1.0, 0, price);
        }
        double urgency = clamp((SAFE_DAYS - d) / (double) SAFE_DAYS, 0, 1);
        int stock = stockQty == null ? 0 : stockQty;
        double stockPressure = clamp(stock / (double) HIGH_STOCK, 0, 1);

        double risk = URGENCY_WEIGHT * urgency + STOCK_WEIGHT * stockPressure;
        String level = risk >= 0.6 ? "HIGH" : risk >= 0.3 ? "MEDIUM" : "LOW";

        int rate = 0;
        if (risk >= DISCOUNT_FLOOR) {
            double scaled = (risk - DISCOUNT_FLOOR) / (1 - DISCOUNT_FLOOR);
            rate = (int) Math.round(clamp(scaled, 0, 1) * MAX_DISCOUNT);
        }
        int discounted = Math.max((int) (Math.round(price * (1 - rate / 100.0) / 100.0) * 100), 0);
        return new Pricing((int) d, level, round2(risk), rate, discounted);
    }

    private static double clamp(double v, double lo, double hi) {
        return Math.max(lo, Math.min(hi, v));
    }

    private static double round2(double v) {
        return Math.round(v * 100) / 100.0;
    }
}
