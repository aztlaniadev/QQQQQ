"""
Comprehensive tests for advanced gamification system
Tests achievements, badges, streaks, leaderboards, and admin functionality
"""

import pytest
import pytest_asyncio
from datetime import datetime, timezone, date, timedelta
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch

from ..app.main import app
from ..app.models.gamification import (
    AchievementCategory, AchievementRarity, BadgeType, StreakType, LeaderboardType
)


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_admin_user():
    return {
        "id": "admin123",
        "username": "admin",
        "email": "admin@example.com",
        "is_admin": True,
        "is_active": True
    }


@pytest.fixture
def mock_regular_user():
    return {
        "id": "user123",
        "username": "testuser",
        "email": "user@example.com",
        "is_admin": False,
        "is_active": True,
        "pc_points": 100,
        "pcon_points": 50,
        "rank": "Colaborador",
        "created_at": datetime.now(timezone.utc)
    }


@pytest.fixture
def mock_achievement():
    return {
        "id": "test_achievement",
        "name": "Test Achievement",
        "description": "A test achievement",
        "category": AchievementCategory.BEGINNER,
        "rarity": AchievementRarity.COMMON,
        "badge_icon": "🏆",
        "badge_color": "#FFD700",
        "criteria": {
            "condition_type": "count",
            "target_value": 5,
            "target_field": "questions_created"
        },
        "points_reward": 10,
        "pcon_reward": 5,
        "sort_order": 1,
        "created_at": datetime.now(timezone.utc)
    }


@pytest.fixture
def mock_badge():
    return {
        "id": "test_badge",
        "name": "Test Badge",
        "description": "A test badge",
        "icon": "🎯",
        "color": "#4F46E5",
        "badge_type": BadgeType.ACHIEVEMENT,
        "requirements": {"pc_points": 100},
        "sort_order": 1,
        "created_at": datetime.now(timezone.utc)
    }


@pytest.fixture
def mock_streak():
    return {
        "id": "test_streak",
        "user_id": "user123",
        "streak_type": StreakType.DAILY_LOGIN,
        "current_count": 5,
        "best_count": 10,
        "last_activity_date": date.today(),
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }


class TestAdvancedAchievements:
    """Test advanced achievement system"""

    @patch('app.core.security.get_current_user')
    @patch('app.services.advanced_gamification_service.advanced_gamification_service.get_user_achievement_progress')
    async def test_get_user_achievements(self, mock_progress, mock_auth, client, mock_regular_user):
        """Test getting user achievements with filtering"""
        mock_auth.return_value = mock_regular_user
        mock_progress.return_value = []
        
        response = await client.get(
            "/api/v1/gamification/achievements",
            params={
                "category": "beginner",
                "rarity": "common",
                "is_earned": False
            }
        )
        
        assert response.status_code == 200
        mock_progress.assert_called_once()

    @patch('app.core.security.get_current_user')
    @patch('app.services.advanced_gamification_service.advanced_gamification_service.check_advanced_achievements')
    async def test_check_achievements(self, mock_check, mock_auth, client, mock_regular_user):
        """Test manually triggering achievement check"""
        mock_auth.return_value = mock_regular_user
        mock_check.return_value = []
        
        response = await client.post("/api/v1/gamification/achievements/check")
        
        assert response.status_code == 200
        mock_check.assert_called_once_with(mock_regular_user["id"])

    @patch('app.core.security.get_current_admin_user')
    @patch('app.services.advanced_gamification_service.advanced_gamification_service.initialize_achievements')
    async def test_initialize_achievements_admin(self, mock_init, mock_auth, client, mock_admin_user):
        """Test initializing achievements (admin only)"""
        mock_auth.return_value = mock_admin_user
        mock_init.return_value = None
        
        response = await client.post("/api/v1/gamification/admin/achievements/initialize")
        
        assert response.status_code == 200
        mock_init.assert_called_once()


