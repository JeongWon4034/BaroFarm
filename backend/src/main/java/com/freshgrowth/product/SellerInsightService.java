package com.freshgrowth.product;

import com.freshgrowth.common.AppException;
import com.freshgrowth.order.OrderService;
import com.freshgrowth.order.dto.ProductSales;
import com.freshgrowth.product.ai.ProductAiService;
import com.freshgrowth.product.ai.dto.KamisItem;
import com.freshgrowth.product.ai.dto.ProductAction;
import com.freshgrowth.product.ai.dto.ProductInsight;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 판매자 상품 표 인사이트 — KAMIS 기준 소매가 · 현재 판매가 · 추천 판매가 + 판매 정체 신호를 조립한다.
 * 표 로드는 LLM 없이 KAMIS 캐시 조회만으로 빠르게, 정체 상품의 구체적 행동 추천은 hover 시 LLM으로.
 */
@Service
public class SellerInsightService {
    private static final int STALE_DAYS = 7; // 이 일수 이상 미판매 + 재고 있으면 '정체'

    private final ProductService productService;
    private final OrderService orderService;
    private final ProductAiService productAiService;

    public SellerInsightService(ProductService productService, OrderService orderService,
                                ProductAiService productAiService) {
        this.productService = productService;
        this.orderService = orderService;
        this.productAiService = productAiService;
    }

    public List<ProductInsight> insights(Long sellerId) {
        List<Product> products = productService.findSellerProducts(sellerId);
        Map<Long, String> lastSale = new HashMap<>();
        for (ProductSales s : orderService.sellerProductSales(sellerId)) {
            lastSale.put(s.getProductId(), s.getLastOrderDate());
        }
        LocalDate today = LocalDate.now();

        List<ProductInsight> out = new ArrayList<>(products.size());
        for (Product p : products) {
            ProductInsight in = new ProductInsight();
            in.setProductId(p.getProductId());

            int current = p.getDiscountedPrice() != null ? p.getDiscountedPrice() : p.getPrice();
            in.setCurrentPrice(current);

            KamisItem k = productAiService.kamisMatch(p.getName(), p.getCategory());
            Integer kamisPrice = (k != null) ? k.getPrice() : null;
            in.setKamisPrice(kamisPrice);
            if (k != null) {
                in.setKamisItem(k.getItemName());
                in.setKamisUnit(k.getUnit());
            }

            String last = lastSale.get(p.getProductId());
            Integer daysSinceLastSale = (last == null) ? null
                    : (int) ChronoUnit.DAYS.between(LocalDate.parse(last), today);
            in.setDaysSinceLastSale(daysSinceLastSale);
            in.setNeverSold(last == null);

            Integer daysListed = (p.getCreatedAt() == null) ? null
                    : (int) ChronoUnit.DAYS.between(p.getCreatedAt().toLocalDate(), today);
            in.setDaysListed(daysListed);

            int stock = p.getStockQty() == null ? 0 : p.getStockQty();
            Integer idle = (last == null) ? daysListed : daysSinceLastSale;
            boolean stale = stock > 0 && idle != null && idle >= STALE_DAYS;
            in.setStale(stale);

            // 추천가(규칙): 정체면 더 공격적으로(0.85), 아니면 시세 대비 5%↓. 시세 없고 양호하면 현재가 유지.
            int base = kamisPrice != null ? kamisPrice : current;
            int rec = (!stale && kamisPrice == null) ? current : round100((int) (base * (stale ? 0.85 : 0.95)));
            in.setRecommendedPrice(rec);

            out.add(in);
        }
        return out;
    }

    /** 정체 상품 행동 추천(hover) — 본인 상품만. */
    public ProductAction action(Long sellerId, Long productId) {
        Product p = productService.findById(productId);
        if (p == null) {
            throw new AppException(HttpStatus.NOT_FOUND, "PRODUCT_NOT_FOUND", "상품을 찾을 수 없습니다.");
        }
        if (!sellerId.equals(p.getSellerId())) {
            throw new AppException(HttpStatus.FORBIDDEN, "FORBIDDEN", "본인 상품만 조회할 수 있습니다.");
        }

        LocalDate today = LocalDate.now();
        String last = null;
        for (ProductSales s : orderService.sellerProductSales(sellerId)) {
            if (s.getProductId().equals(productId)) { last = s.getLastOrderDate(); break; }
        }
        boolean neverSold = (last == null);
        Integer daysNoSale = neverSold
                ? (p.getCreatedAt() == null ? null : (int) ChronoUnit.DAYS.between(p.getCreatedAt().toLocalDate(), today))
                : (int) ChronoUnit.DAYS.between(LocalDate.parse(last), today);

        return productAiService.profitAction(p, daysNoSale, neverSold);
    }

    private static int round100(int v) {
        return Math.max((int) (Math.round(v / 100.0) * 100), 100);
    }
}
