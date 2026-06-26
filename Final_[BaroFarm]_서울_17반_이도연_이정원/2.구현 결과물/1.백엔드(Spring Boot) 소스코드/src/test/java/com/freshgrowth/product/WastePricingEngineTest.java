package com.freshgrowth.product;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.time.LocalDate;

import static org.assertj.core.api.Assertions.assertThat;

class WastePricingEngineTest {

    private WastePricingEngine engine;

    @BeforeEach
    void setUp() {
        engine = new WastePricingEngine();
    }

    // ── 헬퍼 ──────────────────────────────────────────────────────────────────

    private Product product(int price, int stock, LocalDate expiry) {
        Product p = new Product();
        p.setPrice(price);
        p.setStockQty(stock);
        p.setExpirationDate(expiry);
        return p;
    }

    // ── 기본값 보호 ───────────────────────────────────────────────────────────

    @Test
    @DisplayName("유통기한 null이면 계산 건너뜀 — discountedPrice null 유지")
    void skip_when_expirationDate_is_null() {
        Product p = product(10000, 10, null);
        engine.apply(p);
        assertThat(p.getDiscountedPrice()).isNull();
    }

    @Test
    @DisplayName("price null이면 계산 건너뜀")
    void skip_when_price_is_null() {
        Product p = new Product();
        p.setStockQty(10);
        p.setExpirationDate(LocalDate.now().plusDays(3));
        engine.apply(p);
        assertThat(p.getDiscountRate()).isNull();
    }

    // ── EXPIRED ──────────────────────────────────────────────────────────────

    @Test
    @DisplayName("유통기한 경과 → EXPIRED, 할인율 0, 가격 정가 유지")
    void expired_product() {
        Product p = product(10000, 5, LocalDate.now().minusDays(1));
        engine.apply(p);
        assertThat(p.getRiskLevel()).isEqualTo("EXPIRED");
        assertThat(p.getDiscountRate()).isEqualTo(0);
        assertThat(p.getDiscountedPrice()).isEqualTo(10000);
    }

    // ── 할인율 범위 ────────────────────────────────────────────────────────────

    @Test
    @DisplayName("할인율은 0 이상 60 이하")
    void discount_rate_bounded() {
        // 극단값: D-1, 재고 100 → 최고 위험
        Product high = product(10000, 100, LocalDate.now().plusDays(1));
        engine.apply(high);
        assertThat(high.getDiscountRate()).isBetween(0, 60);

        // 여유: D-30, 재고 1 → 낮은 위험
        Product low = product(10000, 1, LocalDate.now().plusDays(30));
        engine.apply(low);
        assertThat(low.getDiscountRate()).isBetween(0, 60);
    }

    // ── discountedPrice 계산 정확성 ──────────────────────────────────────────

    @Test
    @DisplayName("discountedPrice = price * (1 - rate/100), 100원 단위 반올림")
    void discounted_price_calculation() {
        Product p = product(10000, 30, LocalDate.now().plusDays(2));
        engine.apply(p);
        int rate = p.getDiscountRate();
        int expected = (int) (Math.round(10000 * (1 - rate / 100.0) / 100.0) * 100);
        assertThat(p.getDiscountedPrice()).isEqualTo(expected);
    }

    @Test
    @DisplayName("discountedPrice는 0 이상 — 음수 불가")
    void discounted_price_non_negative() {
        Product p = product(100, 1000, LocalDate.now().plusDays(1));
        engine.apply(p);
        assertThat(p.getDiscountedPrice()).isGreaterThanOrEqualTo(0);
    }

    // ── riskLevel 경계 ────────────────────────────────────────────────────────

    @Test
    @DisplayName("안전 기간(D+8 이상, 재고 소량) → LOW")
    void low_risk_for_safe_product() {
        Product p = product(5000, 2, LocalDate.now().plusDays(10));
        engine.apply(p);
        assertThat(p.getRiskLevel()).isEqualTo("LOW");
        assertThat(p.getDiscountRate()).isEqualTo(0);
        assertThat(p.getDiscountedPrice()).isEqualTo(5000);
    }

    @Test
    @DisplayName("D-1 + 재고 많음 → HIGH")
    void high_risk_for_imminent_expiry_and_large_stock() {
        Product p = product(8000, 60, LocalDate.now().plusDays(1));
        engine.apply(p);
        assertThat(p.getRiskLevel()).isEqualTo("HIGH");
        assertThat(p.getDiscountRate()).isGreaterThan(0);
    }

    // ── daysToExpiry ─────────────────────────────────────────────────────────

    @Test
    @DisplayName("daysToExpiry = 오늘로부터 남은 일수(정수)")
    void days_to_expiry_value() {
        Product p = product(3000, 10, LocalDate.now().plusDays(5));
        engine.apply(p);
        assertThat(p.getDaysToExpiry()).isEqualTo(5);
    }
}
