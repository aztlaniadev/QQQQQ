"""
Advanced Gamification Models
Comprehensive models for achievements, badges, streaks, and competition
"""

from datetime import datetime, date
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from enum import Enum


class AchievementCategory(str, Enum):
    """Achievement categories"""
    BEGINNER = "beginner"
    CONTRIBUTOR = "contributor"
    EXPERT = "expert"
    SOCIAL = "social"
    SPECIAL = "special"
    MILESTONE = "milestone"
    STREAK = "streak"
    COMPETITIVE = "competitive"


class AchievementRarity(str, Enum):
    """Achievement rarity levels"""
    COMMON = "common"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


class BadgeType(str, Enum):
    """Badge types"""
    ACHIEVEMENT = "achievement"
    RANK = "rank"
    SPECIAL = "special"
    EVENT = "event"
    MILESTONE = "milestone"


class StreakType(str, Enum):
    """Streak types"""
    DAILY_LOGIN = "daily_login"
    QUESTION_ANSWERED = "question_answered"
    DAILY_ACTIVITY = "daily_activity"
    WEEKLY_GOAL = "weekly_goal"


# ===========================================
# ACHIEVEMENT MODELS
# ===========================================

class AchievementCriteria(BaseModel):
    """Criteria for earning an achievement"""
    condition_type: Literal["points", "count", "streak", "special"] = "count"
    target_value: int
    target_field: Optional[str] = None  # e.g., "questions_created", "pc_points"
    additional_conditions: Optional[Dict[str, Any]] = None


class Achievement(BaseModel):
    """Advanced achievement model"""
    id: str
    name: str
    description: str
    category: AchievementCategory
    rarity: AchievementRarity
    badge_icon: str = "🏆"
    badge_color: str = "#FFD700"
    criteria: AchievementCriteria
    points_reward: int = 0
    pcon_reward: int = 0
    is_hidden: bool = False  # Hidden until earned
    is_repeatable: bool = False
    sort_order: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserAchievement(BaseModel):
    """User's earned achievement"""
    id: str
    user_id: str
    achievement_id: str
    achievement: Optional[Achievement] = None
    progress: int = 0  # Current progress towards achievement
    earned_at: Optional[datetime] = None
    is_earned: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AchievementProgress(BaseModel):
    """Achievement progress tracking"""
    achievement_id: str
    achievement: Achievement
    current_progress: int
    target_progress: int
    percentage: float
    is_earned: bool
    earned_at: Optional[datetime] = None


# ===========================================
# BADGE MODELS
# ===========================================

class Badge(BaseModel):
    """Badge model"""
    id: str
    name: str
    description: str
    icon: str
    color: str = "#4F46E5"
    badge_type: BadgeType
    requirements: Optional[Dict[str, Any]] = None
    is_rare: bool = False
    sort_order: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserBadge(BaseModel):
    """User's earned badge"""
    id: str
    user_id: str
    badge_id: str
    badge: Optional[Badge] = None
    earned_at: datetime = Field(default_factory=datetime.utcnow)
    is_featured: bool = False  # Display prominently on profile


# ===========================================
# STREAK MODELS
# ===========================================

class Streak(BaseModel):
    """User streak tracking"""
    id: str
    user_id: str
    streak_type: StreakType
    current_count: int = 0
    best_count: int = 0
    last_activity_date: Optional[date] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class StreakBonus(BaseModel):
    """Streak bonus configuration"""
    streak_type: StreakType
    milestone: int  # e.g., 7 days, 30 days
    pc_bonus: int = 0
    pcon_bonus: int = 0
    badge_reward: Optional[str] = None
    achievement_reward: Optional[str] = None


# ===========================================
# LEADERBOARD MODELS
# ===========================================

