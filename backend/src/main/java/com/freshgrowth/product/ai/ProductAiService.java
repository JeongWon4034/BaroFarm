package com.freshgrowth.product.ai;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.freshgrowth.product.Product;
import com.freshgrowth.product.ProductMapper;
import com.freshgrowth.product.ProductService;
import com.freshgrowth.product.ai.dto.CompetitorPrice;
import com.freshgrowth.product.ai.dto.DescriptionResult;
import com.freshgrowth.product.ai.dto.KamisItem;
import com.freshgrowth.product.ai.dto.PriceStats;
import com.freshgrowth.product.ai.dto.PriceSuggestion;
import com.freshgrowth.product.ai.dto.ProductAction;
import com.freshgrowth.product.ai.dto.Recipe;
import com.freshgrowth.product.ai.dto.SellerReport;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.IntSummaryStatistics;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.stream.Collectors;

@Service
public class ProductAiService {
    private final AiClient aiClient;
    private final KamisClient kamisClient;
    private final NaverShoppingClient naverClient;
    private final ProductMapper productMapper;
    private final ProductService productService;
    private final ObjectMapper om = new ObjectMapper();

    // 우리 카테고리 → KAMIS category_name (소프트 매칭 보정)
    private static final Map<String, String> CAT_MAP = Map.of(
            "vegetable", "채소류",
            "fruit", "과일류",
            "seafood", "수산물",
            "meat", "축산물",
            "grain", "식량작물",
            "mushroom", "특용작물"
    );

    // 카테고리 한글 라벨(표시용)
    private static final Map<String, String> CAT_KO = Map.of(
            "vegetable", "채소", "fruit", "과일", "seafood", "해산물", "meat", "육류",
            "grain", "곡물", "mushroom", "버섯", "root", "구근"
    );

    private static final double FAST_SALE_FACTOR = 0.92; // 빠른 판매: 시세보다 8% 낮게

    private final RecipeApiClient recipeApiClient;

    public ProductAiService(AiClient aiClient, KamisClient kamisClient, NaverShoppingClient naverClient,
                            ProductMapper productMapper, ProductService productService,
                            RecipeApiClient recipeApiClient) {
        this.aiClient = aiClient;
        this.kamisClient = kamisClient;
        this.naverClient = naverClient;
        this.productMapper = productMapper;
        this.productService = productService;
        this.recipeApiClient = recipeApiClient;
    }

    /** 판매자 폐기위험 데이터를 LLM에 넣어 운영 요약 리포트 생성 (입력 데이터도 함께 반환) */
    public SellerReport generateSellerReport(Long sellerId) {
        List<Product> products = productService.findSellerProducts(sellerId);
        long high = 0, med = 0, wasteLoss = 0, recovered = 0;
        List<Product> atRisk = new ArrayList<>();
        for (Product p : products) {
            String r = p.getRiskLevel();
            if ("HIGH".equals(r)) high++;
            if ("MEDIUM".equals(r)) med++;
            if ("HIGH".equals(r) || "MEDIUM".equals(r)) {
                atRisk.add(p);
                int stock = p.getStockQty() == null ? 0 : p.getStockQty();
                int price = p.getPrice() == null ? 0 : p.getPrice();
                int deal = p.getDiscountedPrice() == null ? price : p.getDiscountedPrice();
                wasteLoss += (long) stock * price;
                recovered += (long) stock * deal;
            }
        }

        List<String> usedData = new ArrayList<>();
        usedData.add("전체 상품 " + products.size() + "개");
        usedData.add("폐기위험 상품 " + atRisk.size() + "개 (HIGH " + high + " · MEDIUM " + med + ")");
        usedData.add("방치 시 예상 폐기손실 약 " + wonL(wasteLoss) + "원");
        usedData.add("AI 할인가 적용 시 회수 예상 약 " + wonL(recovered) + "원");

        SellerReport report = new SellerReport();
        report.setUsedData(usedData);
        if (atRisk.isEmpty()) {
            report.setSummary("오늘 폐기위험 상품이 없습니다. 재고 상태가 양호합니다.");
            return report;
        }

        String system = "너는 신선식품 마켓 판매자의 운영 어시스턴트다. 주어진 폐기위험 데이터를 바탕으로 "
                + "판매자가 오늘 알아야 할 핵심과 추천 행동을 1~2문장의 한국어로 담백하게 요약한다. 이모지·과장 없이. "
                + "할인 관련 표현은 'AI 할인가를 적용하여 ~' 형태로 서술한다.";
        String user = "판매자 재고 폐기위험 현황:\n" + String.join("\n", usedData)
                + "\n위 데이터를 바탕으로 핵심 요약과 추천 행동을 1~2문장으로 작성해줘.";
        report.setSummary(aiClient.chat(system, user, 250));
        return report;
    }

