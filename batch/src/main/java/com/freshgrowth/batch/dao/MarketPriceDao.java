package com.freshgrowth.batch.dao;

import java.util.List;

import com.freshgrowth.batch.dto.MarketReportDto;
import com.freshgrowth.batch.dto.SeoulMarketPriceDto;

public interface MarketPriceDao {

    int insertMarketPriceBatch(List<SeoulMarketPriceDto> list);

    int insertMarketReport(MarketReportDto report);
}
