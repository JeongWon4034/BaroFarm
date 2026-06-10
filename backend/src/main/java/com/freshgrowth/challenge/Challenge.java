package com.freshgrowth.challenge;

import java.time.LocalDateTime;

public class Challenge {
    private Long challengeId;
    private String title;
    private String description;
    private String goalType;     // 목표 유형 (DEADLINE_PURCHASE = 마감임박 상품 구매)
    private Integer goalCount;    // 달성 목표 횟수
    private Integer periodDays;
    private String badgeEmoji;
    private LocalDateTime createdAt;

    public Long getChallengeId() { return challengeId; }
    public void setChallengeId(Long challengeId) { this.challengeId = challengeId; }
    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    public String getGoalType() { return goalType; }
    public void setGoalType(String goalType) { this.goalType = goalType; }
    public Integer getGoalCount() { return goalCount; }
    public void setGoalCount(Integer goalCount) { this.goalCount = goalCount; }
    public Integer getPeriodDays() { return periodDays; }
    public void setPeriodDays(Integer periodDays) { this.periodDays = periodDays; }
    public String getBadgeEmoji() { return badgeEmoji; }
    public void setBadgeEmoji(String badgeEmoji) { this.badgeEmoji = badgeEmoji; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
}
