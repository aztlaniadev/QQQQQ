"""
Advanced Gamification Router
Endpoints for achievements, badges, streaks, leaderboards, and gamification dashboard
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse

from ..core.security import get_current_user, get_current_admin_user
from ..models.user import User
from ..models.base import BaseResponse, MessageResponse
from ..models.gamification import (
    Achievement, UserAchievement, AchievementProgress, AchievementFilters,
    Badge, UserBadge, BadgeFilters, Streak, StreakType,
    LeaderboardType, Leaderboard, LeaderboardResponse,
    GamificationDashboard, UserGamificationProfile,
    ReferralReward, AchievementCategory, AchievementRarity, BadgeType
)
from ..services.advanced_gamification_service import advanced_gamification_service

router = APIRouter()

# ===========================================
# ACHIEVEMENTS ENDPOINTS
# ===========================================

@router.get("/achievements", response_model=List[AchievementProgress])
async def get_user_achievements(
    category: Optional[AchievementCategory] = Query(None, description="Filter by achievement category"),
    rarity: Optional[AchievementRarity] = Query(None, description="Filter by achievement rarity"),
    is_earned: Optional[bool] = Query(None, description="Filter by earned status"),
    search: Optional[str] = Query(None, description="Search achievements by name or description"),
    current_user: User = Depends(get_current_user)
):
    """Get user's achievement progress with optional filtering"""
    try:
        filters = AchievementFilters(
            category=category,
            rarity=rarity,
            is_earned=is_earned,
            search=search
        )
        
        achievements = await advanced_gamification_service.get_user_achievement_progress(
            current_user.id, 
            filters
        )
        
        return achievements
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get achievements: {str(e)}"
        )


@router.post("/achievements/check", response_model=List[UserAchievement])
async def check_achievements(
    current_user: User = Depends(get_current_user)
):
    """Manually trigger achievement checking for the current user"""
    try:
        new_achievements = await advanced_gamification_service.check_advanced_achievements(
            current_user.id
        )
        
        return new_achievements
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check achievements: {str(e)}"
        )


@router.post("/admin/achievements/initialize", response_model=MessageResponse)
async def initialize_achievements(
    current_user: User = Depends(get_current_admin_user)
):
    """Initialize predefined achievements (Admin only)"""
    try:
        await advanced_gamification_service.initialize_achievements()
        
        return MessageResponse(message="Achievements initialized successfully")
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize achievements: {str(e)}"
        )

# ===========================================
# BADGES ENDPOINTS
# ===========================================

@router.get("/badges", response_model=List[UserBadge])
async def get_user_badges(
    badge_type: Optional[BadgeType] = Query(None, description="Filter by badge type"),
    is_featured: Optional[bool] = Query(None, description="Filter by featured status"),
    search: Optional[str] = Query(None, description="Search badges by name or description"),
    current_user: User = Depends(get_current_user)
):
    """Get user's badges with optional filtering"""
    try:
        filters = BadgeFilters(
            badge_type=badge_type,
            is_featured=is_featured,
            search=search
        )
        
        badges = await advanced_gamification_service.get_user_badges(
            current_user.id,
            filters
        )
        
        return badges
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get badges: {str(e)}"
        )


@router.post("/badges/{badge_id}/award", response_model=UserBadge)
async def award_badge(
    badge_id: str,
    user_id: str,
    is_featured: bool = False,
    current_user: User = Depends(get_current_admin_user)
):
    """Award a badge to a user (Admin only)"""
    try:
        user_badge = await advanced_gamification_service.award_badge(
            user_id,
            badge_id,
            is_featured
        )
        
        return user_badge
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to award badge: {str(e)}"
        )


@router.post("/admin/badges/initialize", response_model=MessageResponse)
async def initialize_badges(
    current_user: User = Depends(get_current_admin_user)
):
    """Initialize predefined badges (Admin only)"""
    try:
        await advanced_gamification_service.initialize_badges()
        
        return MessageResponse(message="Badges initialized successfully")
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize badges: {str(e)}"
        )

# ===========================================
# STREAKS ENDPOINTS
# ===========================================

@router.get("/streaks", response_model=List[Streak])
async def get_user_streaks(
    current_user: User = Depends(get_current_user)
):
    """Get user's current streaks"""
    try:
        streaks = await advanced_gamification_service.get_user_streaks(current_user.id)
        return streaks
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get streaks: {str(e)}"
        )


@router.post("/streaks/{streak_type}/update", response_model=Streak)
async def update_streak(
    streak_type: StreakType,
    current_user: User = Depends(get_current_user)
):
    """Update user's streak for a specific type"""
    try:
        streak = await advanced_gamification_service.update_streak(
            current_user.id,
            streak_type
        )
        
        return streak
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update streak: {str(e)}"
        )

# ===========================================
# LEADERBOARDS ENDPOINTS
# ===========================================

