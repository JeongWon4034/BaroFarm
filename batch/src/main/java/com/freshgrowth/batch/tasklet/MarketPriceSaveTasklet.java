package com.freshgrowth.batch.tasklet;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.freshgrowth.batch.dao.MarketPriceDao;
import com.freshgrowth.batch.dto.SeoulMarketPriceDto;
import com.freshgrowth.batch.shared.CtxKeys;
import org.springframework.batch.core.StepContribution;
import org.springframework.batch.core.scope.context.ChunkContext;
import org.springframework.batch.core.step.tasklet.Tasklet;
import org.springframework.batch.repeat.RepeatStatus;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.List;

@Component
public class MarketPriceSaveTasklet implements Tasklet {

    private final MarketPriceDao marketPriceDao;
    private final ObjectMapper objectMapper = new ObjectMapper();

    public MarketPriceSaveTasklet(MarketPriceDao marketPriceDao) {
        this.marketPriceDao = marketPriceDao;
    }

    @Override
    public RepeatStatus execute(StepContribution contribution, ChunkContext chunkContext) throws Exception {
        var ctx = chunkContext.getStepContext()
                .getStepExecution()
                .getJobExecution()
                .getExecutionContext();

        String json = (String) ctx.get(CtxKeys.PRICE_JSON);
        List<SeoulMarketPriceDto> priceList = parse(json);

        if (!priceList.isEmpty()) {
            int inserted = marketPriceDao.insertMarketPriceBatch(priceList);
            System.out.println("[Save] market_price inserted rows=" + inserted);
        } else {
            System.out.println("[Save] 저장할 가격 데이터가 없습니다.");
        }

        ctx.put(CtxKeys.PRICE_LIST, priceList);
        return RepeatStatus.FINISHED;
    }

    private List<SeoulMarketPriceDto> parse(String json) throws Exception {
        JsonNode root = objectMapper.readTree(json);
        JsonNode rows = findRows(root);
        List<SeoulMarketPriceDto> result = new ArrayList<>();

        if (rows == null || !rows.isArray()) {
            throw new IllegalStateException("서울시 API 응답에서 row 배열을 찾지 못했습니다. 응답=" + shrink(json));
        }

        for (JsonNode row : rows) {
            SeoulMarketPriceDto dto = new SeoulMarketPriceDto();
            dto.setTradeDate(text(row, "E_NAME"));
            dto.setMarketName(text(row, "MRKT_DIV"));
            dto.setItemName(text(row, "PUM_NM_A"));
            dto.setItemCode(text(row, "PUM_CD"));
            dto.setKindName(text(row, "G_NAME_A"));
            dto.setGradeName(text(row, "F_NAME"));
            dto.setUnitQty(text(row, "UNIT_QTY"));
            dto.setAvgPrice(number(row, "AV_P_A"));
            dto.setPrevAvgPrice(number(row, "PAV_P_A"));
            dto.setPrevYearPrice(number(row, "PAV_PY_A"));
            dto.setFluctuationRate(text(row, "A_B"));
            dto.setRawJson(row.toString());
            result.add(dto);
        }
        return result;
    }

    private JsonNode findRows(JsonNode root) {
        if (root == null || !root.isObject()) {
            return null;
        }
        var fields = root.fields();
        while (fields.hasNext()) {
            JsonNode value = fields.next().getValue();
            JsonNode rows = value.get("row");
            if (rows != null && rows.isArray()) {
                return rows;
            }
        }
        return null;
    }

    private String text(JsonNode node, String field) {
        JsonNode value = node.get(field);
        return value == null || value.isNull() ? "" : value.asText("");
    }

    private Integer number(JsonNode node, String field) {
        String value = text(node, field).replace(",", "").trim();
        if (value.isBlank() || "-".equals(value)) {
            return null;
        }
        try {
            return Integer.parseInt(value);
        } catch (NumberFormatException e) {
            return null;
        }
    }

    private String shrink(String text) {
        if (text == null || text.length() <= 500) {
            return text;
        }
        return text.substring(0, 500) + "...";
    }
}
