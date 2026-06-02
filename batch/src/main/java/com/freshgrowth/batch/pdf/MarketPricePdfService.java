package com.freshgrowth.batch.pdf;

import com.freshgrowth.batch.dto.SeoulMarketPriceDto;
import com.openhtmltopdf.pdfboxout.PdfRendererBuilder;
import org.springframework.stereotype.Service;

import java.io.File;
import java.io.FileOutputStream;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.List;

@Service
public class MarketPricePdfService {

    public String createDailyReport(List<SeoulMarketPriceDto> priceList, String summary) throws Exception {
        String date = LocalDate.now().format(DateTimeFormatter.BASIC_ISO_DATE);
        File outputDir = new File("output");
        outputDir.mkdirs();

        String pdfPath = "output" + File.separator + "daily-market-report-" + date + ".pdf";
        String html = buildHtml(date, priceList, summary);

        try (FileOutputStream fos = new FileOutputStream(pdfPath)) {
            PdfRendererBuilder builder = new PdfRendererBuilder();
            builder.useFastMode();
            builder.withHtmlContent(html, new File(".").toURI().toString());
            builder.useFont(() -> getClass().getResourceAsStream("/fonts/NotoSansKR-Regular.ttf"), "NotoSansKR");
            builder.useFont(() -> getClass().getResourceAsStream("/fonts/NotoSansKR-Bold.ttf"), "NotoSansKRBold");
            builder.toStream(fos);
            builder.run();
        }

        return pdfPath;
    }

    private String buildHtml(String date, List<SeoulMarketPriceDto> priceList, String summary) {
        StringBuilder sb = new StringBuilder();
        sb.append("""
                <!DOCTYPE html>
                <html xmlns="http://www.w3.org/1999/xhtml">
                <head>
                  <meta charset="UTF-8" />
                  <style>
                    @page { size: A4; margin: 18mm; }
                    body { font-family: "NotoSansKR", Arial, sans-serif; color: #111; font-size: 12px; }
                    h1 { font-family: "NotoSansKRBold", "NotoSansKR", Arial, sans-serif; font-size: 22px; margin: 0 0 6px; }
                    h2 { font-family: "NotoSansKRBold", "NotoSansKR", Arial, sans-serif; font-size: 15px; margin-top: 18px; }
                    .muted { color: #666; }
                    .summary { white-space: pre-wrap; line-height: 1.6; border: 1px solid #eee; padding: 12px; }
                    table { width: 100%; border-collapse: collapse; margin-top: 10px; }
                    th { background: #f6f6f6; font-family: "NotoSansKRBold", "NotoSansKR", Arial, sans-serif; }
                    th, td { border-bottom: 1px solid #eee; padding: 7px; text-align: left; }
                  </style>
                </head>
                <body>
                """);

        sb.append("<h1>FreshGrowth Daily Market Report</h1>");
        sb.append("<div class=\"muted\">Generated on ").append(esc(date)).append("</div>");
        sb.append("<h2>AI Summary</h2>");
        sb.append("<div class=\"summary\">").append(esc(summary)).append("</div>");
        sb.append("<h2>Market Price Data</h2>");
        sb.append("<table>");
        sb.append("<tr><th>거래일</th><th>시장</th><th>품목</th><th>품종</th><th>등급</th><th>평균가</th><th>전일가</th><th>등락률</th></tr>");

        if (priceList != null) {
            for (SeoulMarketPriceDto p : priceList) {
                sb.append("<tr>");
                sb.append("<td>").append(esc(p.getTradeDate())).append("</td>");
                sb.append("<td>").append(esc(p.getMarketName())).append("</td>");
                sb.append("<td>").append(esc(p.getItemName())).append("</td>");
                sb.append("<td>").append(esc(p.getKindName())).append("</td>");
                sb.append("<td>").append(esc(p.getGradeName())).append("</td>");
                sb.append("<td>").append(esc(String.valueOf(p.getAvgPrice()))).append("</td>");
                sb.append("<td>").append(esc(String.valueOf(p.getPrevAvgPrice()))).append("</td>");
                sb.append("<td>").append(esc(p.getFluctuationRate())).append("</td>");
                sb.append("</tr>");
            }
        }

        sb.append("</table>");
        sb.append("</body></html>");
        return sb.toString();
    }

    private String esc(String value) {
        if (value == null) {
            return "";
        }
        return value.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace("\"", "&quot;")
                .replace("'", "&#39;");
    }
}
