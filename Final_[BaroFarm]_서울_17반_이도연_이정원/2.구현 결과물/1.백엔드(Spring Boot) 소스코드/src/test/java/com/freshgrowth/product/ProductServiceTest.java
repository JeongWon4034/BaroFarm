package com.freshgrowth.product;

import com.freshgrowth.common.AppException;
import com.freshgrowth.common.PageResponse;
import com.freshgrowth.product.dto.ProductRequest;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.http.HttpStatus;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.BDDMockito.given;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class ProductServiceTest {

    @Mock ProductMapper productMapper;
    @Mock ProductLotMapper lotMapper;
    @Mock WastePricingEngine pricingEngine;
    @InjectMocks ProductService productService;

    // ── 헬퍼 ─────────────────────────────────────────────────────────────────

    private Product product(Long productId, Long sellerId) {
        Product p = new Product();
        p.setProductId(productId);
        p.setSellerId(sellerId);
        p.setName("테스트 상품");
        p.setPrice(5000);
        return p;
    }

    private ProductRequest stubRequest() {
        ProductRequest r = mock(ProductRequest.class);
        lenient().when(r.getName()).thenReturn("수정 상품");
        lenient().when(r.getPrice()).thenReturn(6000);
        lenient().when(r.getStockQty()).thenReturn(10);
        return r;
    }

    // ━━━━ findAll — 검색 조건 정규화 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    private void stubFindAll(long total) {
        doReturn(new java.util.ArrayList<Product>())
                .when(productMapper).findAll(anyInt(), anyInt(), any(), any(), any());
        doReturn(total).when(productMapper).countAll(any(), any());
    }

    @Test
    @DisplayName("findAll: keyword 앞뒤 공백 trim 후 전달")
    void findAll_keyword_is_trimmed() {
        stubFindAll(0L);
        productService.findAll(0, 12, "  상추  ", null, null);

        ArgumentCaptor<String> kwCaptor = ArgumentCaptor.forClass(String.class);
        verify(productMapper).findAll(anyInt(), anyInt(), kwCaptor.capture(), any(), any());
        assertThat(kwCaptor.getValue()).isEqualTo("상추");
    }

    @Test
    @DisplayName("findAll: 공백만 있는 keyword → null로 정규화")
    void findAll_blank_keyword_becomes_null() {
        stubFindAll(0L);
        productService.findAll(0, 12, "   ", null, null);

        ArgumentCaptor<String> kwCaptor = ArgumentCaptor.forClass(String.class);
        verify(productMapper).findAll(anyInt(), anyInt(), kwCaptor.capture(), any(), any());
        assertThat(kwCaptor.getValue()).isNull();
    }

    @Test
    @DisplayName("findAll: sort null → 기본값 latest")
    void findAll_null_sort_defaults_to_latest() {
        stubFindAll(0L);
        productService.findAll(0, 12, null, null, null);

        ArgumentCaptor<String> sortCaptor = ArgumentCaptor.forClass(String.class);
        verify(productMapper).findAll(anyInt(), anyInt(), any(), any(), sortCaptor.capture());
        assertThat(sortCaptor.getValue()).isEqualTo("latest");
    }

    @Test
    @DisplayName("findAll: 허용되지 않은 sort 값 → latest로 강제 (SQL injection 방어)")
    void findAll_invalid_sort_falls_back_to_latest() {
        stubFindAll(0L);
        productService.findAll(0, 12, null, null, "'; DROP TABLE products; --");

        ArgumentCaptor<String> sortCaptor = ArgumentCaptor.forClass(String.class);
        verify(productMapper).findAll(anyInt(), anyInt(), any(), any(), sortCaptor.capture());
        assertThat(sortCaptor.getValue()).isEqualTo("latest");
    }

    @Test
    @DisplayName("findAll: 허용된 sort 값(priceAsc, priceDesc, expiry, latest) 그대로 전달")
    void findAll_valid_sorts_passed_through() {
        stubFindAll(0L);
        for (String sort : List.of("priceAsc", "priceDesc", "expiry", "latest")) {
            productService.findAll(0, 12, null, null, sort);
        }

        ArgumentCaptor<String> sortCaptor = ArgumentCaptor.forClass(String.class);
        verify(productMapper, times(4)).findAll(anyInt(), anyInt(), any(), any(), sortCaptor.capture());
        assertThat(sortCaptor.getAllValues()).containsExactlyInAnyOrder("priceAsc", "priceDesc", "expiry", "latest");
    }

    @Test
    @DisplayName("findAll: page 음수 → 0, size 200 → 100(clamp)")
    void findAll_page_and_size_clamped() {
        stubFindAll(0L);
        productService.findAll(-5, 200, null, null, null);

        ArgumentCaptor<Integer> offsetCaptor = ArgumentCaptor.forClass(Integer.class);
        ArgumentCaptor<Integer> sizeCaptor = ArgumentCaptor.forClass(Integer.class);
        verify(productMapper).findAll(offsetCaptor.capture(), sizeCaptor.capture(), any(), any(), any());
        assertThat(offsetCaptor.getValue()).isEqualTo(0);
        assertThat(sizeCaptor.getValue()).isEqualTo(100);
    }

    @Test
    @DisplayName("findAll: PageResponse 메타(page, size, totalElements) 포함")
    void findAll_returns_page_meta() {
        stubFindAll(42L);
        PageResponse<Product> result = productService.findAll(2, 10, null, null, null);

        assertThat(result.getPage()).isEqualTo(2);
        assertThat(result.getSize()).isEqualTo(10);
        assertThat(result.getTotalElements()).isEqualTo(42L);
    }

    // ━━━━ findById ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    @Test
    @DisplayName("findById: 존재하는 상품 → pricingEngine 적용 후 반환")
    void findById_found_applies_pricing() {
        given(productMapper.findById(1L)).willReturn(product(1L, 10L));
        productService.findById(1L);
        verify(pricingEngine).apply(any(Product.class));
    }

    @Test
    @DisplayName("findById: 없는 상품 → 404 PRODUCT_NOT_FOUND")
    void findById_not_found_throws_404() {
        given(productMapper.findById(99L)).willReturn(null);
        assertThatThrownBy(() -> productService.findById(99L))
                .isInstanceOf(AppException.class)
                .extracting("status").isEqualTo(HttpStatus.NOT_FOUND);
    }

    // ━━━━ update — 소유권 분리 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    @Test
    @DisplayName("update: 상품 없음 → 404 PRODUCT_NOT_FOUND")
    void update_product_not_found_throws_404() {
        given(productMapper.findById(1L)).willReturn(null);
        assertThatThrownBy(() -> productService.update(10L, 1L, mock(ProductRequest.class)))
                .isInstanceOf(AppException.class)
                .extracting("status").isEqualTo(HttpStatus.NOT_FOUND);
    }

    @Test
    @DisplayName("update: 타인 상품 → 403 FORBIDDEN (not_found와 구분)")
    void update_other_seller_throws_403() {
        given(productMapper.findById(1L)).willReturn(product(1L, 99L)); // 소유자 99L
        assertThatThrownBy(() -> productService.update(10L, 1L, mock(ProductRequest.class))) // 요청자 10L
                .isInstanceOf(AppException.class)
                .extracting("status").isEqualTo(HttpStatus.FORBIDDEN);
    }

    @Test
    @DisplayName("update: 본인 상품 → update 쿼리 실행")
    void update_owner_succeeds() {
        given(productMapper.findById(1L)).willReturn(product(1L, 10L));
        productService.update(10L, 1L, stubRequest());
        verify(productMapper).update(any());
    }

    // ━━━━ delete — 소유권 분리 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    @Test
    @DisplayName("delete: 상품 없음 → 404 PRODUCT_NOT_FOUND")
    void delete_product_not_found_throws_404() {
        given(productMapper.findById(1L)).willReturn(null);
        assertThatThrownBy(() -> productService.delete(10L, 1L))
                .isInstanceOf(AppException.class)
                .extracting("status").isEqualTo(HttpStatus.NOT_FOUND);
    }

    @Test
    @DisplayName("delete: 타인 상품 → 403 FORBIDDEN (not_found와 구분)")
    void delete_other_seller_throws_403() {
        given(productMapper.findById(1L)).willReturn(product(1L, 99L)); // 소유자 99L
        assertThatThrownBy(() -> productService.delete(10L, 1L)) // 요청자 10L
                .isInstanceOf(AppException.class)
                .extracting("status").isEqualTo(HttpStatus.FORBIDDEN);
    }

    @Test
    @DisplayName("delete: 본인 상품 → delete 쿼리 실행")
    void delete_owner_succeeds() {
        given(productMapper.findById(1L)).willReturn(product(1L, 10L));
        productService.delete(10L, 1L);
        verify(productMapper).delete(1L, 10L);
    }
}