    private static String wonL(long v) {
        return String.format("%,d", v);
    }

    /**
     * 생성형 AI 상품 설명 (GMS). 카테고리·유통기한 D-day·KAMIS 시세 등 도메인 데이터를
     * 프롬프트에 녹이고, 실제로 넣은 정보(usedContext)를 함께 반환한다.
     */
    public DescriptionResult generateDescription(String name, String category,
                                                 LocalDate expirationDate, Integer stockQty) {
        List<String> ctx = new ArrayList<>();
        StringBuilder user = new StringBuilder("상품명: " + name);

        String catKo = category == null ? null : CAT_KO.getOrDefault(category, category);
        if (catKo != null) { ctx.add("카테고리: " + catKo); user.append("\n카테고리: ").append(catKo); }

        if (expirationDate != null) {
            long d = ChronoUnit.DAYS.between(LocalDate.now(), expirationDate);
            String dday = d < 0 ? "유통기한 경과"
                    : d == 0 ? "유통기한: 오늘 마감"
                    : "유통기한: D-" + d + (d <= 2 ? " (마감임박)" : "");
            ctx.add(dday);
            user.append("\n").append(dday);
        }
        if (stockQty != null) { ctx.add("재고: " + stockQty + "개"); }

        KamisItem m = matchKamis(name, category);
        if (m != null && m.getPrice() != null) {
            String market = "KAMIS 소매 시세: " + m.getItemName() + " " + won(m.getPrice()) + "원"
                    + (m.getUnit() == null ? "" : "/" + m.getUnit());
            ctx.add(market);
            user.append("\n").append(market);
        }
        user.append("\n위 정보를 자연스럽게 반영해 판매용 상세 설명을 2~3문장으로 작성해줘.");

        String system = "너는 신선식품 산지직거래 마켓의 카피라이터다. "
                + "주어진 상품 정보(카테고리·유통기한·시세 등)를 자연스럽게 녹여 2~3문장의 한국어 판매 설명을 작성한다. "
                + "과장 표현과 이모지는 쓰지 말고 담백하게. 유통기한이 임박하면 '신선할 때 빨리' 뉘앙스를, "
                + "시세 정보가 있으면 합리적인 가격임을 은근히 드러낸다.";

        DescriptionResult result = new DescriptionResult();
        result.setDescription(aiClient.chat(system, user.toString(), 300));
        result.setUsedContext(ctx);
        return result;
    }

