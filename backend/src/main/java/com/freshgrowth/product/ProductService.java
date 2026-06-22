package com.freshgrowth.product;

import com.freshgrowth.common.AppException;
import com.freshgrowth.common.PageResponse;
import com.freshgrowth.product.dto.ProductRequest;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;
import java.util.Set;

@Service
public class ProductService {
    private static final Set<String> VALID_SORTS = Set.of("latest", "priceAsc", "priceDesc", "expiry");

    private final ProductMapper productMapper;
    private final ProductLotMapper lotMapper;
    private final WastePricingEngine pricingEngine;

    public ProductService(ProductMapper productMapper, ProductLotMapper lotMapper,
                          WastePricingEngine pricingEngine) {
        this.productMapper = productMapper;
        this.lotMapper = lotMapper;
        this.pricingEngine = pricingEngine;
    }

    @Transactional
    public Product create(Long sellerId, ProductRequest request) {
        Product product = toProduct(request);
        product.setSellerId(sellerId);
        productMapper.insert(product);
        return withPricing(productMapper.findById(product.getProductId()));
    }

    public PageResponse<Product> findAll(int page, int size, String keyword, String category, String sort) {
        int safePage = Math.max(page, 0);
        int safeSize = Math.min(Math.max(size, 1), 100);
        int offset = safePage * safeSize;
        String safeKeyword = (keyword != null && !keyword.isBlank()) ? keyword.trim() : null;
        String safeCategory = (category != null && !category.isBlank()) ? category.trim() : null;
        String safeSort = sort != null && VALID_SORTS.contains(sort) ? sort : "latest";
        List<Product> content = productMapper.findAll(offset, safeSize, safeKeyword, safeCategory, safeSort);
        content.forEach(pricingEngine::apply);
        long total = productMapper.countAll(safeKeyword, safeCategory);
        return new PageResponse<>(content, safePage, safeSize, total);
    }

    public Product findById(Long productId) {
        Product product = productMapper.findById(productId);
        if (product == null) {
            throw new AppException(HttpStatus.NOT_FOUND, "PRODUCT_NOT_FOUND", "상품을 찾을 수 없습니다.");
        }
        withPricing(product);
        product.setLots(findLots(productId));   // 상세: 폐기기간별 옵션 + 옵션별 떨이가
        return product;
    }

    /** 한 품목의 폐기기간 옵션(lot) 목록 + 옵션별 동적 떨이가. */
    public List<ProductLot> findLots(Long productId) {
        List<ProductLot> lots = lotMapper.findByProductId(productId);
        lots.forEach(pricingEngine::apply);
        return lots;
    }

    public List<Product> findSellerProducts(Long sellerId) {
        List<Product> products = productMapper.findBySellerId(sellerId);
        products.forEach(pricingEngine::apply);
        return products;
    }

    @Transactional
    public Product update(Long sellerId, Long productId, ProductRequest request) {
        Product existing = productMapper.findById(productId);
        if (existing == null) {
            throw new AppException(HttpStatus.NOT_FOUND, "PRODUCT_NOT_FOUND", "상품을 찾을 수 없습니다.");
        }
        if (!existing.getSellerId().equals(sellerId)) {
            throw new AppException(HttpStatus.FORBIDDEN, "FORBIDDEN", "수정 권한이 없습니다.");
        }
        Product product = toProduct(request);
        product.setProductId(productId);
        product.setSellerId(sellerId);
        productMapper.update(product);
        return withPricing(productMapper.findById(productId));
    }

    @Transactional
    public void delete(Long sellerId, Long productId) {
        Product existing = productMapper.findById(productId);
        if (existing == null) {
            throw new AppException(HttpStatus.NOT_FOUND, "PRODUCT_NOT_FOUND", "상품을 찾을 수 없습니다.");
        }
        if (!existing.getSellerId().equals(sellerId)) {
            throw new AppException(HttpStatus.FORBIDDEN, "FORBIDDEN", "삭제 권한이 없습니다.");
        }
        productMapper.delete(productId, sellerId);
    }

    private Product withPricing(Product product) {
        pricingEngine.apply(product);
        return product;
    }

    private Product toProduct(ProductRequest request) {
        Product product = new Product();
        product.setName(request.getName());
        product.setDescription(request.getDescription());
        product.setCategory(request.getCategory());
        product.setPrice(request.getPrice());
        product.setStockQty(request.getStockQty());
        product.setThumbnailUrl(request.getThumbnailUrl());
        product.setExpirationDate(request.getExpirationDate());
        return product;
    }
}