class LeaderboardType(str, Enum):
    """Leaderboard types"""
    WEEKLY_PC = "weekly_pc"
    WEEKLY_PCON = "weekly_pcon"
    MONTHLY_PC = "monthly_pc"
    MONTHLY_PCON = "monthly_pcon"
    ALL_TIME_PC = "all_time_pc"
    ALL_TIME_PCON = "all_time_pcon"
    QUESTIONS_ANSWERED = "questions_answered"
    BEST_ANSWERS = "best_answers"
    COMMUNITY_HELPER = "community_helper"


class LeaderboardEntry(BaseModel):
    """Leaderboard entry"""
    position: int
    user_id: str
    username: str
    avatar_url: Optional[str] = None
    score: int
    rank: Optional[str] = None
    badges: List[str] = []
    change_from_last: Optional[int] = None  # Position change


class Leaderboard(BaseModel):
    """Leaderboard model"""
    leaderboard_type: LeaderboardType
    entries: List[LeaderboardEntry]
    period_start: datetime
    period_end: datetime
    last_updated: datetime = Field(default_factory=datetime.utcnow)


# ===========================================
# SOCIAL GAMIFICATION MODELS
# ===========================================

class FollowReward(BaseModel):
    """Reward for following/being followed"""
    user_id: str
    follower_id: str
    pc_points: int = 1
    pcon_points: int = 1
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ReferralReward(BaseModel):
    """Referral system reward"""
    referrer_id: str
    referred_id: str
    milestone: Literal["signup", "first_question", "first_answer", "active_user"]
    pc_reward: int
    pcon_reward: int
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ===========================================
# ADVANCED STATISTICS MODELS
# ===========================================

class GamificationStats(BaseModel):
    """Comprehensive gamification statistics"""
    total_pc_distributed: int = 0
    total_pcon_distributed: int = 0
    total_achievements_earned: int = 0
    total_badges_earned: int = 0
    active_streaks: int = 0
    total_referrals: int = 0
    leaderboard_participants: int = 0


class UserGamificationProfile(BaseModel):
    """Complete user gamification profile"""
    user_id: str
    username: str
    pc_points: int = 0
    pcon_points: int = 0
    rank: str = "Iniciante"
    level: int = 1
    achievements: List[UserAchievement] = []
    badges: List[UserBadge] = []
    streaks: List[Streak] = []
    leaderboard_positions: Dict[str, int] = {}
    total_achievements: int = 0
    total_badges: int = 0
    joined_at: datetime = Field(default_factory=datetime.utcnow)


# ===========================================
# REQUEST/RESPONSE MODELS
# ===========================================

class AchievementResponse(BaseModel):
    """Achievement response"""
    achievement: Achievement
    progress: Optional[AchievementProgress] = None
    is_earned: bool = False


class BadgeResponse(BaseModel):
    """Badge response"""
    badge: Badge
    earned_at: Optional[datetime] = None


class StreakResponse(BaseModel):
    """Streak response"""
    streak: Streak
    bonus_earned: Optional[StreakBonus] = None
    next_milestone: Optional[int] = None


class LeaderboardResponse(BaseModel):
    """Leaderboard response"""
    leaderboard: Leaderboard
    user_position: Optional[int] = None
    user_entry: Optional[LeaderboardEntry] = None


class GamificationDashboard(BaseModel):
    """Complete gamification dashboard"""
    user_profile: UserGamificationProfile
    recent_achievements: List[UserAchievement] = []
    active_streaks: List[Streak] = []
    leaderboard_positions: List[LeaderboardEntry] = []
    suggested_goals: List[Achievement] = []
    stats: GamificationStats


# ===========================================
# FILTERS AND SEARCH
# ===========================================

class AchievementFilters(BaseModel):
    """Achievement filtering options"""
    category: Optional[AchievementCategory] = None
    rarity: Optional[AchievementRarity] = None
    is_earned: Optional[bool] = None
    is_hidden: Optional[bool] = None
    search: Optional[str] = None


class BadgeFilters(BaseModel):
    """Badge filtering options"""
    badge_type: Optional[BadgeType] = None
    is_earned: Optional[bool] = None
    is_featured: Optional[bool] = None
    search: Optional[str] = None