    /**
     * 추천가 (고도화) — KAMIS 소매 시세(원가 기준선) + 네이버 쇼핑 경쟁 소매가(컬리 등 유사상품)를
     * 함께 모아, AI가 설정돼 있으면 LLM이 둘을 종합해 추천가·이유를 산출하고(engine=LLM),
     * 아니면 결정형 산식으로 폴백한다(engine=RULE). 근거(원가/경쟁가)는 항상 응답에 담는다.
     * 이 메서드는 판매자가 처음 가격을 올릴 때(신규 등록)만 호출된다 — 원가·경쟁가 근거는 구매자에게 노출하지 않는다.
     */
    public PriceSuggestion suggestPrice(String name, String category, String unit) {
        PriceSuggestion s = new PriceSuggestion();
        String sellUnit = unit == null ? "" : unit.trim();

        // 1) 자체 카탈로그 통계(보조 폴백)
        PriceStats stats = productMapper.findCategoryPriceStats(category);
        if (stats != null && stats.getCnt() > 0) {
            s.setCatalogCount(stats.getCnt());
            s.setCatalogAvg((int) Math.round(stats.getAvgPrice()));
        }

        // 2) KAMIS 원가 시세 매칭 → 응답에 시세 상세 채움
        KamisItem matched = matchKamis(name, category);
        Integer kamisPrice = null;
        if (matched != null && matched.getPrice() != null) {
            kamisPrice = matched.getPrice();
            s.setMarketItem(matched.getItemName());
            s.setMarketUnit(matched.getUnit());
            s.setMarketPrice(kamisPrice);
            s.setMarketMonthAgo(matched.getMonthAgo());
            s.setMarketYearAgo(matched.getYearAgo());
            s.setMarketChange(matched.getChangeRate());
        }

        // 3) 네이버 쇼핑 경쟁 소매가 수집 → 분포(최저/평균/최고) + 예시 목록
        List<CompetitorPrice> comps = collectCompetitors(name, matched);
        if (!comps.isEmpty()) {
            IntSummaryStatistics st = comps.stream()
                    .map(CompetitorPrice::getPrice).filter(Objects::nonNull)
                    .mapToInt(Integer::intValue).summaryStatistics();
            s.setCompetitorLow(st.getMin());
            s.setCompetitorHigh(st.getMax());
            s.setCompetitorAvg((int) Math.round(st.getAverage()));
            s.setCompetitorCount((int) st.getCount());
            s.setCompetitors(comps.stream().limit(5).collect(Collectors.toList()));
        }

        boolean hasKamis = kamisPrice != null;
        boolean hasComp = s.getCompetitorCount() != null;
        boolean hasCatalog = s.getCatalogAvg() != null;

        // 4) 주 근거 출처 결정
        s.setSource(hasKamis ? "KAMIS" : hasComp ? "MARKET" : hasCatalog ? "CATALOG" : "NONE");
        if ("NONE".equals(s.getSource())) {
            s.setEngine("RULE");
            s.setBasis("KAMIS 시세·경쟁 소매가·자체 통계 모두 없어 추천가를 낼 수 없습니다.");
            s.setReason("가격을 직접 입력해주세요. (상품명을 일반 명칭으로 적으면 시세·경쟁가 매칭률이 올라갑니다)");
            return s;
        }
        s.setBasis(buildBasis(matched, kamisPrice, s));

        // 5) AI 설정 + 시세/경쟁가 근거가 있으면 LLM이 단위 정규화까지 종합, 실패·미설정 시 결정형 폴백
        if (aiClient.isConfigured() && (hasKamis || hasComp)
                && llmSuggest(s, name, category, sellUnit, matched, kamisPrice)) {
            return s;
        }
        ruleSuggest(s, matched, kamisPrice, hasComp);
        return s;
    }

    // 상품명에서 걸러낼 수식어(검색 정확도와 무관). 핵심 명사만 남겨 매칭 정확도를 높인다.
    private static final java.util.Set<String> MODIFIERS = java.util.Set.of(
            "무농약", "유기농", "친환경", "국산", "국내산", "산지직송", "산지", "직송", "당일수확", "수확",
            "프리미엄", "특", "특품", "명품", "햇", "햇것", "손질", "세척", "냉장", "냉동", "생물", "활",
            "gap", "GAP", "선물", "선물용", "가정용", "못난이", "정품", "고당도", "꿀");

