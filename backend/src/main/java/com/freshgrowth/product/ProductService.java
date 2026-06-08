package com.freshgrowth.product;

import com.freshgrowth.common.AppException;
import com.freshgrowth.common.PageResponse;
import com.freshgrowth.product.dto.ProductRequest;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;

@Service
public class ProductService {
    private final ProductMapper productMapper;
    private final WastePricingEngine pricingEngine;

    public ProductService(ProductMapper productMapper, WastePricingEngine pricingEngine) {
        this.productMapper = productMapper;
        this.pricingEngine = pricingEngine;
    }

    @Transactional
    public Product create(Long sellerId, ProductRequest request) {
        Product product = toProduct(request);
        product.setSellerId(sellerId);
        productMapper.insert(product);
        return withPricing(productMapper.findById(product.getProductId()));
    }

    public PageResponse<Product> findAll(int page, int size) {
        int safePage = Math.max(page, 0);
        int safeSize = Math.min(Math.max(size, 1), 100);
        int offset = safePage * safeSize;
        List<Product> content = productMapper.findAll(offset, safeSize);
        content.forEach(pricingEngine::apply);
        long total = productMapper.countAll();
        return new PageResponse<>(content, safePage, safeSize, total);
    }

    public Product findById(Long productId) {
        Product product = productMapper.findById(productId);
        if (product == null) {
            throw new AppException(HttpStatus.NOT_FOUND, "PRODUCT_NOT_FOUND", "상품을 찾을 수 없습니다.");
        }
        return withPricing(product);
    }

    public List<Product> findSellerProducts(Long sellerId) {
        List<Product> products = productMapper.findBySellerId(sellerId);
        products.forEach(pricingEngine::apply);
        return products;
    }

    @Transactional
    public Product update(Long sellerId, Long productId, ProductRequest request) {
        findById(productId);
        Product product = toProduct(request);
        product.setProductId(productId);
        product.setSellerId(sellerId);
        int updated = productMapper.update(product);
        if (updated == 0) {
            throw new AppException(HttpStatus.FORBIDDEN, "FORBIDDEN", "수정 권한이 없습니다.");
        }
        return withPricing(productMapper.findById(productId));
    }

    @Transactional
    public void delete(Long sellerId, Long productId) {
        int deleted = productMapper.delete(productId, sellerId);
        if (deleted == 0) {
            throw new AppException(HttpStatus.FORBIDDEN, "FORBIDDEN", "삭제 권한이 없거나 상품이 없습니다.");
        }
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
