package com.freshgrowth.batch.tasklet;

import com.freshgrowth.batch.dao.MarketPriceDao;
import com.freshgrowth.batch.dto.MarketReportDto;
import com.freshgrowth.batch.dto.SeoulMarketPriceDto;
import com.freshgrowth.batch.pdf.MarketPricePdfService;
import com.freshgrowth.batch.shared.CtxKeys;
import org.springframework.batch.core.StepContribution;
import org.springframework.batch.core.scope.context.ChunkContext;
import org.springframework.batch.core.step.tasklet.Tasklet;
import org.springframework.batch.repeat.RepeatStatus;
import org.springframework.stereotype.Component;

import java.time.LocalDate;
import java.util.List;

@Component
public class PdfReportTasklet implements Tasklet {

    private final MarketPricePdfService pdfService;
    private final MarketPriceDao marketPriceDao;

    public PdfReportTasklet(MarketPricePdfService pdfService, MarketPriceDao marketPriceDao) {
        this.pdfService = pdfService;
        this.marketPriceDao = marketPriceDao;
    }

    @Override
    @SuppressWarnings("unchecked")
    public RepeatStatus execute(StepContribution contribution, ChunkContext chunkContext) throws Exception {
        var ctx = chunkContext.getStepContext()
                .getStepExecution()
                .getJobExecution()
                .getExecutionContext();

        List<SeoulMarketPriceDto> priceList = (List<SeoulMarketPriceDto>) ctx.get(CtxKeys.PRICE_LIST);
        String summary = (String) ctx.get(CtxKeys.AI_SUMMARY);
        String pdfPath = pdfService.createDailyReport(priceList, summary);

        marketPriceDao.insertMarketReport(new MarketReportDto(LocalDate.now(), summary, pdfPath));
        ctx.put(CtxKeys.PDF_PATH, pdfPath);

        System.out.println("[PDF] report created. path=" + pdfPath);
        return RepeatStatus.FINISHED;
    }
}