    /**
     * 네이버 쇼핑에서 유사상품 경쟁가 수집 — '실제 상품과 맞는' 결과만 남기는 게 핵심.
     * 1) KAMIS 매칭되면 그 품목(예: '상추')을, 아니면 상품명 핵심 명사(예: '청상추')를 앵커로
     * 2) 핵심 명사 → KAMIS 품목 순으로 단계적 완화해 제목에 그 단어가 든 상품만 채택(엉뚱한 이미지 방지)
     * 3) 대용량 박스·즙 등 가격 이상치 트림
     */
    private List<CompetitorPrice> collectCompetitors(String name, KamisItem matched) {
        if (!naverClient.isConfigured() || name == null || name.isBlank()) {
            return List.of();
        }
        List<CompetitorPrice> raw;
        try {
            raw = naverClient.search(name.trim());
        } catch (Exception e) {
            return List.of();
        }
        if (raw.isEmpty()) {
            return List.of();
        }

        String head = headNoun(name); // 상품명 핵심 명사(수식어·단위 제거) 예: '청상추'
        String kamisBase = (matched != null && matched.getItemName() != null)
                ? matched.getItemName().split("/")[0].trim() : null; // 예: '상추'

        // 핵심 명사로 먼저, 부족하면 KAMIS 품목으로 완화. 둘 다 부실하면 raw 유지.
        List<CompetitorPrice> base = filterByTerm(raw, head);
        if (base.size() < 3 && kamisBase != null && kamisBase.length() >= 2) {
            List<CompetitorPrice> byKamis = filterByTerm(raw, kamisBase);
            if (byKamis.size() > base.size()) {
                base = byKamis;
            }
        }
        if (base.isEmpty()) {
            base = raw;
        }

        // 대용량 박스·즙 등 가격 이상치 제거: 중앙값의 0.4~2.5배만 채택
        List<Integer> prices = base.stream().map(CompetitorPrice::getPrice)
                .filter(Objects::nonNull).sorted().collect(Collectors.toList());
        if (prices.isEmpty()) {
            return List.of();
        }
        int median = prices.get(prices.size() / 2);
        double lo = median * 0.4, hi = median * 2.5;
        List<CompetitorPrice> trimmed = base.stream()
                .filter(c -> c.getPrice() != null && c.getPrice() >= lo && c.getPrice() <= hi)
                .sorted(Comparator.comparingInt(CompetitorPrice::getPrice))
                .collect(Collectors.toList());
        return trimmed.isEmpty() ? base : trimmed;
    }

    private static List<CompetitorPrice> filterByTerm(List<CompetitorPrice> items, String term) {
        if (term == null || term.length() < 2) {
            return List.of();
        }
        return items.stream()
                .filter(c -> c.getTitle() != null && c.getTitle().contains(term))
                .collect(Collectors.toList());
    }

    /** 상품명 핵심 명사 추출 — 괄호/슬래시 뒤 제거 + 수식어·숫자단위 토큰 제외 후 가장 긴 토큰. */
    private static String headNoun(String name) {
        if (name == null) {
            return "";
        }
        String s = name;
        int slash = s.indexOf('/'); if (slash > 0) s = s.substring(0, slash);
        int paren = s.indexOf('('); if (paren > 0) s = s.substring(0, paren);
        String best = "";
        for (String tok : s.trim().split("\\s+")) {
            String t = tok.trim();
            if (t.length() < 2 || MODIFIERS.contains(t) || t.matches(".*\\d.*")) {
                continue; // 짧은 토큰·수식어·숫자(단위) 포함 토큰 제외
            }
            if (t.length() > best.length()) {
                best = t;
            }
        }
        return best.isEmpty() ? coreKeyword(name) : best;
    }

