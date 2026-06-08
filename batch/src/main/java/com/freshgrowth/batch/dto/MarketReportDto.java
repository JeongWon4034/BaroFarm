package com.freshgrowth.batch.dto;

import java.time.LocalDate;

public class MarketReportDto {

    private LocalDate reportDate;
    private String summary;
    private String pdfPath;

    public MarketReportDto(LocalDate reportDate, String summary, String pdfPath) {
        this.reportDate = reportDate;
        this.summary = summary;
        this.pdfPath = pdfPath;
    }

    public LocalDate getReportDate() {
        return reportDate;
    }

    public void setReportDate(LocalDate reportDate) {
        this.reportDate = reportDate;
    }

    public String getSummary() {
        return summary;
    }

    public void setSummary(String summary) {
        this.summary = summary;
    }

    public String getPdfPath() {
        return pdfPath;
    }

    public void setPdfPath(String pdfPath) {
        this.pdfPath = pdfPath;
    }
}
