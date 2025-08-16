"""
Admin Gamification Router
Comprehensive admin panel for gamification management and analytics
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse

from ..core.security import get_current_admin_user
from ..models.user import User
from ..models.base import MessageResponse
from ..models.gamification import (
    Achievement, UserAchievement, Badge, UserBadge, Streak,
    LeaderboardType, GamificationStats, AchievementCategory,
    AchievementRarity, BadgeType, StreakType
)
from ..services.advanced_gamification_service import advanced_gamification_service
from ..services.gamification_service import gamification_service

router = APIRouter()

# ===========================================
# SYSTEM MANAGEMENT
# ===========================================

@router.post("/initialize", response_model=MessageResponse)
async def initialize_gamification_system(
    current_user: User = Depends(get_current_admin_user)
):
    """Initialize the complete gamification system"""
    try:
        # Initialize achievements
        await advanced_gamification_service.initialize_achievements()
        
        # Initialize badges
        await advanced_gamification_service.initialize_badges()
        
        # Generate all leaderboards
        leaderboard_results = []
        for leaderboard_type in LeaderboardType:
            try:
                await advanced_gamification_service.generate_leaderboard(leaderboard_type, 100)
                leaderboard_results.append(f"✅ {leaderboard_type.value}")
            except Exception as e:
                leaderboard_results.append(f"❌ {leaderboard_type.value}: {str(e)}")
        
        return MessageResponse(
            message=f"Gamification system initialized. Leaderboards: {', '.join(leaderboard_results)}"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize gamification system: {str(e)}"
        )


@router.get("/health", response_model=Dict[str, Any])
async def gamification_health_check(
    current_user: User = Depends(get_current_admin_user)
):
    """Comprehensive health check for gamification system"""
    try:
        health_data = {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc),
            "components": {
                "achievements": {"status": "ok", "count": 0},
                "badges": {"status": "ok", "count": 0},
                "streaks": {"status": "ok", "active": 0},
                "leaderboards": {"status": "ok", "generated": 0},
                "referrals": {"status": "ok", "count": 0}
            },
            "statistics": await gamification_service.get_gamification_stats()
        }
        
        # Check achievements count
        achievements_count = await advanced_gamification_service.user_achievements_collection.count_documents({})
        health_data["components"]["achievements"]["count"] = achievements_count
        
        # Check badges count
        badges_count = await advanced_gamification_service.badges_collection.count_documents({})
        health_data["components"]["badges"]["count"] = badges_count
        
        # Check active streaks
        active_streaks = await advanced_gamification_service.streaks_collection.count_documents({"is_active": True})
        health_data["components"]["streaks"]["active"] = active_streaks
        
        # Check leaderboards
        leaderboards_count = await advanced_gamification_service.leaderboards_collection.count_documents({})
        health_data["components"]["leaderboards"]["generated"] = leaderboards_count
        
        # Check referrals
        referrals_count = await advanced_gamification_service.referrals_collection.count_documents({})
        health_data["components"]["referrals"]["count"] = referrals_count
        
        return health_data
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now(timezone.utc),
            "error": str(e)
        }

# ===========================================
# USER MANAGEMENT
# ===========================================

@router.get("/users/{user_id}/profile", response_model=Dict[str, Any])
async def get_user_gamification_admin(
    user_id: str,
    current_user: User = Depends(get_current_admin_user)
):
    """Get comprehensive gamification profile for a user (Admin view)"""
    try:
        # Get user basic data
        user = await advanced_gamification_service.users_collection.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get user statistics
        user_stats = await advanced_gamification_service._get_user_statistics(user_id)
        
        # Get user achievements
        user_achievements = await advanced_gamification_service.user_achievements_collection.find({
            "user_id": user_id,
            "is_earned": True
        }).to_list(length=None)
        
        # Get user badges
        user_badges = await advanced_gamification_service.get_user_badges(user_id)
        
        # Get user streaks
        user_streaks = await advanced_gamification_service.get_user_streaks(user_id)
        
        # Get points history
        points_history = await gamification_service.get_user_points_history(user_id, 20)
        
        return {
            "user_id": user_id,
            "username": user.get("username", "Unknown"),
            "email": user.get("email", ""),
            "rank": user.get("rank", "Iniciante"),
            "pc_points": user.get("pc_points", 0),
            "pcon_points": user.get("pcon_points", 0),
            "created_at": user.get("created_at"),
            "statistics": user_stats,
            "achievements": user_achievements,
            "badges": [badge.model_dump() for badge in user_badges],
            "streaks": [streak.model_dump() for streak in user_streaks],
            "recent_points_history": points_history
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user profile: {str(e)}"
        )


@router.post("/users/{user_id}/points/award", response_model=Dict[str, Any])
async def award_points_to_user(
    user_id: str,
    pc_points: int = 0,
    pcon_points: int = 0,
    reason: str = "admin_manual_award",
    current_user: User = Depends(get_current_admin_user)
):
    """Manually award points to a user"""
    try:
        # Custom points award
        result = await gamification_service.award_points(
            user_id,
            reason,
            target_id="admin_manual",
            target_type="admin_action"
        )
        
        return {
            "message": f"Points awarded successfully",
            "user_id": user_id,
            "pc_points_awarded": pc_points,
            "pcon_points_awarded": pcon_points,
            "reason": reason,
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to award points: {str(e)}"
        )


@router.post("/users/{user_id}/badges/{badge_id}/award", response_model=UserBadge)
async def award_badge_to_user(
    user_id: str,
    badge_id: str,
    is_featured: bool = False,
    current_user: User = Depends(get_current_admin_user)
):
    """Award a badge to a specific user"""
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


@router.post("/users/{user_id}/achievements/check", response_model=List[UserAchievement])
async def check_user_achievements(
    user_id: str,
    current_user: User = Depends(get_current_admin_user)
):
    """Manually trigger achievement checking for a specific user"""
    try:
        new_achievements = await advanced_gamification_service.check_advanced_achievements(user_id)
        return new_achievements
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check achievements: {str(e)}"
        )

# ===========================================
# ANALYTICS AND REPORTS
# ===========================================

@router.get("/analytics/overview", response_model=Dict[str, Any])
async def get_gamification_overview(
    current_user: User = Depends(get_current_admin_user)
):
    """Get comprehensive gamification analytics overview"""
    try:
        # Basic gamification stats
        basic_stats = await gamification_service.get_gamification_stats()
        
        # Achievement statistics
        total_achievements = await advanced_gamification_service.user_achievements_collection.count_documents({})
        earned_achievements = await advanced_gamification_service.user_achievements_collection.count_documents({
            "is_earned": True
        })
        
        # Achievement breakdown by category
        achievement_pipeline = [
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        achievement_by_category = await advanced_gamification_service.user_achievements_collection.aggregate(
            achievement_pipeline
        ).to_list(length=None)
        
        # Badge statistics
        total_badges = await advanced_gamification_service.badges_collection.count_documents({})
        earned_badges = await advanced_gamification_service.user_badges_collection.count_documents({})
        
        # Streak statistics
        active_streaks = await advanced_gamification_service.streaks_collection.count_documents({"is_active": True})
        total_streaks = await advanced_gamification_service.streaks_collection.count_documents({})
        
        # Top streaks
        top_streaks_pipeline = [
            {"$sort": {"current_count": -1}},
            {"$limit": 10},
            {"$lookup": {
                "from": "users",
                "localField": "user_id",
                "foreignField": "id",
                "as": "user"
            }},
            {"$unwind": "$user"},
            {"$project": {
                "user_id": 1,
                "username": "$user.username",
                "streak_type": 1,
                "current_count": 1,
                "best_count": 1
            }}
        ]
        top_streaks = await advanced_gamification_service.streaks_collection.aggregate(
            top_streaks_pipeline
        ).to_list(length=None)
        
        # Recent activity (last 24 hours)
        from datetime import timedelta
        yesterday = datetime.now(timezone.utc) - timedelta(days=1)
        recent_points = await gamification_service.points_history_collection.count_documents({
            "created_at": {"$gte": yesterday}
        })
        
        recent_achievements = await advanced_gamification_service.user_achievements_collection.count_documents({
            "earned_at": {"$gte": yesterday}
        })
        
        return {
            "basic_stats": basic_stats,
            "achievements": {
                "total_available": total_achievements,
                "total_earned": earned_achievements,
                "earn_rate": (earned_achievements / max(total_achievements, 1)) * 100,
                "by_category": achievement_by_category
            },
            "badges": {
                "total_available": total_badges,
                "total_earned": earned_badges
            },
            "streaks": {
                "total": total_streaks,
                "active": active_streaks,
                "top_streaks": top_streaks
            },
            "recent_activity": {
                "period": "24 hours",
                "points_awarded": recent_points,
                "achievements_earned": recent_achievements
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analytics overview: {str(e)}"
        )


@router.get("/analytics/leaderboards", response_model=Dict[str, Any])
async def get_leaderboards_analytics(
    current_user: User = Depends(get_current_admin_user)
):
    """Get analytics for all leaderboards"""
    try:
        leaderboards_data = {}
        
        for leaderboard_type in LeaderboardType:
            try:
                # Get leaderboard
                leaderboard = await advanced_gamification_service.leaderboards_collection.find_one({
                    "leaderboard_type": leaderboard_type.value
                })
                
                if leaderboard:
                    entries_count = len(leaderboard.get("entries", []))
                    last_updated = leaderboard.get("last_updated")
                    
                    leaderboards_data[leaderboard_type.value] = {
                        "entries_count": entries_count,
                        "last_updated": last_updated,
                        "status": "generated"
                    }
                else:
                    leaderboards_data[leaderboard_type.value] = {
                        "entries_count": 0,
                        "last_updated": None,
                        "status": "not_generated"
                    }
                    
            except Exception as e:
                leaderboards_data[leaderboard_type.value] = {
                    "entries_count": 0,
                    "last_updated": None,
                    "status": f"error: {str(e)}"
                }
        
        return {
            "leaderboards": leaderboards_data,
            "total_types": len(LeaderboardType),
            "generated_count": len([lb for lb in leaderboards_data.values() if lb["status"] == "generated"])
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get leaderboards analytics: {str(e)}"
        )

# ===========================================
# CONFIGURATION MANAGEMENT
# ===========================================

@router.get("/config/achievements", response_model=List[Achievement])
async def get_all_achievements_config(
    current_user: User = Depends(get_current_admin_user)
):
    """Get all achievement configurations"""
    try:
        achievements = await advanced_gamification_service.user_achievements_collection.find({}).to_list(length=None)
        return [Achievement(**achievement) for achievement in achievements]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get achievements config: {str(e)}"
        )


@router.get("/config/badges", response_model=List[Badge])
async def get_all_badges_config(
    current_user: User = Depends(get_current_admin_user)
):
    """Get all badge configurations"""
    try:
        badges = await advanced_gamification_service.badges_collection.find({}).to_list(length=None)
        return [Badge(**badge) for badge in badges]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get badges config: {str(e)}"
        )

# ===========================================
# BULK OPERATIONS
# ===========================================

@router.post("/bulk/achievements/check-all", response_model=MessageResponse)
async def check_all_users_achievements(
    limit: int = Query(100, le=1000, description="Number of users to process"),
    current_user: User = Depends(get_current_admin_user)
):
    """Check achievements for all users (bulk operation)"""
    try:
        # Get users
        users = await advanced_gamification_service.users_collection.find({}).limit(limit).to_list(length=None)
        
        processed = 0
        errors = 0
        
        for user in users:
            try:
                await advanced_gamification_service.check_advanced_achievements(user["id"])
                processed += 1
            except Exception as e:
                errors += 1
                continue
        
        return MessageResponse(
            message=f"Processed {processed} users, {errors} errors"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check achievements for all users: {str(e)}"
        )


@router.post("/bulk/leaderboards/generate-all", response_model=MessageResponse)
async def generate_all_leaderboards(
    current_user: User = Depends(get_current_admin_user)
):
    """Generate all leaderboards (bulk operation)"""
    try:
        results = []
        
        for leaderboard_type in LeaderboardType:
            try:
                await advanced_gamification_service.generate_leaderboard(leaderboard_type, 100)
                results.append(f"✅ {leaderboard_type.value}")
            except Exception as e:
                results.append(f"❌ {leaderboard_type.value}: {str(e)}")
        
        return MessageResponse(
            message=f"Leaderboard generation completed: {', '.join(results)}"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate all leaderboards: {str(e)}"
        )

# ===========================================
# MAINTENANCE
# ===========================================

@router.delete("/maintenance/inactive-streaks", response_model=MessageResponse)
async def cleanup_inactive_streaks(
    days_threshold: int = Query(30, description="Days of inactivity to consider for cleanup"),
    current_user: User = Depends(get_current_admin_user)
):
    """Clean up inactive streaks"""
    try:
        from datetime import timedelta
        
        threshold_date = datetime.now(timezone.utc) - timedelta(days=days_threshold)
        
        # Mark old streaks as inactive
        result = await advanced_gamification_service.streaks_collection.update_many(
            {
                "last_activity_date": {"$lt": threshold_date.date()},
                "is_active": True
            },
            {
                "$set": {
                    "is_active": False,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        return MessageResponse(
            message=f"Marked {result.modified_count} streaks as inactive"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cleanup inactive streaks: {str(e)}"
        )