    /**
     * LLM이 KAMIS 원가 시세 + 경쟁 소매가를 종합해 추천가 산출. 핵심: 경쟁가 제목에 섞인
     * 묶음 단위(2kg/500g/4팩 등)를 읽어 공통 기준으로 정규화하고, 판매자의 판매 단위(sellUnit,
     * 비면 상품명에서 추론)에 맞춘 가격을 낸다. 성공 시 s에 추천가·이유·판매단위·환산근거를 채우고 true.
     */
    private boolean llmSuggest(PriceSuggestion s, String name, String category, String sellUnit,
                               KamisItem m, Integer kamisPrice) {
        StringBuilder data = new StringBuilder("상품명: ").append(name)
                .append("\n카테고리: ").append(CAT_KO.getOrDefault(category, category));
        data.append("\n판매자의 판매 단위: ").append(sellUnit.isBlank()
                ? "(미입력 — 상품명에서 추론하거나, 가정 단위를 정하고 그 가정을 unitBasis에 밝힐 것)" : sellUnit);
        if (kamisPrice != null) {
            data.append("\nKAMIS 소매 시세(원가 기준선): ").append(m.getItemName()).append(" ")
                    .append(won(kamisPrice)).append("원").append(m.getUnit() == null ? "" : " / " + m.getUnit() + " 기준");
            if (m.getMonthAgo() != null) {
                data.append(" (1개월 전 ").append(won(m.getMonthAgo())).append("원)");
            }
        }
        if (s.getCompetitorCount() != null) {
            data.append("\n경쟁 소매가(네이버쇼핑 ").append(s.getCompetitorCount())
                    .append("개 몰, lprice=각 상품 최저가). 제목에 묶음 단위가 들어 있으니 반드시 단위를 읽어 정규화할 것:");
            for (CompetitorPrice c : s.getCompetitors()) {
                data.append("\n - ").append(won(c.getPrice())).append("원 | ")
                        .append(c.getTitle() == null ? "" : c.getTitle())
                        .append(c.getMall() == null ? "" : " (" + c.getMall() + ")");
            }
        }
        String system = "너는 신선식품 산지직거래 마켓의 가격 책정 어시스턴트다. "
                + "경쟁 소매가는 상품마다 묶음 단위가 제각각이다(예: '청상추 2kg' 7,000원 vs '청상추 4kg' 18,000원). "
                + "절차: (1) 각 경쟁 상품 제목에서 중량/수량 단위를 파싱한다. 제목에 단위가 없거나 한 항목에 여러 중량이 "
                + "섞여 단가를 특정할 수 없으면(예: '1kg 2kg 4kg') 그 항목은 제외한다. "
                + "(2) 남은 항목을 동일 기준(원/kg 또는 원/100g)으로 환산해 정규화 단가 분포를 구한다. "
                + "(3) 판매자의 '판매 단위' 1개에 해당하는 양으로 그 단가를 곱해 최종 판매가를 만든다. "
                + "산지직거래라 정규화된 경쟁 소매가보다 약간 낮게 책정하되 KAMIS 원가 시세 대비 과도하게 낮추지 않는다. "
                + "가정은 숨기지 말고 unitBasis에 밝혀라. "
                + "★ price는 '판매 단위 1개를 팔 때 받을 최종 금액(원)'이다. 단가(원/kg)가 아니라 판매 단위 가격이며, "
                + "sellUnit과 반드시 일치해야 한다. 예: sellUnit이 '500g'이고 환산 단가가 8,000원/kg이면 price는 4000이다. "
                + "반드시 아래 JSON만 출력한다(코드블록·주석·설명 문장 금지). 모든 숫자는 콤마·단위·'원' 글자 없이 정수만: "
                + "{\"price\": 정수(판매 단위 1개 최종가, 100원 단위), \"sellUnit\": \"판매 단위(예: 500g)\", "
                + "\"unitBasis\": \"경쟁가를 어떤 단위로 환산했고 판매 단위를 어떻게 잡았는지 한국어 1문장\", "
                + "\"reason\": \"원가·정규화된 경쟁가를 근거로 한 한국어 1~2문장\"}";
        String user = data + "\n위 데이터에서 경쟁가를 단위 정규화한 뒤 판매 단위 1개당 추천 판매가를 JSON으로 내줘.";
        try {
            JsonNode node = om.readTree(extractJson(aiClient.chat(system, user, 500, aiClient.getPriceModel())));
            int price = parseIntLoose(node.path("price"));
            String reason = node.path("reason").asText(null);
            if (price <= 0 || reason == null || reason.isBlank()) {
                return false;
            }
            s.setSuggestedPrice(round100(price));
            s.setReason(reason.trim());
            String su = node.path("sellUnit").asText(null);
            s.setSellUnit(su != null && !su.isBlank() ? su.trim() : (sellUnit.isBlank() ? null : sellUnit));
            String ub = node.path("unitBasis").asText(null);
            if (ub != null && !ub.isBlank()) {
                s.setUnitBasis(ub.trim());
            }
            s.setEngine("LLM");
            return true;
        } catch (Exception e) {
            return false;
        }
    }

