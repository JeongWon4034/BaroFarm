# FreshGrowth Seoul Market Batch

서울시농수산식품공사 공공데이터 API를 활용해 주요 농수산물 가격 데이터를 수집하고, DB 저장, AI 요약, PDF 리포트 생성을 자동화하는 Spring Batch 실습 프로젝트입니다.

## Batch Flow

```text
seoulMarketPriceJob
1. seoulMarketPriceCollectStep - 서울시 API 가격 데이터 수집
2. marketPriceSaveStep - 정제 데이터 DB 저장
3. aiSummaryStep - 가격 동향 및 판매자 조언 요약
4. pdfReportStep - PDF 리포트 생성
```

## Run

1. MySQL에 `freshgrowth_batch` 데이터베이스를 생성합니다.
2. `src/main/resources/application.properties`의 DB 계정, `seoul.api.key`, `spring.ai.openai.api-key`를 로컬 값으로 수정합니다.
3. Maven 프로젝트로 import 후 `FreshGrowthBatchApplication`을 실행합니다.

## Output

PDF는 `output/daily-market-report-YYYYMMDD.pdf` 경로에 생성됩니다.
