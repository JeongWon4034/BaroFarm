package com.freshgrowth.product;

import com.freshgrowth.common.ApiResponse;
import com.freshgrowth.product.dto.ProductRequest;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1")
public class ProductController {
    private final ProductService productService;

    public ProductController(ProductService productService) {
        this.productService = productService;
    }

    @GetMapping("/products")
    public ApiResponse<?> findAll(@RequestParam(defaultValue = "0") int page,
                                  @RequestParam(defaultValue = "10") int size) {
        return ApiResponse.ok("상품 목록을 조회했습니다.", productService.findAll(page, size));
    }

    @GetMapping("/products/{productId}")
    public ApiResponse<?> findById(@PathVariable Long productId) {
        return ApiResponse.ok("상품 상세 정보를 조회했습니다.", productService.findById(productId));
    }

    @PostMapping("/products")
    public ApiResponse<?> create(@RequestHeader("X-USER-ID") Long sellerId,
                                 @Valid @RequestBody ProductRequest request) {
        return ApiResponse.ok("상품이 등록되었습니다.", productService.create(sellerId, request));
    }

    @PutMapping("/products/{productId}")
    public ApiResponse<?> update(@RequestHeader("X-USER-ID") Long sellerId,
                                 @PathVariable Long productId,
                                 @Valid @RequestBody ProductRequest request) {
        return ApiResponse.ok("상품이 수정되었습니다.", productService.update(sellerId, productId, request));
    }

    @DeleteMapping("/products/{productId}")
    public ApiResponse<Void> delete(@RequestHeader("X-USER-ID") Long sellerId,
                                    @PathVariable Long productId) {
        productService.delete(sellerId, productId);
        return ApiResponse.ok("상품이 삭제되었습니다.", null);
    }

    @GetMapping("/seller/products")
    public ApiResponse<?> findSellerProducts(@RequestHeader("X-USER-ID") Long sellerId) {
        return ApiResponse.ok("판매자 상품 목록을 조회했습니다.", productService.findSellerProducts(sellerId));
    }
}