class TestBadgeSystem:
    """Test badge system functionality"""

    @patch('app.core.security.get_current_user')
    @patch('app.services.advanced_gamification_service.advanced_gamification_service.get_user_badges')
    async def test_get_user_badges(self, mock_badges, mock_auth, client, mock_regular_user):
        """Test getting user badges with filtering"""
        mock_auth.return_value = mock_regular_user
        mock_badges.return_value = []
        
        response = await client.get(
            "/api/v1/gamification/badges",
            params={
                "badge_type": "achievement",
                "is_featured": True
            }
        )
        
        assert response.status_code == 200
        mock_badges.assert_called_once()

    @patch('app.core.security.get_current_admin_user')
    @patch('app.services.advanced_gamification_service.advanced_gamification_service.award_badge')
    async def test_award_badge_admin(self, mock_award, mock_auth, client, mock_admin_user, mock_badge):
        """Test awarding badge to user (admin only)"""
        mock_auth.return_value = mock_admin_user
        mock_award.return_value = mock_badge
        
        response = await client.post(
            "/api/v1/gamification/badges/test_badge/award",
            params={
                "user_id": "user123",
                "is_featured": True
            }
        )
        
        assert response.status_code == 200
        mock_award.assert_called_once_with("user123", "test_badge", True)

    @patch('app.core.security.get_current_admin_user')
    @patch('app.services.advanced_gamification_service.advanced_gamification_service.initialize_badges')
    async def test_initialize_badges_admin(self, mock_init, mock_auth, client, mock_admin_user):
        """Test initializing badges (admin only)"""
        mock_auth.return_value = mock_admin_user
        mock_init.return_value = None
        
        response = await client.post("/api/v1/gamification/admin/badges/initialize")
        
        assert response.status_code == 200
        mock_init.assert_called_once()


class TestStreakSystem:
    """Test streak system functionality"""

    @patch('app.core.security.get_current_user')
    @patch('app.services.advanced_gamification_service.advanced_gamification_service.get_user_streaks')
    async def test_get_user_streaks(self, mock_streaks, mock_auth, client, mock_regular_user):
        """Test getting user streaks"""
        mock_auth.return_value = mock_regular_user
        mock_streaks.return_value = []
        
        response = await client.get("/api/v1/gamification/streaks")
        
        assert response.status_code == 200
        mock_streaks.assert_called_once_with(mock_regular_user["id"])

    @patch('app.core.security.get_current_user')
    @patch('app.services.advanced_gamification_service.advanced_gamification_service.update_streak')
    async def test_update_streak(self, mock_update, mock_auth, client, mock_regular_user, mock_streak):
        """Test updating user streak"""
        mock_auth.return_value = mock_regular_user
        mock_update.return_value = mock_streak
        
        response = await client.post("/api/v1/gamification/streaks/daily_login/update")
        
        assert response.status_code == 200
        mock_update.assert_called_once_with(mock_regular_user["id"], StreakType.DAILY_LOGIN)


class TestLeaderboards:
    """Test leaderboard functionality"""

    @patch('app.core.security.get_current_user')
    @patch('app.services.advanced_gamification_service.advanced_gamification_service.generate_leaderboard')
    @patch('app.services.advanced_gamification_service.advanced_gamification_service.get_user_leaderboard_position')
    async def test_get_leaderboard(self, mock_position, mock_generate, mock_auth, client, mock_regular_user):
        """Test getting leaderboard"""
        mock_auth.return_value = mock_regular_user
        mock_leaderboard = {
            "leaderboard_type": LeaderboardType.ALL_TIME_PC,
            "entries": [],
            "period_start": datetime.now(timezone.utc),
            "period_end": datetime.now(timezone.utc),
            "last_updated": datetime.now(timezone.utc)
        }
        mock_generate.return_value = mock_leaderboard
        mock_position.return_value = 5
        
        response = await client.get(
            "/api/v1/gamification/leaderboards/all_time_pc",
            params={"limit": 50}
        )
        
        assert response.status_code == 200
        mock_generate.assert_called_once_with(LeaderboardType.ALL_TIME_PC, 50)
        mock_position.assert_called_once_with(mock_regular_user["id"], LeaderboardType.ALL_TIME_PC)

    @patch('app.core.security.get_current_admin_user')
    @patch('app.services.advanced_gamification_service.advanced_gamification_service.generate_leaderboard')
    async def test_generate_leaderboard_admin(self, mock_generate, mock_auth, client, mock_admin_user):
        """Test generating leaderboard (admin only)"""
        mock_auth.return_value = mock_admin_user
        mock_leaderboard = {
            "leaderboard_type": LeaderboardType.WEEKLY_PC,
            "entries": [],
            "period_start": datetime.now(timezone.utc),
            "period_end": datetime.now(timezone.utc),
            "last_updated": datetime.now(timezone.utc)
        }
        mock_generate.return_value = mock_leaderboard
        
        response = await client.post("/api/v1/gamification/leaderboards/weekly_pc/generate")
        
        assert response.status_code == 200
        mock_generate.assert_called_once_with(LeaderboardType.WEEKLY_PC, 100)

    async def test_get_available_leaderboards(self, client):
        """Test getting available leaderboard types"""
        response = await client.get("/api/v1/gamification/leaderboards")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0


