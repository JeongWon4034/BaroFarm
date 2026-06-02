package com.freshgrowth.batch.ai;

import com.freshgrowth.batch.dto.SeoulMarketPriceDto;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class MarketSummaryAiService {

    private final ChatClient chatClient;

    public MarketSummaryAiService(ChatClient.Builder builder) {
        this.chatClient = builder.build();
    }

    public String summarize(List<SeoulMarketPriceDto> priceList) {
        if (priceList == null || priceList.isEmpty()) {
            return "수집된 서울시 농수산물 가격 데이터가 없습니다.";
        }

        String prompt = """
                당신은 FreshGrowth 판매자를 돕는 농산물 가격 분석가입니다.
                아래 서울시농수산식품공사 주요 품목 가격 데이터를 보고 판매자가 바로 이해할 수 있게 요약하세요.

                작성 규칙:
                1. 오늘 가격 흐름을 3~5문장으로 요약합니다.
                2. 가격이 높거나 낮아진 품목이 보이면 언급합니다.
                3. FreshGrowth 판매자에게 줄 재고/가격 운영 조언을 2~3개 제시합니다.
                4. 과장하지 말고 데이터에 근거해서 작성합니다.

                [가격 데이터]
                %s
                """.formatted(toPromptData(priceList));

        try {
            return chatClient.prompt(prompt).call().content();
        } catch (Exception e) {
            System.err.println("[AI] 요약 실패: " + e.getMessage());
            return fallbackSummary(priceList);
        }
    }

    private String toPromptData(List<SeoulMarketPriceDto> priceList) {
        StringBuilder sb = new StringBuilder();
        int limit = Math.min(priceList.size(), 20);
        for (int i = 0; i < limit; i++) {
            SeoulMarketPriceDto p = priceList.get(i);
            sb.append("- ")
                    .append(blank(p.getTradeDate())).append(" / ")
                    .append(blank(p.getMarketName())).append(" / ")
                    .append(blank(p.getItemName())).append(" / ")
                    .append(blank(p.getKindName())).append(" / 평균가 ")
                    .append(p.getAvgPrice()).append(" / 전일평균가 ")
                    .append(p.getPrevAvgPrice()).append(" / 등락률 ")
                    .append(blank(p.getFluctuationRate()))
                    .append('\n');
        }
        return sb.toString();
    }

    private String fallbackSummary(List<SeoulMarketPriceDto> priceList) {
        SeoulMarketPriceDto first = priceList.get(0);
        return "AI 요약 생성에 실패하여 기본 요약을 제공합니다.\n"
                + "총 " + priceList.size() + "건의 서울시 농수산물 가격 데이터를 수집했습니다.\n"
                + "대표 품목은 " + blank(first.getItemName()) + "이며 평균가는 " + first.getAvgPrice() + "원입니다.\n"
                + "판매자는 수집 데이터를 기준으로 유통기한이 짧은 상품의 가격 조정과 재고 관리를 검토할 수 있습니다.";
    }

    private String blank(String value) {
        return value == null ? "" : value;
    }
}
