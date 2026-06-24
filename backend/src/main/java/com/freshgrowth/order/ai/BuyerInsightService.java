package com.freshgrowth.order.ai;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.freshgrowth.order.Order;
import com.freshgrowth.order.OrderService;
import com.freshgrowth.order.ai.dto.BuyerInsight;
import com.freshgrowth.order.ai.dto.RecommendedProduct;
import com.freshgrowth.product.Product;
import com.freshgrowth.product.ProductService;
import com.freshgrowth.product.ai.AiClient;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.YearMonth;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

/**
 * 구매자 주문 내역을 집계해 '내 구매 분석' AI 인사이트를 만든다.
 * 집계는 규칙 기반으로 계산하고, 그 결과를 GMS LLM에 넣어 자연어 요약을 생성한다.
 * (KPI·차트는 프론트가 /orders/my 로 직접 계산 — 판매자 대시보드와 동일 패턴)
 */
@Service
public class BuyerInsightService {
    private static final Map<String, String> CAT_KO = Map.of(
            "vegetable", "채소", "fruit", "과일", "seafood", "해산물", "meat", "육류",
            "grain", "곡물", "mushroom", "버섯", "root", "구근"
    );

    private final OrderService orderService;
    private final ProductService productService;
    private final AiClient aiClient;
    private final ObjectMapper objectMapper;

    public BuyerInsightService(OrderService orderService, ProductService productService,
                               AiClient aiClient, ObjectMapper objectMapper) {
        this.orderService = orderService;
        this.productService = productService;
        this.aiClient = aiClient;
        this.objectMapper = objectMapper;
    }

    public BuyerInsight generate(Long buyerId) {
        List<Order> orders = orderService.findMyOrders(buyerId);
        BuyerInsight insight = new BuyerInsight();

        if (orders.isEmpty()) {
            insight.setUsedData(List.of("구매 내역 0건"));
            insight.setSummary("아직 구매 내역이 없습니다. 첫 주문 후 구매 분석을 확인할 수 있어요.");
            return insight;
        }

        long totalSpend = 0;
        int totalQty = 0;
        long reviewed = 0;
        long savedAmount = 0;   // 할인으로 아낀 누적액 = Σ(정가×수량 − 실결제액)
        int rescuedCount = 0;   // 할인가로 구매해 폐기를 막은 주문 수
        Map<String, Long> byCategory = new LinkedHashMap<>();      // 표시용(한글 라벨)
        Map<String, Long> byCategoryCode = new LinkedHashMap<>();  // 후보 소싱용(원본 코드)
        Map<String, Long> byMonth = new LinkedHashMap<>();
        Map<String, Integer> byProduct = new LinkedHashMap<>();

        for (Order o : orders) {
            int price = o.getTotalPrice() == null ? 0 : o.getTotalPrice();
            totalSpend += price;
            totalQty += o.getQuantity() == null ? 0 : o.getQuantity();
            if (o.getReviewId() != null) reviewed++;

            // 주문 시점 정가가 실결제 단가보다 높으면 그 차액이 할인 절약분
            if (o.getOriginalUnitPrice() != null) {
                int qty = o.getQuantity() == null ? 0 : o.getQuantity();
                long saved = (long) o.getOriginalUnitPrice() * qty - price;
                if (saved > 0) {
                    savedAmount += saved;
                    rescuedCount++;
                }
            }

            String catKo = o.getCategory() == null ? "기타" : CAT_KO.getOrDefault(o.getCategory(), o.getCategory());
            byCategory.merge(catKo, (long) price, Long::sum);
            if (o.getCategory() != null) byCategoryCode.merge(o.getCategory(), (long) price, Long::sum);

            if (o.getOrderDate() != null) {
                String ym = YearMonth.from(o.getOrderDate()).toString();
                byMonth.merge(ym, (long) price, Long::sum);
            }
            if (o.getProductName() != null) {
                byProduct.merge(o.getProductName(), o.getQuantity() == null ? 1 : o.getQuantity(), Integer::sum);
            }
        }

        int count = orders.size();
        long avg = totalSpend / count;
        int reviewRate = (int) Math.round(reviewed * 100.0 / count);
        Map.Entry<String, Long> topCat = topEntry(byCategory);
        Map.Entry<String, Integer> topProduct = topEntry(byProduct);

        // 이번 달 vs 지난 달 지출
        YearMonth now = YearMonth.from(LocalDate.now());
        long thisMonth = byMonth.getOrDefault(now.toString(), 0L);
        long lastMonth = byMonth.getOrDefault(now.minusMonths(1).toString(), 0L);

        List<String> used = new ArrayList<>();
        used.add("총 구매 " + count + "건 · " + totalQty + "개");
        used.add("총 지출 " + won(totalSpend) + "원 (평균 주문액 " + won(avg) + "원)");
        if (topCat != null) {
            used.add("최다 지출 카테고리: " + topCat.getKey() + " " + won(topCat.getValue()) + "원");
        }
        if (topProduct != null) {
            used.add("가장 자주 산 상품: " + topProduct.getKey() + " " + topProduct.getValue() + "개");
        }
        used.add("이번 달 지출 " + won(thisMonth) + "원 · 지난 달 " + won(lastMonth) + "원");
        if (savedAmount > 0) {
            used.add("마감임박 할인으로 아낀 금액 " + won(savedAmount) + "원 (폐기 막은 주문 " + rescuedCount + "건)");
        }
        used.add("리뷰 작성률 " + reviewRate + "% (" + reviewed + "/" + count + ")");

        insight.setUsedData(used);
        insight.setSavedAmount(savedAmount);
        insight.setRescuedCount(rescuedCount);

        String dataBlock = "내 구매 집계 데이터:\n- " + String.join("\n- ", used);

        // ── 1) 구매 패턴 요약 (기존) ──────────────────────────────────────────
        String summarySystem = "너는 신선식품 산지직거래 마켓의 구매 분석 어시스턴트다. "
                + "주어진 구매자 집계 데이터를 바탕으로, 소비자가 자신의 소비 패턴을 이해하고 "
                + "다음 장보기에 참고할 수 있도록 2~3문장의 한국어로 담백하게 요약한다. "
                + "이모지·과장 없이. 수치는 주어진 데이터만 사용하고 지어내지 않는다. "
                + "지출이 늘었으면 절약 팁을, 특정 카테고리에 치우쳤으면 균형 잡힌 장보기 제안을 자연스럽게 곁들인다.";
        insight.setSummary(aiClient.chat(summarySystem,
                dataBlock + "\n위 데이터를 바탕으로 구매 패턴 요약과 가벼운 제안을 2~3문장으로 작성해줘.", 300));

        // ── 2) 다음 장보기 추천 — 실제 카탈로그에서 AI가 선택 (할루시네이션 차단) ──
        // LLM에 상품명을 지어내게 두지 않고, DB의 실제 후보 목록을 주고 그중에서 id로만 고르게 한다.
        insight.setRecommendations(recommendProducts(dataBlock, sourceCandidates(byCategoryCode)));

        // ── 3) 소비 성향 라벨 생성 ────────────────────────────────────────────
        String typeSystem = "너는 신선식품 소비 패턴 분류 전문가다. "
                + "구매 데이터를 보고 이 소비자를 가장 잘 표현하는 5글자 이내의 한국어 성향 라벨 하나만 출력한다. "
                + "예: '채소 마니아', '알뜰 구매러', '균형 식탁파', '해산물 애호가' 등. "
                + "라벨 외 다른 텍스트는 절대 출력하지 않는다.";
        String spendingType = aiClient.chat(typeSystem,
                dataBlock + "\n이 구매자의 소비 성향 라벨을 한 단어로 출력해줘.", 30);
        insight.setSpendingType(spendingType.trim());

        return insight;
    }