class TestGamificationDashboard:
    """Test gamification dashboard functionality"""

    @patch('app.core.security.get_current_user')
    @patch('app.services.advanced_gamification_service.advanced_gamification_service.get_gamification_dashboard')
    async def test_get_gamification_dashboard(self, mock_dashboard, mock_auth, client, mock_regular_user):
        """Test getting comprehensive gamification dashboard"""
        mock_auth.return_value = mock_regular_user
        mock_dashboard_data = {
            "user_profile": {
                "user_id": "user123",
                "username": "testuser",
                "pc_points": 100,
                "pcon_points": 50,
                "rank": "Colaborador",
                "level": 1,
                "achievements": [],
                "badges": [],
                "streaks": [],
                "leaderboard_positions": {},
                "total_achievements": 0,
                "total_badges": 0,
                "joined_at": datetime.now(timezone.utc)
            },
            "recent_achievements": [],
            "active_streaks": [],
            "leaderboard_positions": [],
            "suggested_goals": [],
            "stats": {}
        }
        mock_dashboard.return_value = mock_dashboard_data
        
        response = await client.get("/api/v1/gamification/dashboard")
        
        assert response.status_code == 200
        mock_dashboard.assert_called_once_with(mock_regular_user["id"])

    @patch('app.core.security.get_current_user')
    @patch('app.services.advanced_gamification_service.advanced_gamification_service.get_gamification_dashboard')
    async def test_get_user_gamification_profile(self, mock_dashboard, mock_auth, client, mock_regular_user):
        """Test getting user gamification profile"""
        mock_auth.return_value = mock_regular_user
        mock_dashboard_data = {
            "user_profile": {
                "user_id": "user456",
                "username": "otheruser",
                "pc_points": 200,
                "pcon_points": 100,
                "rank": "Especialista",
                "level": 2,
                "achievements": [],
                "badges": [],
                "streaks": [],
                "leaderboard_positions": {},
                "total_achievements": 5,
                "total_badges": 3,
                "joined_at": datetime.now(timezone.utc)
            }
        }
        mock_dashboard.return_value = mock_dashboard_data
        
        response = await client.get("/api/v1/gamification/profile/user456")
        
        assert response.status_code == 200
        mock_dashboard.assert_called_once_with("user456")


class TestReferralSystem:
    """Test referral system functionality"""

    @patch('app.core.security.get_current_user')
    @patch('app.services.advanced_gamification_service.advanced_gamification_service.create_referral')
    async def test_create_referral(self, mock_create, mock_auth, client, mock_regular_user):
        """Test creating a referral"""
        mock_auth.return_value = mock_regular_user
        mock_referral = {
            "referrer_id": "user123",
            "referred_id": "user456",
            "milestone": "signup",
            "pc_reward": 10,
            "pcon_reward": 5,
            "created_at": datetime.now(timezone.utc)
        }
        mock_create.return_value = mock_referral
        
        response = await client.post(
            "/api/v1/gamification/referrals/create",
            params={"referred_user_id": "user456"}
        )
        
        assert response.status_code == 200
        mock_create.assert_called_once_with(mock_regular_user["id"], "user456")

    @patch('app.core.security.get_current_user')
    @patch('app.services.advanced_gamification_service.advanced_gamification_service.check_referral_milestones')
    async def test_check_referral_milestone(self, mock_check, mock_auth, client, mock_regular_user):
        """Test checking referral milestone"""
        mock_auth.return_value = mock_regular_user
        mock_check.return_value = None
        
        response = await client.post(
            "/api/v1/gamification/referrals/milestone",
            params={"milestone": "first_question"}
        )
        
        assert response.status_code == 200
        mock_check.assert_called_once_with(mock_regular_user["id"], "first_question")


class TestStatistics:
    """Test statistics and analytics endpoints"""

    async def test_get_achievement_categories(self, client):
        """Test getting achievement categories"""
        response = await client.get("/api/v1/gamification/stats/categories")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert "beginner" in data

    async def test_get_achievement_rarities(self, client):
        """Test getting achievement rarities"""
        response = await client.get("/api/v1/gamification/stats/rarities")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert "common" in data

    async def test_get_badge_types(self, client):
        """Test getting badge types"""
        response = await client.get("/api/v1/gamification/stats/badge-types")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert "achievement" in data

    async def test_get_streak_types(self, client):
        """Test getting streak types"""
        response = await client.get("/api/v1/gamification/stats/streak-types")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert "daily_login" in data


