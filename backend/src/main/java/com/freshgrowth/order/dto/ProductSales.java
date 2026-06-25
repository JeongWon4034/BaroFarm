package com.freshgrowth.order.dto;

import java.util.List;

/**
 * 판매자 상품 1개의 판매 분석 — 언제(최근판매일·14일 추이)·어떻게(마감임박 비중)·얼마나(판매량·매출·절약회수).
 * 판매자 상품 표에서 productId로 매칭해 펼쳐 보여준다.
 */
public class ProductSales {
    private Long productId;
    private int soldQty;        // 총 판매 수량
    private long revenue;       // 총 매출(실결제액 합)
    private long saved;         // 마감임박 할인으로 회수/절약된 금액 합(정가-결제액)
    private int orderCount;     // 주문 건수
    private int deadlineQty;    // 마감임박(할인) 구매로 팔린 수량
    private String lastOrderDate; // 최근 판매일(yyyy-MM-dd), 없으면 null
    private List<DayPoint> daily14; // 최근 14일 일별 판매 수량(추이 스파크라인)

    public static class DayPoint {
        private final String date; // 표시용 라벨 'M/d'
        private int qty;
        public DayPoint(String date) { this.date = date; }
        public void add(int q) { this.qty += q; }
        public String getDate() { return date; }
        public int getQty() { return qty; }
    }

    public Long getProductId() { return productId; }
    public void setProductId(Long productId) { this.productId = productId; }
    public int getSoldQty() { return soldQty; }
    public void setSoldQty(int soldQty) { this.soldQty = soldQty; }
    public long getRevenue() { return revenue; }
    public void setRevenue(long revenue) { this.revenue = revenue; }
    public long getSaved() { return saved; }
    public void setSaved(long saved) { this.saved = saved; }
    public int getOrderCount() { return orderCount; }
    public void setOrderCount(int orderCount) { this.orderCount = orderCount; }
    public int getDeadlineQty() { return deadlineQty; }
    public void setDeadlineQty(int deadlineQty) { this.deadlineQty = deadlineQty; }
    public String getLastOrderDate() { return lastOrderDate; }
    public void setLastOrderDate(String lastOrderDate) { this.lastOrderDate = lastOrderDate; }
    public List<DayPoint> getDaily14() { return daily14; }
    public void setDaily14(List<DayPoint> daily14) { this.daily14 = daily14; }
}
