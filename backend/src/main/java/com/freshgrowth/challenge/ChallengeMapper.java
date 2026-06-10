package com.freshgrowth.challenge;

import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface ChallengeMapper {
    List<Challenge> findAll();
    Challenge findById(@Param("challengeId") Long challengeId);

    UserChallenge findUserChallenge(@Param("userId") Long userId, @Param("challengeId") Long challengeId);
    List<UserChallenge> findMyChallenges(@Param("userId") Long userId);
    void insertUserChallenge(UserChallenge userChallenge);

    // 진행도 갱신용 — 참여중(ONGOING)이고 목표유형이 일치하는 참여기록
    List<UserChallenge> findOngoingByUserAndType(@Param("userId") Long userId, @Param("goalType") String goalType);
    int incrementProgress(@Param("userChallengeId") Long userChallengeId);
    int markCompleted(@Param("userChallengeId") Long userChallengeId);
}
