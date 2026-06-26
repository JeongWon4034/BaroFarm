package com.freshgrowth.challenge;

import com.freshgrowth.common.AppException;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class ChallengeService {
    private static final String DEADLINE_PURCHASE = "DEADLINE_PURCHASE";

    private final ChallengeMapper challengeMapper;
    private final com.freshgrowth.coupon.CouponService couponService;

    public ChallengeService(ChallengeMapper challengeMapper,
                            com.freshgrowth.coupon.CouponService couponService) {
        this.challengeMapper = challengeMapper;
        this.couponService = couponService;
    }

    public List<Challenge> findAll() {
        return challengeMapper.findAll();
    }

    public Challenge findById(Long challengeId) {
        Challenge challenge = challengeMapper.findById(challengeId);
        if (challenge == null) {
            throw new AppException(HttpStatus.NOT_FOUND, "CHALLENGE_NOT_FOUND", "챌린지를 찾을 수 없습니다.");
        }
        return challenge;
    }

    public List<UserChallenge> findMyChallenges(Long userId) {
        return challengeMapper.findMyChallenges(userId);
    }

    @Transactional
    public UserChallenge join(Long userId, Long challengeId) {
        findById(challengeId); // 존재 검증(404)
        if (challengeMapper.findUserChallenge(userId, challengeId) != null) {
            throw new AppException(HttpStatus.CONFLICT, "ALREADY_JOINED", "이미 참여한 챌린지입니다.");
        }
        UserChallenge uc = new UserChallenge();
        uc.setUserId(userId);
        uc.setChallengeId(challengeId);
        challengeMapper.insertUserChallenge(uc);
        return challengeMapper.findUserChallenge(userId, challengeId);
    }

    /**
     * 마감임박 상품 구매 시 호출. 참여중인 DEADLINE_PURCHASE 챌린지의 진행도를 +1 하고,
     * 목표에 도달하면 달성(COMPLETED) 처리한다. (주문 흐름에서 호출)
     */
    @Transactional
    public void recordDeadlinePurchase(Long userId) {
        List<UserChallenge> ongoing = challengeMapper.findOngoingByUserAndType(userId, DEADLINE_PURCHASE);
        for (UserChallenge uc : ongoing) {
            challengeMapper.incrementProgress(uc.getUserChallengeId());
            int newProgress = (uc.getProgress() == null ? 0 : uc.getProgress()) + 1;
            if (newProgress >= uc.getGoalCount()
                    && challengeMapper.markCompleted(uc.getUserChallengeId()) > 0) {
                // 막 완료된 경우에만 보상 쿠폰 발급(중복 완료는 markCompleted가 0 반환)
                int rate = uc.getRewardDiscountRate() == null ? 10 : uc.getRewardDiscountRate();
                couponService.issueForChallenge(userId, uc.getChallengeId(), rate);
            }
        }
    }
}