@router.get("/leaderboards/{leaderboard_type}", response_model=LeaderboardResponse)
async def get_leaderboard(
    leaderboard_type: LeaderboardType,
    limit: int = Query(100, le=100, ge=10, description="Number of entries to return"),
    current_user: User = Depends(get_current_user)
):
    """Get leaderboard for specific type"""
    try:
        # Generate fresh leaderboard
        leaderboard = await advanced_gamification_service.generate_leaderboard(
            leaderboard_type,
            limit
        )
        
        # Get user's position in this leaderboard
        user_position = await advanced_gamification_service.get_user_leaderboard_position(
            current_user.id,
            leaderboard_type
        )
        
        # Find user's entry
        user_entry = None
        if user_position:
            for entry in leaderboard.entries:
                if entry.user_id == current_user.id:
                    user_entry = entry
                    break
        
        response = LeaderboardResponse(
            leaderboard=leaderboard,
            user_position=user_position,
            user_entry=user_entry
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get leaderboard: {str(e)}"
        )


@router.post("/leaderboards/{leaderboard_type}/generate", response_model=Leaderboard)
async def generate_leaderboard(
    leaderboard_type: LeaderboardType,
    limit: int = Query(100, le=100, ge=10, description="Number of entries to return"),
    current_user: User = Depends(get_current_admin_user)
):
    """Generate/refresh leaderboard (Admin only)"""
    try:
        leaderboard = await advanced_gamification_service.generate_leaderboard(
            leaderboard_type,
            limit
        )
        
        return leaderboard
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate leaderboard: {str(e)}"
        )


@router.get("/leaderboards", response_model=List[str])
async def get_available_leaderboards():
    """Get list of available leaderboard types"""
    return [lb_type.value for lb_type in LeaderboardType]

# ===========================================
# DASHBOARD ENDPOINT
# ===========================================

@router.get("/dashboard", response_model=GamificationDashboard)
async def get_gamification_dashboard(
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive gamification dashboard for the current user"""
    try:
        dashboard = await advanced_gamification_service.get_gamification_dashboard(
            current_user.id
        )
        
        return dashboard
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get gamification dashboard: {str(e)}"
        )


@router.get("/profile/{user_id}", response_model=UserGamificationProfile)
async def get_user_gamification_profile(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get gamification profile for a specific user"""
    try:
        dashboard = await advanced_gamification_service.get_gamification_dashboard(user_id)
        return dashboard.user_profile
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user gamification profile: {str(e)}"
        )

# ===========================================
# REFERRAL SYSTEM ENDPOINTS
# ===========================================

@router.post("/referrals/create", response_model=ReferralReward)
async def create_referral(
    referred_user_id: str,
    current_user: User = Depends(get_current_user)
):
    """Create a referral for a new user"""
    try:
        referral = await advanced_gamification_service.create_referral(
            current_user.id,
            referred_user_id
        )
        
        return referral
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create referral: {str(e)}"
        )


@router.post("/referrals/milestone", response_model=MessageResponse)
async def check_referral_milestone(
    milestone: str,
    current_user: User = Depends(get_current_user)
):
    """Check and award referral milestone for the current user"""
    try:
        await advanced_gamification_service.check_referral_milestones(
            current_user.id,
            milestone
        )
        
        return MessageResponse(message="Referral milestone checked successfully")
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check referral milestone: {str(e)}"
        )

# ===========================================
# STATISTICS AND ANALYTICS
# ===========================================

@router.get("/stats/categories", response_model=List[str])
async def get_achievement_categories():
    """Get list of available achievement categories"""
    return [category.value for category in AchievementCategory]


@router.get("/stats/rarities", response_model=List[str])
async def get_achievement_rarities():
    """Get list of available achievement rarities"""
    return [rarity.value for rarity in AchievementRarity]


@router.get("/stats/badge-types", response_model=List[str])
async def get_badge_types():
    """Get list of available badge types"""
    return [badge_type.value for badge_type in BadgeType]


@router.get("/stats/streak-types", response_model=List[str])
async def get_streak_types():
    """Get list of available streak types"""
    return [streak_type.value for streak_type in StreakType]

# ===========================================
# ADMIN MANAGEMENT ENDPOINTS
# ===========================================

@router.post("/admin/initialize-all", response_model=MessageResponse)
async def initialize_all_gamification(
    current_user: User = Depends(get_current_admin_user)
):
    """Initialize all gamification components (Admin only)"""
    try:
        # Initialize achievements
        await advanced_gamification_service.initialize_achievements()
        
        # Initialize badges
        await advanced_gamification_service.initialize_badges()
        
        # Generate initial leaderboards
        for leaderboard_type in LeaderboardType:
            try:
                await advanced_gamification_service.generate_leaderboard(leaderboard_type, 100)
            except Exception as e:
                # Log error but continue with other leaderboards
                print(f"Failed to generate {leaderboard_type}: {str(e)}")
        
        return MessageResponse(
            message="All gamification components initialized successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize gamification: {str(e)}"
        )


@router.get("/admin/health", response_model=dict)
async def gamification_health_check(
    current_user: User = Depends(get_current_admin_user)
):
    """Health check for gamification system (Admin only)"""
    try:
        # Check various components
        health_status = {
            "status": "healthy",
            "components": {
                "achievements": "ok",
                "badges": "ok", 
                "streaks": "ok",
                "leaderboards": "ok",
                "referrals": "ok"
            }
        }
        
        # Could add more detailed health checks here
        # For example, checking if collections exist, indexes are created, etc.
        
        return health_status
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }