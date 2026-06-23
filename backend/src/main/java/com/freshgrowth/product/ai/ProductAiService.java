package com.freshgrowth.product.ai;

import com.freshgrowth.product.Product;
import com.freshgrowth.product.ProductMapper;
import com.freshgrowth.product.ProductService;
import com.freshgrowth.product.ai.dto.DescriptionResult;
import com.freshgrowth.product.ai.dto.KamisItem;
import com.freshgrowth.product.ai.dto.PriceStats;
import com.freshgrowth.product.ai.dto.PriceSuggestion;
import com.freshgrowth.product.ai.dto.Recipe;
import com.freshgrowth.product.ai.dto.SellerReport;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
public class ProductAiService {
    private final AiClient aiClient;
    private final KamisClient kamisClient;
    private final ProductMapper productMapper;
    private final ProductService productService;

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

    public ProductAiService(AiClient aiClient, KamisClient kamisClient,
                            ProductMapper productMapper, ProductService productService,
                            RecipeApiClient recipeApiClient) {
        this.aiClient = aiClient;
        this.kamisClient = kamisClient;
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
                + "할인 관련 표현은 '떨이'라는 단어를 쓰지 말고 'AI 할인가를 적용하여 ~' 형태로 서술한다.";
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