    /** 추천 후보 풀: 구매자가 가장 많이 산 카테고리 위주 + 재고 있는 상품, 할인율 우선 최대 24개. */
    private List<Product> sourceCandidates(Map<String, Long> byCategoryCode) {
        List<String> topCats = byCategoryCode.entrySet().stream()
                .sorted((a, b) -> Long.compare(b.getValue(), a.getValue()))
                .map(Map.Entry::getKey).limit(2).collect(Collectors.toList());

        LinkedHashMap<Long, Product> pool = new LinkedHashMap<>();
        for (String cat : topCats) {
            for (Product p : productService.findAll(0, 100, null, cat, "latest").getContent()) {
                if (inStock(p)) pool.putIfAbsent(p.getProductId(), p);
            }
        }
        // 선호 카테고리만으로 후보가 빈약하면 전체에서 보충
        if (pool.size() < 6) {
            for (Product p : productService.findAll(0, 100, null, null, "latest").getContent()) {
                if (inStock(p)) pool.putIfAbsent(p.getProductId(), p);
            }
        }
        return pool.values().stream()
                .sorted((a, b) -> Integer.compare(nz(b.getDiscountRate()), nz(a.getDiscountRate())))
                .limit(24).collect(Collectors.toList());
    }

    /** 후보 목록을 LLM에 주고 id로만 3개를 고르게 한다. 실패/무효 시 규칙 기반 폴백. */
    private List<RecommendedProduct> recommendProducts(String dataBlock, List<Product> candidates) {
        if (candidates.isEmpty()) return List.of();

        StringBuilder cb = new StringBuilder("추천 후보 상품 목록(반드시 이 안에서만 고른다):\n");
        for (Product p : candidates) {
            String catKo = CAT_KO.getOrDefault(p.getCategory(), p.getCategory());
            cb.append("[").append(p.getProductId()).append("] ").append(p.getName())
              .append(" (").append(catKo).append(") · 정가 ").append(won(nz(p.getPrice()))).append("원");
            if (hasDeal(p)) {
                cb.append(" · 할인가 ").append(won(nz(p.getDiscountedPrice())))
                  .append("원(").append(p.getDiscountRate()).append("%↓)");
            }
            cb.append("\n");
        }

        String recSystem = "너는 신선식품 마켓 큐레이터다. 구매자의 소비 패턴과 아래 '추천 후보 상품 목록'을 보고, "
                + "다음 장보기에 가장 어울리는 상품 3개를 후보 목록 안에서만 고른다. "
                + "반드시 목록에 있는 id만 사용하고, 목록에 없는 상품은 절대 만들어내지 않는다. "
                + "출력은 JSON 배열 하나만(다른 텍스트·코드블록 표시 없이): "
                + "[{\"id\": <상품id>, \"reason\": \"20자 내외 한국어 추천 이유\"}] 형식으로 정확히 3개.";
        String userPrompt = dataBlock + "\n\n" + cb + "\n위 후보에서 이 구매자에게 맞는 3개를 골라 JSON으로만 답해줘.";

        List<RecommendedProduct> out;
        try {
            out = parseRecs(aiClient.chat(recSystem, userPrompt, 300), candidates);
        } catch (Exception e) {
            out = List.of();
        }
        return out.isEmpty() ? fallbackRecs(candidates) : out;
    }

