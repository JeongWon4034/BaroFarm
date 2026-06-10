package com.freshgrowth.challenge;

import java.time.LocalDateTime;

/**
 * 사용자의 챌린지 참여 기록. 조회 시 challenges 테이블을 조인해
 * 화면 표시용 챌린지 정보(title/goalCount/badge)도 함께 담는다.
 */
public class UserChallenge {
    private Long userChallengeId;
    private Long userId;
    private Long challengeId;
    private String status;        // ONGOING / COMPLETED
    private Integer progress;
    private LocalDateTime joinedAt;
    private LocalDateTime completedAt;

    // 조인된 챌린지 정보(목록/달성 로그 표시용)
    private String title;
    private String description;
    private Integer goalCount;
    private String badgeEmoji;

    public Long getUserChallengeId() { return userChallengeId; }
    public void setUserChallengeId(Long userChallengeId) { this.userChallengeId = userChallengeId; }
    public Long getUserId() { return userId; }
    public void setUserId(Long userId) { this.userId = userId; }
    public Long getChallengeId() { return challengeId; }
    public void setChallengeId(Long challengeId) { this.challengeId = challengeId; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    public Integer getProgress() { return progress; }
    public void setProgress(Integer progress) { this.progress = progress; }
    public LocalDateTime getJoinedAt() { return joinedAt; }
    public void setJoinedAt(LocalDateTime joinedAt) { this.joinedAt = joinedAt; }
    public LocalDateTime getCompletedAt() { return completedAt; }
    public void setCompletedAt(LocalDateTime completedAt) { this.completedAt = completedAt; }
    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    public Integer getGoalCount() { return goalCount; }
    public void setGoalCount(Integer goalCount) { this.goalCount = goalCount; }
    public String getBadgeEmoji() { return badgeEmoji; }
    public void setBadgeEmoji(String badgeEmoji) { this.badgeEmoji = badgeEmoji; }
}
