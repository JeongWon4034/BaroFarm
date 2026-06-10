package com.freshgrowth.review;

import com.freshgrowth.common.AppException;
import com.freshgrowth.order.Order;
import com.freshgrowth.order.OrderMapper;
import com.freshgrowth.review.dto.ReviewRequest;
import com.freshgrowth.review.dto.ReviewUpdateRequest;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;

@Service
public class ReviewService {
    private final ReviewMapper reviewMapper;
    private final OrderMapper orderMapper;

    public ReviewService(ReviewMapper reviewMapper, OrderMapper orderMapper) {
        this.reviewMapper = reviewMapper;
        this.orderMapper = orderMapper;
    }

    @Transactional
    public Review create(Long buyerId, ReviewRequest request) {
        Order order = orderMapper.findById(request.getOrderId());
        if (order == null) {
            throw new AppException(HttpStatus.NOT_FOUND, "ORDER_NOT_FOUND", "주문을 찾을 수 없습니다.");
        }
        if (!order.getBuyerId().equals(buyerId)) {
            throw new AppException(HttpStatus.FORBIDDEN, "FORBIDDEN", "본인 주문만 리뷰할 수 있습니다.");
        }
        if (reviewMapper.findByOrderId(request.getOrderId()) != null) {
            throw new AppException(HttpStatus.CONFLICT, "DUPLICATED_REVIEW", "이미 리뷰를 작성한 주문입니다.");
        }

        Review review = new Review();
        review.setOrderId(request.getOrderId());
        review.setRating(request.getRating());
        review.setContent(request.getContent());
        reviewMapper.insert(review);
        return reviewMapper.findById(review.getReviewId());
    }

    public List<Review> findByProductId(Long productId) {
        return reviewMapper.findByProductId(productId);
    }

    @Transactional
    public Review update(Long buyerId, Long reviewId, ReviewUpdateRequest request) {
        requireOwnedReview(buyerId, reviewId);
        reviewMapper.update(reviewId, request.getRating(), request.getContent());
        return reviewMapper.findById(reviewId);
    }

    @Transactional
    public void delete(Long buyerId, Long reviewId) {
        requireOwnedReview(buyerId, reviewId);
        reviewMapper.delete(reviewId);
    }

    // 리뷰 존재 + 본인(주문 구매자) 소유 검증
    private void requireOwnedReview(Long buyerId, Long reviewId) {
        Review review = reviewMapper.findById(reviewId);
        if (review == null) {
            throw new AppException(HttpStatus.NOT_FOUND, "REVIEW_NOT_FOUND", "리뷰를 찾을 수 없습니다.");
        }
        if (!review.getBuyerId().equals(buyerId)) {
            throw new AppException(HttpStatus.FORBIDDEN, "FORBIDDEN", "본인 리뷰만 수정·삭제할 수 있습니다.");
        }
    }
}
