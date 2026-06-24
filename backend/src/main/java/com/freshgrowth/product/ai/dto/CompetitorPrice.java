package com.freshgrowth.product.ai.dto;

/** 네이버 쇼핑 검색 1건 — 경쟁 소매가 비교용(컬리 등 외부 몰의 유사상품 1개). */
public class CompetitorPrice {
    private String title;   // 상품명(HTML 태그 제거됨)
    private String mall;    // 판매처(mallName) 예: 마켓컬리
    private Integer price;   // 최저가(lprice)
    private String link;    // 상품 링크
    private String image;   // 상품 썸네일 URL — 실제 판매 화면처럼 보여주기 위함
    private String brand;   // 브랜드(있을 때)

    public CompetitorPrice() {}

    public CompetitorPrice(String title, String mall, Integer price, String link, String image, String brand) {
        this.title = title;
        this.mall = mall;
        this.price = price;
        this.link = link;
        this.image = image;
        this.brand = brand;
    }

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }
    public String getMall() { return mall; }
    public void setMall(String mall) { this.mall = mall; }
    public Integer getPrice() { return price; }
    public void setPrice(Integer price) { this.price = price; }
    public String getLink() { return link; }
    public void setLink(String link) { this.link = link; }
    public String getImage() { return image; }
    public void setImage(String image) { this.image = image; }
    public String getBrand() { return brand; }
    public void setBrand(String brand) { this.brand = brand; }
}
