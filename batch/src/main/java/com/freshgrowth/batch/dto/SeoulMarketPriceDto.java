package com.freshgrowth.batch.dto;

import java.io.Serializable;

public class SeoulMarketPriceDto implements Serializable {

    private static final long serialVersionUID = 1L;

    private String tradeDate;
    private String marketName;
    private String itemName;
    private String itemCode;
    private String kindName;
    private String gradeName;
    private String unitQty;
    private Integer avgPrice;
    private Integer prevAvgPrice;
    private Integer prevYearPrice;
    private String fluctuationRate;
    private String rawJson;

    public String getTradeDate() {
        return tradeDate;
    }

    public void setTradeDate(String tradeDate) {
        this.tradeDate = tradeDate;
    }

    public String getMarketName() {
        return marketName;
    }

    public void setMarketName(String marketName) {
        this.marketName = marketName;
    }

    public String getItemName() {
        return itemName;
    }

    public void setItemName(String itemName) {
        this.itemName = itemName;
    }

    public String getItemCode() {
        return itemCode;
    }

    public void setItemCode(String itemCode) {
        this.itemCode = itemCode;
    }

    public String getKindName() {
        return kindName;
    }

    public void setKindName(String kindName) {
        this.kindName = kindName;
    }

    public String getGradeName() {
        return gradeName;
    }

    public void setGradeName(String gradeName) {
        this.gradeName = gradeName;
    }

    public String getUnitQty() {
        return unitQty;
    }

    public void setUnitQty(String unitQty) {
        this.unitQty = unitQty;
    }

    public Integer getAvgPrice() {
        return avgPrice;
    }

    public void setAvgPrice(Integer avgPrice) {
        this.avgPrice = avgPrice;
    }

    public Integer getPrevAvgPrice() {
        return prevAvgPrice;
    }

    public void setPrevAvgPrice(Integer prevAvgPrice) {
        this.prevAvgPrice = prevAvgPrice;
    }

    public Integer getPrevYearPrice() {
        return prevYearPrice;
    }

    public void setPrevYearPrice(Integer prevYearPrice) {
        this.prevYearPrice = prevYearPrice;
    }

    public String getFluctuationRate() {
        return fluctuationRate;
    }

    public void setFluctuationRate(String fluctuationRate) {
        this.fluctuationRate = fluctuationRate;
    }

    public String getRawJson() {
        return rawJson;
    }

    public void setRawJson(String rawJson) {
        this.rawJson = rawJson;
    }
}
