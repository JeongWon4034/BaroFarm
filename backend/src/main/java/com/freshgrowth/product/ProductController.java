package com.freshgrowth.product;

import com.freshgrowth.common.ApiResponse;
import com.freshgrowth.common.auth.LoginRequired;
import com.freshgrowth.common.auth.LoginUser;
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

    @LoginRequired(role = "SELLER")
    @PostMapping("/products")
    public ApiResponse<?> create(@LoginUser Long sellerId,
                                 @Valid @RequestBody ProductRequest request) {
        return ApiResponse.ok("상품이 등록되었습니다.", productService.create(sellerId, request));
    }

    @LoginRequired(role = "SELLER")
    @PutMapping("/products/{productId}")
    public ApiResponse<?> update(@LoginUser Long sellerId,
                                 @PathVariable Long productId,
                                 @Valid @RequestBody ProductRequest request) {
        return ApiResponse.ok("상품이 수정되었습니다.", productService.update(sellerId, productId, request));
    }

    @LoginRequired(role = "SELLER")
    @DeleteMapping("/products/{productId}")
    public ApiResponse<Void> delete(@LoginUser Long sellerId,
                                    @PathVariable Long productId) {
        productService.delete(sellerId, productId);
        return ApiResponse.ok("상품이 삭제되었습니다.", null);
    }

    @LoginRequired(role = "SELLER")
    @GetMapping("/seller/products")
    public ApiResponse<?> findSellerProducts(@LoginUser Long sellerId) {
        return ApiResponse.ok("판매자 상품 목록을 조회했습니다.", productService.findSellerProducts(sellerId));
    }
}
