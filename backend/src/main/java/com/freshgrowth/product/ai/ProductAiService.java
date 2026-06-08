package com.freshgrowth.product.ai;

import com.freshgrowth.product.ProductMapper;
import com.freshgrowth.product.ai.dto.KamisItem;
import com.freshgrowth.product.ai.dto.PriceStats;
import com.freshgrowth.product.ai.dto.PriceSuggestion;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;

@Service
public class ProductAiService {
    private final AiClient aiClient;
    private final KamisClient kamisClient;
    private final ProductMapper productMapper;

    // 우리 카테고리 → KAMIS category_name (소프트 매칭 보정)
    private static final Map<String, String> CAT_MAP = Map.of(
            "vegetable", "채소류",
            "fruit", "과일류",
            "seafood", "수산물",
            "meat", "축산물",
            "grain", "식량작물",
            "mushroom", "특용작물"
    );

    private static final double FAST_SALE_FACTOR = 0.92; // 빠른 판매: 시세보다 8% 낮게

    public ProductAiService(AiClient aiClient, KamisClient kamisClient, ProductMapper productMapper) {
        this.aiClient = aiClient;
        this.kamisClient = kamisClient;
        this.productMapper = productMapper;
    }

    /** 생성형 AI 상품 설명 (GMS) */
    public String generateDescription(String name, String category) {
        String system = "너는 신선식품 산지직거래 마켓의 카피라이터다. "
                + "상품의 신선함과 매력을 살린 2~3문장의 한국어 상품 설명을 작성한다. "
                + "과장된 표현과 이모지는 쓰지 말고, 구매자가 신뢰할 수 있게 담백하게 쓴다.";
        String user = "상품명: " + name + "\n카테고리: " + (category == null ? "" : category)
                + "\n이 상품의 판매용 상세 설명을 2~3문장으로 작성해줘.";
        return aiClient.chat(system, user, 300);
    }

    /**
     * 추천가 — KAMIS 소매 시세에 품목 매칭되면 그 시세 기반(근거·이유 포함),
     * 매칭 안 되면 자체 카탈로그 통계로 폴백.
     */
    public PriceSuggestion suggestPrice(String name, String category) {
        PriceSuggestion s = new PriceSuggestion();

        PriceStats stats = productMapper.findCategoryPriceStats(category);
        if (stats != null && stats.getCnt() > 0) {
            s.setCatalogCount(stats.getCnt());
            s.setCatalogAvg((int) Math.round(stats.getAvgPrice()));
        }

        KamisItem matched = matchKamis(name, category);
        if (matched != null && matched.getPrice() != null) {
            int market = matched.getPrice();
            s.setSuggestedPrice(fastSale(market));
            s.setSource("KAMIS");
            s.setMarketItem(matched.getItemName());
            s.setMarketUnit(matched.getUnit());
            s.setMarketPrice(market);
            s.setMarketMonthAgo(matched.getMonthAgo());
            s.setMarketYearAgo(matched.getYearAgo());
            s.setMarketChange(matched.getChangeRate());
            s.setBasis("KAMIS 소매 시세 — " + matched.getItemName()
                    + (matched.getUnit() == null ? "" : " (" + matched.getUnit() + ")")
                    + " 당일 " + won(market) + "원"
                    + (matched.getMonthAgo() != null ? " · 1개월 전 " + won(matched.getMonthAgo()) + "원" : "")
                    + (matched.getYearAgo() != null ? " · 1년 전 " + won(matched.getYearAgo()) + "원" : ""));
            s.setReason(buildReason(market, matched));
            return s;
        }

        if (s.getCatalogAvg() != null) {
            int avg = s.getCatalogAvg();
            s.setSuggestedPrice(fastSale(avg));
            s.setSource("CATALOG");
            s.setBasis("KAMIS에 해당 품목이 없어 자체 마켓 통계 사용 — 동일 카테고리 "
                    + s.getCatalogCount() + "개 평균 " + won(avg) + "원");
            s.setReason("동일 카테고리 평균가에서 빠른 판매를 위해 8% 낮춘 추천가입니다. "
                    + "(상품명을 KAMIS 품목과 맞추면 시세 기반으로 더 정확해집니다)");
            return s;
        }

        s.setSource("NONE");
        s.setBasis("KAMIS 매칭·자체 통계 모두 없어 추천가를 낼 수 없습니다.");
        s.setReason("가격을 직접 입력해주세요.");
        return s;
    }

    /** 상품명에 포함된 KAMIS 품목(예: '상추')으로 매칭. 카테고리 일치 시 우선. */
    private KamisItem matchKamis(String name, String category) {
        if (!kamisClient.isConfigured() || name == null || name.isBlank()) {
            return null;
        }
        List<KamisItem> items;
        try {
            items = kamisClient.getDailyRetail();
        } catch (Exception e) {
            return null;
        }
        String kamisCat = CAT_MAP.get(category);
        KamisItem best = null;
        for (KamisItem it : items) {
            if (it.getItemName() == null) {
                continue;
            }
            String base = it.getItemName().split("/")[0].trim();
            if (base.isEmpty() || !name.contains(base)) {
                continue;
            }
            if (kamisCat != null && kamisCat.equals(it.getCategory())) {
                return it; // 품목 + 카테고리 동시 일치
            }
            if (best == null) {
                best = it;
            }
        }
        return best;
    }

    private String buildReason(int market, KamisItem m) {
        StringBuilder sb = new StringBuilder();
        sb.append("KAMIS 소매 당일가 ").append(won(market)).append("원 기준, 빠른 판매를 위해 8% 낮춰 추천했습니다.");
        if (m.getMonthAgo() != null && m.getMonthAgo() > 0) {
            double diff = (market - m.getMonthAgo()) * 100.0 / m.getMonthAgo();
            sb.append(String.format(" 한 달 전 대비 %.1f%% %s.", Math.abs(diff), diff >= 0 ? "상승" : "하락"));
        }
        sb.append(" ※ KAMIS 단위(").append(m.getUnit() == null ? "-" : m.getUnit())
                .append(")와 판매 단위가 다를 수 있으니 참고해 조정하세요.");
        return sb.toString();
    }

    private int fastSale(int basePrice) {
        return Math.max((int) (Math.round(basePrice * FAST_SALE_FACTOR / 100.0) * 100), 100);
    }

    private static String won(int v) {
        return String.format("%,d", v);
    }
}