class TestAdminGamification:
    """Test admin gamification management"""

    @patch('app.core.security.get_current_admin_user')
    @patch('app.services.advanced_gamification_service.advanced_gamification_service.initialize_achievements')
    @patch('app.services.advanced_gamification_service.advanced_gamification_service.initialize_badges')
    async def test_initialize_gamification_system(self, mock_init_badges, mock_init_achievements, mock_auth, client, mock_admin_user):
        """Test initializing complete gamification system"""
        mock_auth.return_value = mock_admin_user
        mock_init_achievements.return_value = None
        mock_init_badges.return_value = None
        
        response = await client.post("/api/v1/admin/gamification/initialize")
        
        assert response.status_code == 200
        mock_init_achievements.assert_called_once()
        mock_init_badges.assert_called_once()

    @patch('app.core.security.get_current_admin_user')
    async def test_gamification_health_check(self, mock_auth, client, mock_admin_user):
        """Test gamification health check"""
        mock_auth.return_value = mock_admin_user
        
        with patch.multiple(
            'app.services.advanced_gamification_service.advanced_gamification_service',
            user_achievements_collection=AsyncMock(),
            badges_collection=AsyncMock(),
            streaks_collection=AsyncMock(),
            leaderboards_collection=AsyncMock(),
            referrals_collection=AsyncMock()
        ):
            response = await client.get("/api/v1/admin/gamification/health")
            assert response.status_code == 200

    @patch('app.core.security.get_current_admin_user')
    @patch('app.services.advanced_gamification_service.advanced_gamification_service.users_collection')
    async def test_get_user_gamification_admin(self, mock_users, mock_auth, client, mock_admin_user, mock_regular_user):
        """Test getting user gamification profile (admin view)"""
        mock_auth.return_value = mock_admin_user
        mock_users.find_one.return_value = mock_regular_user
        
        with patch.multiple(
            'app.services.advanced_gamification_service.advanced_gamification_service',
            _get_user_statistics=AsyncMock(return_value={}),
            user_achievements_collection=AsyncMock(),
            get_user_badges=AsyncMock(return_value=[]),
            get_user_streaks=AsyncMock(return_value=[])
        ), patch('app.services.gamification_service.gamification_service.get_user_points_history', return_value=[]):
            response = await client.get("/api/v1/admin/gamification/users/user123/profile")
            assert response.status_code == 200

    @patch('app.core.security.get_current_admin_user')
    @patch('app.services.gamification_service.gamification_service.award_points')
    async def test_award_points_to_user(self, mock_award, mock_auth, client, mock_admin_user):
        """Test manually awarding points to user"""
        mock_auth.return_value = mock_admin_user
        mock_award.return_value = {"pc_points": 10, "pcon_points": 5}
        
        response = await client.post(
            "/api/v1/admin/gamification/users/user123/points/award",
            params={
                "pc_points": 10,
                "pcon_points": 5,
                "reason": "admin_bonus"
            }
        )
        
        assert response.status_code == 200
        mock_award.assert_called_once()

    @patch('app.core.security.get_current_admin_user')
    @patch('app.services.gamification_service.gamification_service.get_gamification_stats')
    async def test_get_gamification_overview(self, mock_stats, mock_auth, client, mock_admin_user):
        """Test getting gamification analytics overview"""
        mock_auth.return_value = mock_admin_user
        mock_stats.return_value = {}
        
        with patch.multiple(
            'app.services.advanced_gamification_service.advanced_gamification_service',
            user_achievements_collection=AsyncMock(),
            badges_collection=AsyncMock(),
            streaks_collection=AsyncMock()
        ), patch('app.services.gamification_service.gamification_service.points_history_collection', AsyncMock()):
            response = await client.get("/api/v1/admin/gamification/analytics/overview")
            assert response.status_code == 200

    @patch('app.core.security.get_current_admin_user')
    async def test_get_leaderboards_analytics(self, mock_auth, client, mock_admin_user):
        """Test getting leaderboards analytics"""
        mock_auth.return_value = mock_admin_user
        
        with patch('app.services.advanced_gamification_service.advanced_gamification_service.leaderboards_collection', AsyncMock()):
            response = await client.get("/api/v1/admin/gamification/analytics/leaderboards")
            assert response.status_code == 200

    @patch('app.core.security.get_current_admin_user')
    async def test_get_all_achievements_config(self, mock_auth, client, mock_admin_user):
        """Test getting all achievements configuration"""
        mock_auth.return_value = mock_admin_user
        
        with patch('app.services.advanced_gamification_service.advanced_gamification_service.user_achievements_collection', AsyncMock()):
            response = await client.get("/api/v1/admin/gamification/config/achievements")
            assert response.status_code == 200

    @patch('app.core.security.get_current_admin_user')
    async def test_get_all_badges_config(self, mock_auth, client, mock_admin_user):
        """Test getting all badges configuration"""
        mock_auth.return_value = mock_admin_user
        
        with patch('app.services.advanced_gamification_service.advanced_gamification_service.badges_collection', AsyncMock()):
            response = await client.get("/api/v1/admin/gamification/config/badges")
            assert response.status_code == 200

    @patch('app.core.security.get_current_admin_user')
    async def test_check_all_users_achievements(self, mock_auth, client, mock_admin_user):
        """Test bulk checking achievements for all users"""
        mock_auth.return_value = mock_admin_user
        
        with patch.multiple(
            'app.services.advanced_gamification_service.advanced_gamification_service',
            users_collection=AsyncMock(),
            check_advanced_achievements=AsyncMock(return_value=[])
        ):
            response = await client.post(
                "/api/v1/admin/gamification/bulk/achievements/check-all",
                params={"limit": 50}
            )
            assert response.status_code == 200

    @patch('app.core.security.get_current_admin_user')
    @patch('app.services.advanced_gamification_service.advanced_gamification_service.generate_leaderboard')
    async def test_generate_all_leaderboards(self, mock_generate, mock_auth, client, mock_admin_user):
        """Test bulk generating all leaderboards"""
        mock_auth.return_value = mock_admin_user
        mock_generate.return_value = {}
        
        response = await client.post("/api/v1/admin/gamification/bulk/leaderboards/generate-all")
        
        assert response.status_code == 200
        # Should be called for each leaderboard type
        assert mock_generate.call_count == len(LeaderboardType)

    @patch('app.core.security.get_current_admin_user')
    async def test_cleanup_inactive_streaks(self, mock_auth, client, mock_admin_user):
        """Test cleaning up inactive streaks"""
        mock_auth.return_value = mock_admin_user
        
        with patch('app.services.advanced_gamification_service.advanced_gamification_service.streaks_collection', AsyncMock()):
            response = await client.delete(
                "/api/v1/admin/gamification/maintenance/inactive-streaks",
                params={"days_threshold": 30}
            )
            assert response.status_code == 200


