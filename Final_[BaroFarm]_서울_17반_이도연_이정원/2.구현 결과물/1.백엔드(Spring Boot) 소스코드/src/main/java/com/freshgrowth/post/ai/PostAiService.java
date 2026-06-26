package com.freshgrowth.post.ai;

import com.freshgrowth.post.ai.dto.MarketTrend;
import com.freshgrowth.post.ai.dto.TrendItem;
import com.freshgrowth.product.ai.AiClient;
import com.freshgrowth.product.ai.KamisClient;
import com.freshgrowth.product.ai.dto.KamisItem;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

/**
 * 게시판 상단 'AI 식료품 트렌드' 카드 생성.
 * KAMIS 소매 시세의 한 달 전 대비 등락이 큰 품목을 뽑아 GMS LLM에 넣어
 * 구매자가 읽기 좋은 트렌드 분석 글을 만든다. 결과는 하루 1회 캐시한다.
 */
@Service
public class PostAiService {
    private static final int TOP_N = 3;           // 오른/내린 품목 각각 최대 개수
    private static final double MIN_ABS_PCT = 3.0; // 등락 3% 미만은 '변동 없음'으로 제외

    private final KamisClient kamisClient;
    private final AiClient aiClient;

    private volatile MarketTrend cache;
    private volatile LocalDate cachedOn;

    public PostAiService(KamisClient kamisClient, AiClient aiClient) {
        this.kamisClient = kamisClient;
        this.aiClient = aiClient;
    }

    /** 오늘자 트렌드 카드(캐시). AI·KAMIS 미설정이거나 변동 품목이 없으면 available=false. */
    public MarketTrend getMarketTrend() {
        LocalDate today = LocalDate.now();
        MarketTrend c = cache;
        if (c != null && today.equals(cachedOn)) {
            return c;
        }
        MarketTrend trend = build(today);
        cache = trend;
        cachedOn = today;
        return trend;
    }

    private MarketTrend build(LocalDate today) {
        MarketTrend trend = new MarketTrend();
        trend.setGeneratedOn(today);

        if (!aiClient.isConfigured() || !kamisClient.isConfigured()) {
            trend.setAvailable(false);
            return trend;
        }

        List<KamisItem> items;
        try {
            items = kamisClient.getDailyRetail();
        } catch (Exception e) {
            trend.setAvailable(false);
            return trend;
        }

        // 한 달 전 대비 등락률 계산 — 유효한 품목만
        List<TrendItem> movers = new ArrayList<>();
        for (KamisItem it : items) {
            if (it.getPrice() == null || it.getMonthAgo() == null || it.getMonthAgo() <= 0) {
                continue;
            }
            double pct = (it.getPrice() - it.getMonthAgo()) * 100.0 / it.getMonthAgo();
            if (Math.abs(pct) < MIN_ABS_PCT) {
                continue;
            }
            TrendItem m = new TrendItem();
            m.setItemName(it.getItemName());
            m.setUnit(it.getUnit());
            m.setPrice(it.getPrice());
            m.setMonthAgo(it.getMonthAgo());
            m.setChangePct(Math.round(pct * 10) / 10.0);
            movers.add(m);
        }

        if (movers.isEmpty()) {
            trend.setAvailable(false);
            return trend;
        }

        List<TrendItem> risers = movers.stream()
                .filter(m -> m.getChangePct() > 0)
                .sorted(Comparator.comparingDouble(TrendItem::getChangePct).reversed())
                .limit(TOP_N).toList();
        List<TrendItem> fallers = movers.stream()
                .filter(m -> m.getChangePct() < 0)
                .sorted(Comparator.comparingDouble(TrendItem::getChangePct))
                .limit(TOP_N).toList();

        trend.setRisers(risers);
        trend.setFallers(fallers);
        trend.setBasis("KAMIS 소매 시세 · 한 달 전 대비 · 분석 품목 " + movers.size() + "개");
        trend.setSummary(generateSummary(risers, fallers));
        trend.setAvailable(true);
        return trend;
    }

    private String generateSummary(List<TrendItem> risers, List<TrendItem> fallers) {
        StringBuilder data = new StringBuilder();
        if (!risers.isEmpty()) {
            data.append("오른 품목:\n");
            for (TrendItem m : risers) {
                data.append("- ").append(line(m)).append("\n");
            }
        }
        if (!fallers.isEmpty()) {
            data.append("내린 품목:\n");
            for (TrendItem m : fallers) {
                data.append("- ").append(line(m)).append("\n");
            }
        }

        String system = "너는 신선식품 산지직거래 마켓의 식료품 트렌드 큐레이터다. "
                + "주어진 KAMIS 소매 시세(한 달 전 대비 등락) 데이터를 바탕으로, "
                + "장 보는 소비자가 읽기 좋은 트렌드 코멘트를 3~4문장의 한국어로 작성한다. "
                + "이모지·과장 없이 담백하게. 가격이 내린 품목은 '지금이 사기 좋은 때'라는 뉘앙스를, "
                + "오른 품목은 '대체 품목이나 보관' 같은 실용 팁을 자연스럽게 곁들인다. "
                + "수치는 데이터에 있는 값만 쓰고 지어내지 않는다.";
        String user = "이번 달 식료품 시세 변동 데이터:\n" + data
                + "\n위 데이터를 바탕으로 소비자용 식료품 트렌드 코멘트를 3~4문장으로 작성해줘.";
        return aiClient.chat(system, user, 350);
    }

    private static String line(TrendItem m) {
        return m.getItemName()
                + (m.getUnit() == null ? "" : "(" + m.getUnit() + ")")
                + " " + String.format("%,d", m.getPrice()) + "원, 한 달 전 대비 "
                + (m.getChangePct() >= 0 ? "+" : "") + m.getChangePct() + "%";
    }
}
