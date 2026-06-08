package com.freshgrowth.follow;

import com.freshgrowth.follow.dto.SellerSummary;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface FollowMapper {
    int insert(@Param("followerId") Long followerId, @Param("followingId") Long followingId);
    int delete(@Param("followerId") Long followerId, @Param("followingId") Long followingId);
    int exists(@Param("followerId") Long followerId, @Param("followingId") Long followingId);
    List<SellerSummary> findFollowingSellers(@Param("buyerId") Long buyerId);
    SellerSummary findSellerSummary(@Param("sellerId") Long sellerId);
}