class TestGamificationService:
    """Test advanced gamification service methods"""

    @pytest.mark.asyncio
    async def test_calculate_user_level(self):
        """Test user level calculation"""
        from ..app.services.advanced_gamification_service import advanced_gamification_service
        
        # Test level calculation
        assert advanced_gamification_service._calculate_user_level(0) == 1
        assert advanced_gamification_service._calculate_user_level(50) == 1
        assert advanced_gamification_service._calculate_user_level(100) == 1
        assert advanced_gamification_service._calculate_user_level(150) == 2
        assert advanced_gamification_service._calculate_user_level(1000) == 10

    @pytest.mark.asyncio
    async def test_check_achievement_criteria(self):
        """Test achievement criteria checking"""
        from ..app.services.advanced_gamification_service import advanced_gamification_service
        
        user_stats = {
            "questions_created": 5,
            "pc_points": 100,
            "current_daily_login_streak": 7,
            "days_since_registration": 30,
            "followers": 25,
            "following": 25
        }
        
        # Test count criteria
        count_achievement = {
            "criteria": {
                "condition_type": "count",
                "target_value": 5,
                "target_field": "questions_created"
            }
        }
        assert await advanced_gamification_service._check_achievement_criteria(user_stats, count_achievement) == True
        
        # Test points criteria
        points_achievement = {
            "criteria": {
                "condition_type": "points",
                "target_value": 50,
                "target_field": "pc_points"
            }
        }
        assert await advanced_gamification_service._check_achievement_criteria(user_stats, points_achievement) == True
        
        # Test streak criteria
        streak_achievement = {
            "criteria": {
                "condition_type": "streak",
                "target_value": 5,
                "target_field": "daily_login"
            }
        }
        assert await advanced_gamification_service._check_achievement_criteria(user_stats, streak_achievement) == True
        
        # Test special criteria with additional conditions
        special_achievement = {
            "criteria": {
                "condition_type": "special",
                "target_value": 25,
                "additional_conditions": {
                    "followers": 25,
                    "following": 25
                }
            }
        }
        assert await advanced_gamification_service._check_achievement_criteria(user_stats, special_achievement) == True


if __name__ == "__main__":
    pytest.main([__file__])