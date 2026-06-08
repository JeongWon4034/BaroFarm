package com.freshgrowth.batch.tasklet;

import com.freshgrowth.batch.ai.MarketSummaryAiService;
import com.freshgrowth.batch.dto.SeoulMarketPriceDto;
import com.freshgrowth.batch.shared.CtxKeys;
import org.springframework.batch.core.StepContribution;
import org.springframework.batch.core.scope.context.ChunkContext;
import org.springframework.batch.core.step.tasklet.Tasklet;
import org.springframework.batch.repeat.RepeatStatus;
import org.springframework.stereotype.Component;

import java.util.List;

@Component
public class AiSummaryTasklet implements Tasklet {

    private final MarketSummaryAiService aiService;

    public AiSummaryTasklet(MarketSummaryAiService aiService) {
        this.aiService = aiService;
    }

    @Override
    @SuppressWarnings("unchecked")
    public RepeatStatus execute(StepContribution contribution, ChunkContext chunkContext) {
        var ctx = chunkContext.getStepContext()
                .getStepExecution()
                .getJobExecution()
                .getExecutionContext();

        List<SeoulMarketPriceDto> priceList = (List<SeoulMarketPriceDto>) ctx.get(CtxKeys.PRICE_LIST);
        String summary = aiService.summarize(priceList);
        ctx.put(CtxKeys.AI_SUMMARY, summary);

        System.out.println("[AI] summary created.");
        return RepeatStatus.FINISHED;
    }
}