    /** 결정형 추천가 폴백 — 원가 시세·최저 경쟁가 중 낮은 쪽 기준 8% 할인. */
    private void ruleSuggest(PriceSuggestion s, KamisItem m, Integer kamisPrice, boolean hasComp) {
        s.setEngine("RULE");
        if (hasComp && kamisPrice != null) {
            int anchor = Math.min(s.getCompetitorLow(), kamisPrice);
            s.setSuggestedPrice(fastSale(anchor));
            s.setReason("KAMIS 시세 " + won(kamisPrice) + "원과 최저 경쟁가 " + won(s.getCompetitorLow())
                    + "원 중 낮은 쪽을 기준으로, 산지직거래 경쟁력을 위해 8% 낮춰 추천했습니다.");
        } else if (hasComp) {
            s.setSuggestedPrice(fastSale(s.getCompetitorLow()));
            s.setReason("최저 경쟁 소매가 " + won(s.getCompetitorLow())
                    + "원보다 8% 낮춰 산지직거래 경쟁력을 확보한 추천가입니다.");
        } else if (kamisPrice != null) {
            s.setSuggestedPrice(fastSale(kamisPrice));
            s.setReason(buildReason(kamisPrice, m));
        } else if (s.getCatalogAvg() != null) {
            s.setSuggestedPrice(fastSale(s.getCatalogAvg()));
            s.setReason("동일 카테고리 평균가에서 빠른 판매를 위해 8% 낮춘 추천가입니다. "
                    + "(상품명을 KAMIS 품목·일반 명칭과 맞추면 시세·경쟁가 기반으로 더 정확해집니다)");
        }
    }

    /** 응답에 담을 근거 요약(원가 시세 · 경쟁가 분포 · 자체 통계). */
    private String buildBasis(KamisItem m, Integer kamisPrice, PriceSuggestion s) {
        List<String> parts = new ArrayList<>();
        if (kamisPrice != null) {
            parts.add("KAMIS 소매 시세 " + m.getItemName()
                    + (m.getUnit() == null ? "" : " (" + m.getUnit() + ")") + " " + won(kamisPrice) + "원"
                    + (m.getMonthAgo() != null ? " · 1개월 전 " + won(m.getMonthAgo()) + "원" : ""));
        }
        if (s.getCompetitorCount() != null) {
            parts.add("경쟁 소매가 " + s.getCompetitorCount() + "개 몰 최저 " + won(s.getCompetitorLow())
                    + "원~최고 " + won(s.getCompetitorHigh()) + "원");
        }
        if (parts.isEmpty() && s.getCatalogAvg() != null) {
            parts.add("자체 마켓 동일 카테고리 " + s.getCatalogCount() + "개 평균 " + won(s.getCatalogAvg()) + "원");
        }
        return String.join(" · ", parts);
    }

    /** ```json …``` 코드블록/잡텍스트 제거 — 첫 '{' ~ 마지막 '}'만 추출. */
    private static String extractJson(String raw) {
        if (raw == null) {
            return "{}";
        }
        int a = raw.indexOf('{'), b = raw.lastIndexOf('}');
        return (a >= 0 && b > a) ? raw.substring(a, b + 1) : raw;
    }

    private static int round100(int v) {
        return Math.max((int) (Math.round(v / 100.0) * 100), 100);
    }

