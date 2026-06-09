package com.freshgrowth.order.ai;

import com.freshgrowth.order.Order;
import com.freshgrowth.order.OrderService;
import com.freshgrowth.order.ai.dto.BuyerInsight;
import com.freshgrowth.product.ai.AiClient;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.YearMonth;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

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
    private final AiClient aiClient;

    public BuyerInsightService(OrderService orderService, AiClient aiClient) {
        this.orderService = orderService;
        this.aiClient = aiClient;
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
        Map<String, Long> byCategory = new LinkedHashMap<>();
        Map<String, Long> byMonth = new LinkedHashMap<>();
        Map<String, Integer> byProduct = new LinkedHashMap<>();

        for (Order o : orders) {
            int price = o.getTotalPrice() == null ? 0 : o.getTotalPrice();
            totalSpend += price;
            totalQty += o.getQuantity() == null ? 0 : o.getQuantity();
            if (o.getReviewId() != null) reviewed++;

            String catKo = o.getCategory() == null ? "기타" : CAT_KO.getOrDefault(o.getCategory(), o.getCategory());
            byCategory.merge(catKo, (long) price, Long::sum);

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
        used.add("리뷰 작성률 " + reviewRate + "% (" + reviewed + "/" + count + ")");

        insight.setUsedData(used);

        String system = "너는 신선식품 산지직거래 마켓의 구매 분석 어시스턴트다. "
                + "주어진 구매자 집계 데이터를 바탕으로, 소비자가 자신의 소비 패턴을 이해하고 "
                + "다음 장보기에 참고할 수 있도록 2~3문장의 한국어로 담백하게 요약한다. "
                + "이모지·과장 없이. 수치는 주어진 데이터만 사용하고 지어내지 않는다. "
                + "지출이 늘었으면 절약 팁을, 특정 카테고리에 치우쳤으면 균형 잡힌 장보기 제안을 자연스럽게 곁들인다.";
        String user = "내 구매 집계 데이터:\n- " + String.join("\n- ", used)
                + "\n위 데이터를 바탕으로 구매 패턴 요약과 가벼운 제안을 2~3문장으로 작성해줘.";
        insight.setSummary(aiClient.chat(system, user, 300));
        return insight;
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
