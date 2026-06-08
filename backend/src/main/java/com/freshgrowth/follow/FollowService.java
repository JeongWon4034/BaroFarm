package com.freshgrowth.follow;

import com.freshgrowth.common.AppException;
import com.freshgrowth.follow.dto.SellerSummary;
import com.freshgrowth.user.User;
import com.freshgrowth.user.UserMapper;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class FollowService {
    private final FollowMapper followMapper;
    private final UserMapper userMapper;

    public FollowService(FollowMapper followMapper, UserMapper userMapper) {
        this.followMapper = followMapper;
        this.userMapper = userMapper;
    }

    @Transactional
    public void follow(Long buyerId, Long sellerId) {
        if (buyerId.equals(sellerId)) {
            throw new AppException(HttpStatus.BAD_REQUEST, "INVALID_FOLLOW", "자기 자신을 팔로우할 수 없습니다.");
        }
        requireSeller(sellerId);
        followMapper.insert(buyerId, sellerId);
    }

    @Transactional
    public void unfollow(Long buyerId, Long sellerId) {
        followMapper.delete(buyerId, sellerId);
    }

    public List<SellerSummary> findFollowing(Long buyerId) {
        List<SellerSummary> sellers = followMapper.findFollowingSellers(buyerId);
        sellers.forEach(s -> s.setIsFollowing(true));
        return sellers;
    }

    public SellerSummary getSellerSummary(Long sellerId, Long viewerId) {
        SellerSummary summary = followMapper.findSellerSummary(sellerId);
        if (summary == null) {
            throw new AppException(HttpStatus.NOT_FOUND, "SELLER_NOT_FOUND", "판매자를 찾을 수 없습니다.");
        }
        summary.setIsFollowing(viewerId != null && followMapper.exists(viewerId, sellerId) > 0);
        return summary;
    }

    private void requireSeller(Long sellerId) {
        User seller = userMapper.findById(sellerId);
        if (seller == null || !"SELLER".equals(seller.getRole())) {
            throw new AppException(HttpStatus.NOT_FOUND, "SELLER_NOT_FOUND", "판매자를 찾을 수 없습니다.");
        }
    }
}