    /** JSON price 값을 느슨하게 정수화 — 콤마·'원'·단위 글자가 붙어도 숫자만 추출. */
    private static int parseIntLoose(JsonNode n) {
        if (n == null || n.isMissingNode() || n.isNull()) {
            return 0;
        }
        String t = n.asText("").replaceAll("[^0-9]", "");
        if (t.isEmpty()) {
            return 0;
        }
        try {
            return Integer.parseInt(t);
        } catch (NumberFormatException e) {
            return 0;
        }
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

    /** KAMIS 품목 매칭 공개 래퍼 — 판매자 상품 인사이트에서 기준 소매가 산출용. */
    public KamisItem kamisMatch(String name, String category) {
        return matchKamis(name, category);
    }

    /**
     * 판매 정체 상품 행동 추천(hover) — KAMIS 시세·현재가·미판매 기간·재고를 바탕으로
     * 이익 증진 행동과 추천가를 LLM이 제안(미설정 시 규칙 폴백). 1회 LLM 호출(경쟁가 조회 없음 → 빠름).
     */
    public ProductAction profitAction(Product p, Integer daysNoSale, boolean neverSold) {
        ProductAction r = new ProductAction();
        r.setProductId(p.getProductId());
        int current = p.getDiscountedPrice() != null ? p.getDiscountedPrice() : p.getPrice();
        r.setCurrentPrice(current);

        KamisItem k = kamisMatch(p.getName(), p.getCategory());
        Integer kamisPrice = (k != null) ? k.getPrice() : null;
        r.setKamisPrice(kamisPrice);
        r.setDaysSinceLastSale(daysNoSale);

        String headline = neverSold
                ? (daysNoSale == null ? "아직 판매 없음" : "등록 후 " + daysNoSale + "일째 미판매")
                : daysNoSale + "일째 판매 없음";
        r.setHeadline(headline);

        // 규칙 추천가: 시세·현재가 중 낮은 쪽에서 더 공격적으로(정체 해소)
        int base = kamisPrice != null ? Math.min(kamisPrice, current) : current;
        int ruleRec = round100((int) (base * 0.85));

        if (aiClient.isConfigured()) {
            StringBuilder ctx = new StringBuilder("상품명: ").append(p.getName())
                    .append("\n카테고리: ").append(CAT_KO.getOrDefault(p.getCategory(), p.getCategory()))
                    .append("\n현재 판매가: ").append(won(current)).append("원");
            if (kamisPrice != null) {
                ctx.append("\nKAMIS 소매 시세: ").append(won(kamisPrice)).append("원")
                        .append(k.getUnit() == null ? "" : "/" + k.getUnit());
            }
            ctx.append("\n재고: ").append(p.getStockQty() == null ? 0 : p.getStockQty()).append("개");
            if (p.getDaysToExpiry() != null) {
                ctx.append("\n유통기한까지: D-").append(p.getDaysToExpiry());
            }
            ctx.append("\n판매 상태: ").append(headline);

            String system = "너는 신선식품 산지직거래 마켓의 매출 코치다. 며칠째 안 팔리는 상품에 대해 "
                    + "'이익 증진을 위한 구체적 행동'을 제안한다. 가격 인하 폭, 마감임박 딜 전환, 번들/묶음, 노출 강화 등 "
                    + "실행 가능한 조치를 우선순위로 제시하되, 무작정 싸게 팔라 하지 말고 재고 회전과 마진의 균형을 고려한다. "
                    + "유통기한이 임박했으면 더 빠른 회전을 우선한다. "
                    + "반드시 아래 JSON만 출력한다(코드블록·설명 문장 금지). 숫자는 정수만: "
                    + "{\"recommendedPrice\": 정수(100원 단위 추천 판매가), \"action\": \"한국어 2~3문장 행동 추천\"}";
            String user = ctx + "\n위 상품의 판매가 정체됐어. 이익을 늘릴 구체적 행동과 추천 판매가를 JSON으로 줘.";
            try {
                JsonNode node = om.readTree(extractJson(aiClient.chat(system, user, 350, aiClient.getPriceModel())));
                int price = parseIntLoose(node.path("recommendedPrice"));
                String action = node.path("action").asText(null);
                if (price > 0 && action != null && !action.isBlank()) {
                    r.setRecommendedPrice(round100(price));
                    r.setAction(action.trim());
                    r.setEngine("LLM");
                    return r;
                }
            } catch (Exception ignore) {
                // 폴백으로
            }
        }

        r.setRecommendedPrice(ruleRec);
        int cut = current > 0 ? (int) Math.round((current - ruleRec) * 100.0 / current) : 0;
        r.setAction(headline + ". 추천가 " + won(ruleRec) + "원(현재가 대비 " + cut + "% 인하)으로 내리고 '마감임박 딜' 탭에 "
                + "노출하면 회전이 빨라집니다. 재고가 많다면 묶음(번들) 구성으로 객단가를 유지하는 것도 방법입니다.");
        r.setEngine("RULE");
        return r;
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

    // ── 홈 '오늘의 레시피' ─ 식약처 레시피 DB(실제 사진·조리법)에서, 우리가 파는 재료와 ──
    // ── 가장 많이 겹치는(마감임박 우선) 레시피를 골라 보여준다. 하루 1회 캐시. ─────────────
    private List<Recipe> cachedRecipes;
    private LocalDate recipesCachedOn;

    public List<Recipe> recommendRecipes() {
        LocalDate today = LocalDate.now();
        if (cachedRecipes != null && today.equals(recipesCachedOn)) return cachedRecipes;
        cachedRecipes = buildRecipes();
        recipesCachedOn = today;
        return cachedRecipes;
    }

    /** 상세 = 이미 만들어둔 목록에서 idx 선택(식약처 데이터라 추가 생성 없이 즉시). */
    public Recipe recipeDetail(int idx) {
        List<Recipe> list = recommendRecipes();
        if (list.isEmpty()) return null;
        return list.get(Math.max(0, Math.min(idx, list.size() - 1)));
    }

    private List<Recipe> buildRecipes() {
        // 1) 판매중(마감임박 우선) 재고 상품 → 재료 키워드 맵
        List<Product> products = productService.findAll(0, 100, null, null, "expiry").getContent();
        LinkedHashMap<String, Long> kwMap = new LinkedHashMap<>();
        for (Product p : products) {
            if (p.getStockQty() == null || p.getStockQty() <= 0) continue;
            String kw = coreKeyword(p.getName());
            if (kw.length() >= 2) kwMap.putIfAbsent(kw, p.getProductId());
        }
        // 2) 식약처 레시피 가져와 우리 재료와 겹치는 순으로 정렬 → 상위 4개
        List<Map<String, Object>> rows = recipeApiClient.fetch(1, 100);
        if (rows.isEmpty()) return List.of();
        List<Recipe> all = new ArrayList<>();
        for (Map<String, Object> row : rows) all.add(toRecipe(row, kwMap));
        all.sort((a, b) -> mappedCount(b) - mappedCount(a)); // 매칭 많은 레시피 우선
        return all.stream().limit(4).collect(Collectors.toList());
    }

    /** 식약처 row → Recipe(요리명·대표사진·재료 매핑·조리단계·단계사진). */
    private Recipe toRecipe(Map<String, Object> row, Map<String, Long> kwMap) {
        String name = str(row, "RCP_NM");
        String pat = str(row, "RCP_PAT2");
        String way = str(row, "RCP_WAY2");
        String eyebrow = (pat.isEmpty() ? "오늘의 레시피" : pat) + (way.isEmpty() ? "" : " · " + way);

        // 재료 = 이 레시피에 들어가는 '우리 판매 상품'(겹치는 것만 → 사서 만들 수 있게 연결)
        String parts = str(row, "RCP_PARTS_DTLS");
        List<Recipe.Ingredient> ings = new ArrayList<>();
        for (Map.Entry<String, Long> e : kwMap.entrySet()) {
            if (parts.contains(e.getKey())) {
                ings.add(new Recipe.Ingredient(e.getKey(), e.getValue()));
                if (ings.size() >= 6) break;
            }
        }

        Recipe r = new Recipe(name, eyebrow, ings);
        r.setImage(firstNonBlank(str(row, "ATT_FILE_NO_MAIN"), str(row, "ATT_FILE_NO_MK")));

        // 조리 단계(MANUAL01~20) + 단계 이미지(MANUAL_IMG01~20), 같은 순서로 정렬
        List<String> steps = new ArrayList<>();
        List<String> stepImgs = new ArrayList<>();
        for (int i = 1; i <= 20; i++) {
            String num = String.format("%02d", i);
            String text = str(row, "MANUAL" + num).replaceAll("^\\s*\\d+\\.?\\s*", "").trim();
            if (text.isEmpty()) continue;
            steps.add(text);
            stepImgs.add(str(row, "MANUAL_IMG" + num));
        }
        r.setSteps(steps);
        r.setStepImages(stepImgs);
        return r;
    }

    private static int mappedCount(Recipe r) {
        return r.getIngredients() == null ? 0 : (int) r.getIngredients().stream().filter(g -> g.getProductId() != null).count();
    }

    /** "양파/양파 (1kg)" → "양파", "꼬막/국산(새꼬막) (1kg)" → "꼬막" */
    private static String coreKeyword(String name) {
        if (name == null) return "";
        String s = name;
        int slash = s.indexOf('/');
        if (slash > 0) s = s.substring(0, slash);
        int paren = s.indexOf('(');
        if (paren > 0) s = s.substring(0, paren);
        return s.trim();
    }

    private static String str(Map<String, Object> row, String key) {
        Object v = row.get(key);
        return v == null ? "" : v.toString().trim();
    }

    private static String firstNonBlank(String a, String b) {
        return (a != null && !a.isBlank()) ? a : (b == null ? "" : b);
    }
}
