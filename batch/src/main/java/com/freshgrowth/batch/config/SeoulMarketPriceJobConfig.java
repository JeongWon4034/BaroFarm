package com.freshgrowth.batch.config;

import com.freshgrowth.batch.tasklet.AiSummaryTasklet;
import com.freshgrowth.batch.tasklet.MarketPriceSaveTasklet;
import com.freshgrowth.batch.tasklet.PdfReportTasklet;
import com.freshgrowth.batch.tasklet.SeoulMarketPriceCollectTasklet;
import org.springframework.batch.core.Job;
import org.springframework.batch.core.Step;
import org.springframework.batch.core.job.builder.JobBuilder;
import org.springframework.batch.core.launch.support.RunIdIncrementer;
import org.springframework.batch.core.repository.JobRepository;
import org.springframework.batch.core.step.builder.StepBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.transaction.PlatformTransactionManager;

@Configuration
public class SeoulMarketPriceJobConfig {

    @Bean
    public Step seoulMarketPriceCollectStep(
            JobRepository jobRepository,
            PlatformTransactionManager transactionManager,
            SeoulMarketPriceCollectTasklet tasklet) {
        return new StepBuilder("seoulMarketPriceCollectStep", jobRepository)
                .tasklet(tasklet, transactionManager)
                .build();
    }

    @Bean
    public Step marketPriceSaveStep(
            JobRepository jobRepository,
            PlatformTransactionManager transactionManager,
            MarketPriceSaveTasklet tasklet) {
        return new StepBuilder("marketPriceSaveStep", jobRepository)
                .tasklet(tasklet, transactionManager)
                .build();
    }

    @Bean
    public Step aiSummaryStep(
            JobRepository jobRepository,
            PlatformTransactionManager transactionManager,
            AiSummaryTasklet tasklet) {
        return new StepBuilder("aiSummaryStep", jobRepository)
                .tasklet(tasklet, transactionManager)
                .build();
    }

    @Bean
    public Step pdfReportStep(
            JobRepository jobRepository,
            PlatformTransactionManager transactionManager,
            PdfReportTasklet tasklet) {
        return new StepBuilder("pdfReportStep", jobRepository)
                .tasklet(tasklet, transactionManager)
                .build();
    }

    @Bean
    public Job seoulMarketPriceJob(
            JobRepository jobRepository,
            Step seoulMarketPriceCollectStep,
            Step marketPriceSaveStep,
            Step aiSummaryStep,
            Step pdfReportStep) {
        return new JobBuilder("seoulMarketPriceJob", jobRepository)
                .incrementer(new RunIdIncrementer())
                .start(seoulMarketPriceCollectStep)
                .next(marketPriceSaveStep)
                .next(aiSummaryStep)
                .next(pdfReportStep)
                .build();
    }
}
