package com.freshgrowth.product.ai.dto;

import java.util.List;

/**
 * AI 추천 레시피 — 현재 판매중인 재료로 만들 수 있는 가정식.
 * 각 재료(ingredient)는 가능하면 실제 판매 상품(productId)에 매핑되어,
 * 프론트에서 키워드를 누르면 해당 상품으로 연결된다.
 */
public class Recipe {
    private String title;                 // 요리명
    private String eyebrow;               // 상단 한 줄 문구
    private List<Ingredient> ingredients; // 핵심 재료(상품 매핑 포함)
    private List<String> steps;           // 상세: 조리 단계 텍스트
    private List<String> stepImages;      // 상세: 단계별 이미지 URL(steps와 같은 순서, 없으면 빈 문자열)
    private String image;                 // 대표(완성) 이미지 URL

    public Recipe() {}
    public Recipe(String title, String eyebrow, List<Ingredient> ingredients) {
        this.title = title;
        this.eyebrow = eyebrow;
        this.ingredients = ingredients;
    }

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }
    public String getEyebrow() { return eyebrow; }
    public void setEyebrow(String eyebrow) { this.eyebrow = eyebrow; }
    public List<Ingredient> getIngredients() { return ingredients; }
    public void setIngredients(List<Ingredient> ingredients) { this.ingredients = ingredients; }
    public List<String> getSteps() { return steps; }
    public void setSteps(List<String> steps) { this.steps = steps; }
    public List<String> getStepImages() { return stepImages; }
    public void setStepImages(List<String> stepImages) { this.stepImages = stepImages; }
    public String getImage() { return image; }
    public void setImage(String image) { this.image = image; }

    /** 재료 키워드 + 매핑된 판매 상품(없으면 null → 키워드 검색으로 연결). */
    public static class Ingredient {
        private String label;
        private Long productId;

        public Ingredient() {}
        public Ingredient(String label, Long productId) {
            this.label = label;
            this.productId = productId;
        }

        public String getLabel() { return label; }
        public void setLabel(String label) { this.label = label; }
        public Long getProductId() { return productId; }
        public void setProductId(Long productId) { this.productId = productId; }
    }
}