    /** LLM JSON 응답을 파싱해 실제 후보와 매칭(없는 id·중복 제거). */
    private List<RecommendedProduct> parseRecs(String raw, List<Product> candidates) {
        Map<Long, Product> byId = new LinkedHashMap<>();
        for (Product p : candidates) byId.put(p.getProductId(), p);

        List<RecommendedProduct> out = new ArrayList<>();
        String json = extractJsonArray(raw);
        if (json == null) return out;
        try {
            JsonNode arr = objectMapper.readTree(json);
            if (!arr.isArray()) return out;
            Set<Long> seen = new HashSet<>();
            for (JsonNode n : arr) {
                if (!n.hasNonNull("id")) continue;
                long id = n.get("id").asLong();
                Product p = byId.get(id);
                if (p == null || !seen.add(id)) continue;
                String reason = n.hasNonNull("reason") ? n.get("reason").asText().trim() : defaultReason(p);
                out.add(toRec(p, reason));
                if (out.size() == 3) break;
            }
        } catch (Exception ignore) {
            // 파싱 실패 → 빈 리스트 반환(상위에서 폴백)
        }
        return out;
    }

    /** AI 미가용/파싱 실패 시: 할인율 우선 정렬된 후보 상위 3개를 규칙 기반 이유로. */
    private List<RecommendedProduct> fallbackRecs(List<Product> candidates) {
        return candidates.stream().limit(3)
                .map(p -> toRec(p, defaultReason(p))).collect(Collectors.toList());
    }

    private static RecommendedProduct toRec(Product p, String reason) {
        Integer disc = hasDeal(p) ? p.getDiscountedPrice() : null;
        return new RecommendedProduct(p.getProductId(), p.getName(), p.getCategory(),
                p.getPrice(), disc, p.getThumbnailUrl(), reason);
    }

    private static String defaultReason(Product p) {
        return hasDeal(p) ? "마감임박 할인으로 알뜰하게" : "자주 찾는 카테고리의 신선식품";
    }

    /** 코드블록/잡설 섞여 와도 첫 '['~마지막 ']' 구간만 추출. */
    private static String extractJsonArray(String raw) {
        if (raw == null) return null;
        int s = raw.indexOf('[');
        int e = raw.lastIndexOf(']');
        return (s >= 0 && e > s) ? raw.substring(s, e + 1) : null;
    }

    private static boolean inStock(Product p) {
        return p.getStockQty() != null && p.getStockQty() > 0;
    }

    private static boolean hasDeal(Product p) {
        return p.getDiscountedPrice() != null && p.getDiscountRate() != null && p.getDiscountRate() > 0;
    }

    private static int nz(Integer v) {
        return v == null ? 0 : v;
    }

    private static <V extends Comparable<V>> Map.Entry<String, V> topEntry(Map<String, V> m) {
        Map.Entry<String, V> best = null;
        for (Map.Entry<String, V> e : m.entrySet()) {
            if (best == null || e.getValue().compareTo(best.getValue()) > 0) best = e;
        }
        return best;
    }

    private static String won(long v) {
        return String.format("%,d", v);
    }
}
