"""
Advanced Gamification Service
Handles sophisticated gamification features: achievements, badges, streaks, leaderboards
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, date, timedelta
import logging
import calendar

from ..core.database import (
    get_users_collection, get_badges_collection, get_user_badges_collection,
    get_streaks_collection, get_user_achievements_collection, 
    get_leaderboards_collection, get_referrals_collection,
    get_questions_collection, get_answers_collection, get_votes_collection
)
from ..core.config import settings
from ..core.security import generate_unique_id
from ..models.gamification import (
    Achievement, UserAchievement, AchievementProgress, AchievementCriteria,
    Badge, UserBadge, Streak, StreakBonus, LeaderboardType, LeaderboardEntry,
    Leaderboard, UserGamificationProfile, GamificationDashboard,
    AchievementCategory, AchievementRarity, BadgeType, StreakType,
    ReferralReward, AchievementFilters, BadgeFilters
)
from .gamification_service import gamification_service

logger = logging.getLogger(__name__)


class AdvancedGamificationService:
    """Advanced gamification service with sophisticated features"""
    
    def __init__(self):
        # Lazy loading for all collections
        self._users_collection = None
        self._badges_collection = None
        self._user_badges_collection = None
        self._streaks_collection = None
        self._user_achievements_collection = None
        self._leaderboards_collection = None
        self._referrals_collection = None
        self._questions_collection = None
        self._answers_collection = None
        self._votes_collection = None
    
    # Collection properties with lazy loading
    @property
    def users_collection(self):
        if self._users_collection is None:
            self._users_collection = get_users_collection()
        return self._users_collection
    
    @property
    def badges_collection(self):
        if self._badges_collection is None:
            self._badges_collection = get_badges_collection()
        return self._badges_collection
    
    @property
    def user_badges_collection(self):
        if self._user_badges_collection is None:
            self._user_badges_collection = get_user_badges_collection()
        return self._user_badges_collection
    
    @property
    def streaks_collection(self):
        if self._streaks_collection is None:
            self._streaks_collection = get_streaks_collection()
        return self._streaks_collection
    
    @property
    def user_achievements_collection(self):
        if self._user_achievements_collection is None:
            self._user_achievements_collection = get_user_achievements_collection()
        return self._user_achievements_collection
    
    @property
    def leaderboards_collection(self):
        if self._leaderboards_collection is None:
            self._leaderboards_collection = get_leaderboards_collection()
        return self._leaderboards_collection
    
    @property
    def referrals_collection(self):
        if self._referrals_collection is None:
            self._referrals_collection = get_referrals_collection()
        return self._referrals_collection
    
    @property
    def questions_collection(self):
        if self._questions_collection is None:
            self._questions_collection = get_questions_collection()
        return self._questions_collection
    
    @property
    def answers_collection(self):
        if self._answers_collection is None:
            self._answers_collection = get_answers_collection()
        return self._answers_collection
    
    @property
    def votes_collection(self):
        if self._votes_collection is None:
            self._votes_collection = get_votes_collection()
        return self._votes_collection

    # ===========================================
    # ADVANCED ACHIEVEMENTS SYSTEM
    # ===========================================

    async def initialize_achievements(self):
        """Initialize predefined achievements in the database"""
        try:
            achievements = [
                # Beginner achievements
                {
                    "id": "first_question",
                    "name": "Primeira Pergunta",
                    "description": "Faça sua primeira pergunta na comunidade",
                    "category": AchievementCategory.BEGINNER,
                    "rarity": AchievementRarity.COMMON,
                    "badge_icon": "❓",
                    "badge_color": "#10B981",
                    "criteria": {
                        "condition_type": "count",
                        "target_value": 1,
                        "target_field": "questions_created"
                    },
                    "points_reward": 5,
                    "pcon_reward": 2,
                    "sort_order": 1
                },
                {
                    "id": "first_answer",
                    "name": "Primeira Resposta",
                    "description": "Dê sua primeira resposta útil",
                    "category": AchievementCategory.BEGINNER,
                    "rarity": AchievementRarity.COMMON,
                    "badge_icon": "💡",
                    "badge_color": "#F59E0B",
                    "criteria": {
                        "condition_type": "count",
                        "target_value": 1,
                        "target_field": "answers_created"
                    },
                    "points_reward": 5,
                    "pcon_reward": 2,
                    "sort_order": 2
                },
                # Contributor achievements
                {
                    "id": "helpful_contributor",
                    "name": "Colaborador Útil",
                    "description": "Tenha 10 respostas aceitas",
                    "category": AchievementCategory.CONTRIBUTOR,
                    "rarity": AchievementRarity.RARE,
                    "badge_icon": "🤝",
                    "badge_color": "#3B82F6",
                    "criteria": {
                        "condition_type": "count",
                        "target_value": 10,
                        "target_field": "accepted_answers"
                    },
                    "points_reward": 50,
                    "pcon_reward": 25,
                    "sort_order": 10
                },
                {
                    "id": "community_champion",
                    "name": "Campeão da Comunidade",
                    "description": "Receba 100 upvotes em suas contribuições",
                    "category": AchievementCategory.CONTRIBUTOR,
                    "rarity": AchievementRarity.EPIC,
                    "badge_icon": "🏆",
                    "badge_color": "#8B5CF6",
                    "criteria": {
                        "condition_type": "count",
                        "target_value": 100,
                        "target_field": "total_upvotes"
                    },
                    "points_reward": 100,
                    "pcon_reward": 50,
                    "sort_order": 20
                },
                # Expert achievements
                {
                    "id": "knowledge_master",
                    "name": "Mestre do Conhecimento",
                    "description": "Alcance 1000 pontos PC",
                    "category": AchievementCategory.EXPERT,
                    "rarity": AchievementRarity.LEGENDARY,
                    "badge_icon": "🧠",
                    "badge_color": "#EF4444",
                    "criteria": {
                        "condition_type": "points",
                        "target_value": 1000,
                        "target_field": "pc_points"
                    },
                    "points_reward": 200,
                    "pcon_reward": 100,
                    "sort_order": 30
                },
                # Social achievements
                {
                    "id": "social_butterfly",
                    "name": "Borboleta Social",
                    "description": "Siga 25 usuários e seja seguido por 25",
                    "category": AchievementCategory.SOCIAL,
                    "rarity": AchievementRarity.RARE,
                    "badge_icon": "🦋",
                    "badge_color": "#EC4899",
                    "criteria": {
                        "condition_type": "special",
                        "target_value": 25,
                        "additional_conditions": {
                            "followers": 25,
                            "following": 25
                        }
                    },
                    "points_reward": 30,
                    "pcon_reward": 15,
                    "sort_order": 40
                },
                # Streak achievements
                {
                    "id": "week_warrior",
                    "name": "Guerreiro da Semana",
                    "description": "Mantenha uma sequência de 7 dias consecutivos",
                    "category": AchievementCategory.STREAK,
                    "rarity": AchievementRarity.RARE,
                    "badge_icon": "🔥",
                    "badge_color": "#F97316",
                    "criteria": {
                        "condition_type": "streak",
                        "target_value": 7,
                        "target_field": "daily_login"
                    },
                    "points_reward": 25,
                    "pcon_reward": 15,
                    "sort_order": 50
                },
                {
                    "id": "month_master",
                    "name": "Mestre do Mês",
                    "description": "Mantenha uma sequência de 30 dias consecutivos",
                    "category": AchievementCategory.STREAK,
                    "rarity": AchievementRarity.LEGENDARY,
                    "badge_icon": "🌟",
                    "badge_color": "#A855F7",
                    "criteria": {
                        "condition_type": "streak",
                        "target_value": 30,
                        "target_field": "daily_login"
                    },
                    "points_reward": 150,
                    "pcon_reward": 75,
                    "sort_order": 60
                },
                # Milestone achievements
                {
                    "id": "veteran_member",
                    "name": "Membro Veterano",
                    "description": "Complete 1 ano como membro ativo",
                    "category": AchievementCategory.MILESTONE,
                    "rarity": AchievementRarity.EPIC,
                    "badge_icon": "🎖️",
                    "badge_color": "#059669",
                    "criteria": {
                        "condition_type": "special",
                        "target_value": 365,
                        "target_field": "days_since_registration"
                    },
                    "points_reward": 100,
                    "pcon_reward": 50,
                    "sort_order": 70
                },
                # Competitive achievements
                {
                    "id": "top_contributor",
                    "name": "Top Contribuidor",
                    "description": "Chegue ao Top 10 no leaderboard mensal",
                    "category": AchievementCategory.COMPETITIVE,
                    "rarity": AchievementRarity.EPIC,
                    "badge_icon": "👑",
                    "badge_color": "#DC2626",
                    "criteria": {
                        "condition_type": "special",
                        "target_value": 10,
                        "target_field": "leaderboard_position"
                    },
                    "points_reward": 75,
                    "pcon_reward": 40,
                    "sort_order": 80
                }
            ]
            
            # Insert achievements if they don't exist
            for achievement_data in achievements:
                existing = await self.user_achievements_collection.find_one({"id": achievement_data["id"]})
                if not existing:
                    achievement_data["created_at"] = datetime.now(timezone.utc)
                    await self.user_achievements_collection.insert_one(achievement_data)
            
            logger.info(f"Initialized {len(achievements)} achievements")
            
        except Exception as e:
            logger.error(f"Error initializing achievements: {str(e)}")

    async def check_advanced_achievements(self, user_id: str, action: str = None) -> List[UserAchievement]:
        """Check and award advanced achievements based on user activity"""
        try:
            # Get user data
            user = await self.users_collection.find_one({"id": user_id})
            if not user:
                return []
            
            # Get user statistics
            user_stats = await self._get_user_statistics(user_id)
            
            # Get all available achievements
            all_achievements = await self.user_achievements_collection.find({}).to_list(length=None)
            
            # Get user's current achievements
            user_achievements = await self.user_achievements_collection.find({
                "user_id": user_id,
                "is_earned": True
            }).to_list(length=None)
            
            earned_achievement_ids = [ua["achievement_id"] for ua in user_achievements]
            new_achievements = []
            
            for achievement in all_achievements:
                if achievement["id"] in earned_achievement_ids:
                    continue
                
                # Check if achievement criteria is met
                if await self._check_achievement_criteria(user_stats, achievement):
                    # Award achievement
                    user_achievement = await self._award_achievement(user_id, achievement)
                    new_achievements.append(user_achievement)
            
            return new_achievements
            
        except Exception as e:
            logger.error(f"Error checking advanced achievements: {str(e)}")
            return []

    async def _get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user statistics for achievement checking"""
        try:
            # User basic data
            user = await self.users_collection.find_one({"id": user_id})
            
            # Question statistics
            questions_count = await self.questions_collection.count_documents({"author_id": user_id})
            
            # Answer statistics
            answers_count = await self.answers_collection.count_documents({"author_id": user_id})
            accepted_answers = await self.answers_collection.count_documents({
                "author_id": user_id,
                "is_accepted": True
            })
            
            # Vote statistics
            upvotes_received = await self.votes_collection.count_documents({
                "target_id": {"$in": []},  # This would need to be populated with user's content IDs
                "vote_type": "upvote"
            })
            
            # Streak data
            login_streak = await self.streaks_collection.find_one({
                "user_id": user_id,
                "streak_type": StreakType.DAILY_LOGIN
            })
            
            # Days since registration
            days_since_registration = 0
            if user and user.get("created_at"):
                days_since_registration = (datetime.now(timezone.utc) - user["created_at"]).days
            
            return {
                "user_id": user_id,
                "pc_points": user.get("pc_points", 0) if user else 0,
                "pcon_points": user.get("pcon_points", 0) if user else 0,
                "questions_created": questions_count,
                "answers_created": answers_count,
                "accepted_answers": accepted_answers,
                "total_upvotes": upvotes_received,
                "current_login_streak": login_streak.get("current_count", 0) if login_streak else 0,
                "days_since_registration": days_since_registration,
                "followers": len(user.get("followers", [])) if user else 0,
                "following": len(user.get("following", [])) if user else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting user statistics: {str(e)}")
            return {}

    async def _check_achievement_criteria(self, user_stats: Dict[str, Any], achievement: Dict[str, Any]) -> bool:
        """Check if achievement criteria is met"""
        try:
            criteria = achievement["criteria"]
            condition_type = criteria["condition_type"]
            target_value = criteria["target_value"]
            target_field = criteria.get("target_field")
            
            if condition_type == "count":
                current_value = user_stats.get(target_field, 0)
                return current_value >= target_value
            
            elif condition_type == "points":
                current_value = user_stats.get(target_field, 0)
                return current_value >= target_value
            
            elif condition_type == "streak":
                current_value = user_stats.get(f"current_{target_field}_streak", 0)
                return current_value >= target_value
            
            elif condition_type == "special":
                # Handle special conditions
                if target_field == "leaderboard_position":
                    # This would need leaderboard checking logic
                    return False
                elif target_field == "days_since_registration":
                    return user_stats.get("days_since_registration", 0) >= target_value
                elif "additional_conditions" in criteria:
                    # Check multiple conditions
                    conditions = criteria["additional_conditions"]
                    for field, required_value in conditions.items():
                        if user_stats.get(field, 0) < required_value:
                            return False
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking achievement criteria: {str(e)}")
            return False

    async def _award_achievement(self, user_id: str, achievement: Dict[str, Any]) -> UserAchievement:
        """Award achievement to user"""
        try:
            # Create user achievement record
            user_achievement = {
                "id": generate_unique_id(),
                "user_id": user_id,
                "achievement_id": achievement["id"],
                "progress": achievement["criteria"]["target_value"],
                "earned_at": datetime.now(timezone.utc),
                "is_earned": True,
                "created_at": datetime.now(timezone.utc)
            }
            
            await self.user_achievements_collection.insert_one(user_achievement)
            
            # Award points if specified
            if achievement.get("points_reward", 0) > 0 or achievement.get("pcon_reward", 0) > 0:
                # Create a custom points award for achievement
                await gamification_service.award_points(
                    user_id,
                    "achievement_unlocked",
                    target_id=achievement["id"],
                    target_type="achievement"
                )
            
            logger.info(f"Achievement awarded: {achievement['name']} to user {user_id}")
            return UserAchievement(**user_achievement)
            
        except Exception as e:
            logger.error(f"Error awarding achievement: {str(e)}")
            raise

    async def get_user_achievement_progress(self, user_id: str, filters: AchievementFilters = None) -> List[AchievementProgress]:
        """Get user's progress on all achievements"""
        try:
            # Get user statistics
            user_stats = await self._get_user_statistics(user_id)
            
            # Build filter query
            query = {}
            if filters:
                if filters.category:
                    query["category"] = filters.category
                if filters.rarity:
                    query["rarity"] = filters.rarity
                if filters.is_hidden is not None:
                    query["is_hidden"] = filters.is_hidden
                if filters.search:
                    query["$or"] = [
                        {"name": {"$regex": filters.search, "$options": "i"}},
                        {"description": {"$regex": filters.search, "$options": "i"}}
                    ]
            
            # Get all achievements
            achievements = await self.user_achievements_collection.find(query).to_list(length=None)
            
            # Get user's earned achievements
            user_achievements = await self.user_achievements_collection.find({
                "user_id": user_id,
                "is_earned": True
            }).to_list(length=None)
            
            earned_ids = [ua["achievement_id"] for ua in user_achievements]
            
            progress_list = []
            for achievement in achievements:
                # Calculate current progress
                criteria = achievement["criteria"]
                target_value = criteria["target_value"]
                target_field = criteria.get("target_field")
                
                if criteria["condition_type"] in ["count", "points"]:
                    current_progress = user_stats.get(target_field, 0)
                elif criteria["condition_type"] == "streak":
                    current_progress = user_stats.get(f"current_{target_field}_streak", 0)
                else:
                    current_progress = 0
                
                is_earned = achievement["id"] in earned_ids
                earned_at = None
                
                if is_earned:
                    user_achievement = next((ua for ua in user_achievements if ua["achievement_id"] == achievement["id"]), None)
                    if user_achievement:
                        earned_at = user_achievement.get("earned_at")
                
                progress = AchievementProgress(
                    achievement_id=achievement["id"],
                    achievement=Achievement(**achievement),
                    current_progress=min(current_progress, target_value),
                    target_progress=target_value,
                    percentage=min(100.0, (current_progress / target_value) * 100),
                    is_earned=is_earned,
                    earned_at=earned_at
                )
                
                progress_list.append(progress)
            
            # Sort by earned status and progress
            progress_list.sort(key=lambda x: (not x.is_earned, -x.percentage))
            return progress_list
            
        except Exception as e:
            logger.error(f"Error getting achievement progress: {str(e)}")
            return []

    # ===========================================
    # BADGE SYSTEM
    # ===========================================

    async def initialize_badges(self):
        """Initialize predefined badges in the database"""
        try:
            badges = [
                # Rank badges
                {
                    "id": "rank_iniciante",
                    "name": "Iniciante",
                    "description": "Badge de rank Iniciante",
                    "icon": "🌱",
                    "color": "#10B981",
                    "badge_type": BadgeType.RANK,
                    "requirements": {"rank": "Iniciante"},
                    "sort_order": 1
                },
                {
                    "id": "rank_colaborador",
                    "name": "Colaborador",
                    "description": "Badge de rank Colaborador",
                    "icon": "⭐",
                    "color": "#F59E0B",
                    "badge_type": BadgeType.RANK,
                    "requirements": {"rank": "Colaborador"},
                    "sort_order": 2
                },
                {
                    "id": "rank_especialista",
                    "name": "Especialista",
                    "description": "Badge de rank Especialista",
                    "icon": "💎",
                    "color": "#3B82F6",
                    "badge_type": BadgeType.RANK,
                    "requirements": {"rank": "Especialista"},
                    "sort_order": 3
                },
                {
                    "id": "rank_veterano",
                    "name": "Veterano",
                    "description": "Badge de rank Veterano",
                    "icon": "🏆",
                    "color": "#8B5CF6",
                    "badge_type": BadgeType.RANK,
                    "requirements": {"rank": "Veterano"},
                    "sort_order": 4
                },
                {
                    "id": "rank_mestre",
                    "name": "Mestre",
                    "description": "Badge de rank Mestre",
                    "icon": "👑",
                    "color": "#EC4899",
                    "badge_type": BadgeType.RANK,
                    "requirements": {"rank": "Mestre"},
                    "sort_order": 5
                },
                {
                    "id": "rank_lenda",
                    "name": "Lenda",
                    "description": "Badge de rank Lenda",
                    "icon": "🌟",
                    "color": "#EF4444",
                    "badge_type": BadgeType.RANK,
                    "requirements": {"rank": "Lenda"},
                    "sort_order": 6
                },
                # Special badges
                {
                    "id": "early_adopter",
                    "name": "Early Adopter",
                    "description": "Um dos primeiros 100 usuários",
                    "icon": "🚀",
                    "color": "#6366F1",
                    "badge_type": BadgeType.SPECIAL,
                    "is_rare": True,
                    "sort_order": 10
                },
                {
                    "id": "beta_tester",
                    "name": "Beta Tester",
                    "description": "Participou dos testes beta",
                    "icon": "🧪",
                    "color": "#059669",
                    "badge_type": BadgeType.SPECIAL,
                    "is_rare": True,
                    "sort_order": 11
                },
                # Milestone badges
                {
                    "id": "question_master",
                    "name": "Mestre das Perguntas",
                    "description": "Fez 100 perguntas de qualidade",
                    "icon": "❓",
                    "color": "#DC2626",
                    "badge_type": BadgeType.MILESTONE,
                    "requirements": {"questions_created": 100},
                    "is_rare": True,
                    "sort_order": 20
                },
                {
                    "id": "answer_guru",
                    "name": "Guru das Respostas",
                    "description": "Teve 50 respostas aceitas",
                    "icon": "✅",
                    "color": "#7C3AED",
                    "badge_type": BadgeType.MILESTONE,
                    "requirements": {"accepted_answers": 50},
                    "is_rare": True,
                    "sort_order": 21
                }
            ]
            
            # Insert badges if they don't exist
            for badge_data in badges:
                existing = await self.badges_collection.find_one({"id": badge_data["id"]})
                if not existing:
                    badge_data["created_at"] = datetime.now(timezone.utc)
                    await self.badges_collection.insert_one(badge_data)
            
            logger.info(f"Initialized {len(badges)} badges")
            
        except Exception as e:
            logger.error(f"Error initializing badges: {str(e)}")

    async def award_badge(self, user_id: str, badge_id: str, is_featured: bool = False) -> UserBadge:
        """Award a badge to a user"""
        try:
            # Check if user already has this badge
            existing = await self.user_badges_collection.find_one({
                "user_id": user_id,
                "badge_id": badge_id
            })
            
            if existing:
                return UserBadge(**existing)
            
            # Get badge information
            badge = await self.badges_collection.find_one({"id": badge_id})
            if not badge:
                raise Exception(f"Badge {badge_id} not found")
            
            # Create user badge record
            user_badge = {
                "id": generate_unique_id(),
                "user_id": user_id,
                "badge_id": badge_id,
                "earned_at": datetime.now(timezone.utc),
                "is_featured": is_featured
            }
            
            await self.user_badges_collection.insert_one(user_badge)
            
            logger.info(f"Badge awarded: {badge['name']} to user {user_id}")
            return UserBadge(**user_badge)
            
        except Exception as e:
            logger.error(f"Error awarding badge: {str(e)}")
            raise

    async def get_user_badges(self, user_id: str, filters: BadgeFilters = None) -> List[UserBadge]:
        """Get user's badges with optional filtering"""
        try:
            # Build query
            query = {"user_id": user_id}
            
            # Get user badges
            user_badges_cursor = self.user_badges_collection.find(query)
            if filters and filters.is_featured is not None:
                user_badges_cursor = user_badges_cursor.find({"is_featured": filters.is_featured})
            
            user_badges = await user_badges_cursor.to_list(length=None)
            
            # Get badge details
            badge_ids = [ub["badge_id"] for ub in user_badges]
            badge_query = {"id": {"$in": badge_ids}}
            
            if filters:
                if filters.badge_type:
                    badge_query["badge_type"] = filters.badge_type
                if filters.search:
                    badge_query["$or"] = [
                        {"name": {"$regex": filters.search, "$options": "i"}},
                        {"description": {"$regex": filters.search, "$options": "i"}}
                    ]
            
            badges = await self.badges_collection.find(badge_query).to_list(length=None)
            badge_dict = {badge["id"]: badge for badge in badges}
            
            # Combine user badges with badge details
            result = []
            for user_badge in user_badges:
                badge_id = user_badge["badge_id"]
                if badge_id in badge_dict:
                    user_badge["badge"] = Badge(**badge_dict[badge_id])
                    result.append(UserBadge(**user_badge))
            
            # Sort by earned date (newest first)
            result.sort(key=lambda x: x.earned_at, reverse=True)
            return result
            
        except Exception as e:
            logger.error(f"Error getting user badges: {str(e)}")
            return []

    # ===========================================
    # STREAK SYSTEM
    # ===========================================

    async def update_streak(self, user_id: str, streak_type: StreakType) -> Streak:
        """Update user's streak for a specific type"""
        try:
            today = date.today()
            
            # Get existing streak
            streak_doc = await self.streaks_collection.find_one({
                "user_id": user_id,
                "streak_type": streak_type
            })
            
            if not streak_doc:
                # Create new streak
                streak_doc = {
                    "id": generate_unique_id(),
                    "user_id": user_id,
                    "streak_type": streak_type,
                    "current_count": 1,
                    "best_count": 1,
                    "last_activity_date": today,
                    "is_active": True,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                }
                await self.streaks_collection.insert_one(streak_doc)
            else:
                last_activity = streak_doc.get("last_activity_date")
                if last_activity:
                    if isinstance(last_activity, str):
                        last_activity = datetime.fromisoformat(last_activity).date()
                    elif isinstance(last_activity, datetime):
                        last_activity = last_activity.date()
                
                current_count = streak_doc.get("current_count", 0)
                best_count = streak_doc.get("best_count", 0)
                
                if last_activity == today:
                    # Already counted today
                    pass
                elif last_activity == today - timedelta(days=1):
                    # Consecutive day
                    current_count += 1
                    best_count = max(best_count, current_count)
                else:
                    # Streak broken
                    current_count = 1
                
                # Update streak
                await self.streaks_collection.update_one(
                    {"id": streak_doc["id"]},
                    {
                        "$set": {
                            "current_count": current_count,
                            "best_count": best_count,
                            "last_activity_date": today,
                            "is_active": True,
                            "updated_at": datetime.now(timezone.utc)
                        }
                    }
                )
                
                streak_doc.update({
                    "current_count": current_count,
                    "best_count": best_count,
                    "last_activity_date": today,
                    "updated_at": datetime.now(timezone.utc)
                })
            
            # Check for streak bonuses
            await self._check_streak_bonuses(user_id, streak_type, streak_doc["current_count"])
            
            return Streak(**streak_doc)
            
        except Exception as e:
            logger.error(f"Error updating streak: {str(e)}")
            raise

    async def _check_streak_bonuses(self, user_id: str, streak_type: StreakType, current_count: int):
        """Check and award streak bonuses"""
        try:
            # Define streak milestones and bonuses
            bonuses = {
                StreakType.DAILY_LOGIN: [
                    {"milestone": 7, "pc_bonus": 10, "pcon_bonus": 5, "badge_reward": "week_warrior"},
                    {"milestone": 30, "pc_bonus": 50, "pcon_bonus": 25, "badge_reward": "month_master"},
                    {"milestone": 100, "pc_bonus": 200, "pcon_bonus": 100, "achievement_reward": "streak_legend"}
                ],
                StreakType.DAILY_ACTIVITY: [
                    {"milestone": 14, "pc_bonus": 20, "pcon_bonus": 10},
                    {"milestone": 60, "pc_bonus": 100, "pcon_bonus": 50}
                ]
            }
            
            streak_bonuses = bonuses.get(streak_type, [])
            
            for bonus in streak_bonuses:
                if current_count == bonus["milestone"]:
                    # Award bonus points
                    if bonus.get("pc_bonus", 0) > 0 or bonus.get("pcon_bonus", 0) > 0:
                        await gamification_service.award_points(
                            user_id,
                            f"streak_bonus_{streak_type}_{bonus['milestone']}",
                            target_id=str(bonus["milestone"]),
                            target_type="streak_milestone"
                        )
                    
                    # Award badge if specified
                    if bonus.get("badge_reward"):
                        await self.award_badge(user_id, bonus["badge_reward"])
                    
                    # Award achievement if specified
                    if bonus.get("achievement_reward"):
                        # This would trigger achievement checking
                        await self.check_advanced_achievements(user_id, "streak_milestone")
                    
                    logger.info(f"Streak bonus awarded to user {user_id}: {streak_type} {bonus['milestone']} days")
                    break
            
        except Exception as e:
            logger.error(f"Error checking streak bonuses: {str(e)}")

    async def get_user_streaks(self, user_id: str) -> List[Streak]:
        """Get all user's streaks"""
        try:
            cursor = self.streaks_collection.find({"user_id": user_id})
            streaks = await cursor.to_list(length=None)
            return [Streak(**streak) for streak in streaks]
            
        except Exception as e:
            logger.error(f"Error getting user streaks: {str(e)}")
            return []

    # ===========================================
    # ENHANCED LEADERBOARDS
    # ===========================================

    async def generate_leaderboard(self, leaderboard_type: LeaderboardType, limit: int = 100) -> Leaderboard:
        """Generate leaderboard for specific type and time period"""
        try:
            now = datetime.now(timezone.utc)
            
            # Calculate period
            if leaderboard_type in [LeaderboardType.WEEKLY_PC, LeaderboardType.WEEKLY_PCON]:
                # Current week (Monday to Sunday)
                days_since_monday = now.weekday()
                period_start = (now - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
                period_end = period_start + timedelta(days=7)
            elif leaderboard_type in [LeaderboardType.MONTHLY_PC, LeaderboardType.MONTHLY_PCON]:
                # Current month
                period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                _, last_day = calendar.monthrange(now.year, now.month)
                period_end = period_start.replace(day=last_day, hour=23, minute=59, second=59)
            else:
                # All time
                period_start = datetime(2020, 1, 1, tzinfo=timezone.utc)
                period_end = now
            
            # Build aggregation pipeline based on leaderboard type
            if leaderboard_type in [LeaderboardType.ALL_TIME_PC, LeaderboardType.WEEKLY_PC, LeaderboardType.MONTHLY_PC]:
                sort_field = "pc_points"
            elif leaderboard_type in [LeaderboardType.ALL_TIME_PCON, LeaderboardType.WEEKLY_PCON, LeaderboardType.MONTHLY_PCON]:
                sort_field = "pcon_points"
            elif leaderboard_type == LeaderboardType.QUESTIONS_ANSWERED:
                # Need to aggregate from answers collection
                pipeline = [
                    {"$match": {"created_at": {"$gte": period_start, "$lte": period_end}}},
                    {"$group": {"_id": "$author_id", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                    {"$limit": limit}
                ]
                results = await self.answers_collection.aggregate(pipeline).to_list(length=None)
                entries = await self._build_leaderboard_entries(results, "count")
            elif leaderboard_type == LeaderboardType.BEST_ANSWERS:
                # Accepted answers
                pipeline = [
                    {"$match": {
                        "created_at": {"$gte": period_start, "$lte": period_end},
                        "is_accepted": True
                    }},
                    {"$group": {"_id": "$author_id", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                    {"$limit": limit}
                ]
                results = await self.answers_collection.aggregate(pipeline).to_list(length=None)
                entries = await self._build_leaderboard_entries(results, "count")
            else:
                # Default to PC points
                sort_field = "pc_points"
            
            # For point-based leaderboards
            if leaderboard_type in [LeaderboardType.ALL_TIME_PC, LeaderboardType.ALL_TIME_PCON, 
                                  LeaderboardType.WEEKLY_PC, LeaderboardType.WEEKLY_PCON,
                                  LeaderboardType.MONTHLY_PC, LeaderboardType.MONTHLY_PCON]:
                
                # For weekly/monthly, we need to sum points from history within period
                if "WEEKLY" in leaderboard_type.value or "MONTHLY" in leaderboard_type.value:
                    point_field = "pc_points_change" if "PC" in leaderboard_type.value else "pcon_points_change"
                    pipeline = [
                        {"$match": {"created_at": {"$gte": period_start, "$lte": period_end}}},
                        {"$group": {"_id": "$user_id", "total": {"$sum": f"${point_field}"}}},
                        {"$sort": {"total": -1}},
                        {"$limit": limit}
                    ]
                    results = await gamification_service.points_history_collection.aggregate(pipeline).to_list(length=None)
                    entries = await self._build_leaderboard_entries(results, "total")
                else:
                    # All time - use current totals
                    cursor = self.users_collection.find(
                        {},
                        {"id": 1, "username": 1, "avatar_url": 1, "rank": 1, sort_field: 1}
                    ).sort(sort_field, -1).limit(limit)
                    
                    users = await cursor.to_list(length=None)
                    entries = []
                    
                    for i, user in enumerate(users):
                        entry = LeaderboardEntry(
                            position=i + 1,
                            user_id=user["id"],
                            username=user["username"],
                            avatar_url=user.get("avatar_url"),
                            score=user.get(sort_field, 0),
                            rank=user.get("rank", "Iniciante"),
                            badges=[]  # Could be populated with user's featured badges
                        )
                        entries.append(entry)
            
            # Create leaderboard
            leaderboard = Leaderboard(
                leaderboard_type=leaderboard_type,
                entries=entries,
                period_start=period_start,
                period_end=period_end,
                last_updated=now
            )
            
            # Store/update in database
            await self.leaderboards_collection.replace_one(
                {"leaderboard_type": leaderboard_type.value},
                leaderboard.model_dump(),
                upsert=True
            )
            
            return leaderboard
            
        except Exception as e:
            logger.error(f"Error generating leaderboard: {str(e)}")
            raise

    async def _build_leaderboard_entries(self, results: List[Dict], score_field: str) -> List[LeaderboardEntry]:
        """Build leaderboard entries from aggregation results"""
        try:
            entries = []
            user_ids = [result["_id"] for result in results]
            
            # Get user details
            users = await self.users_collection.find(
                {"id": {"$in": user_ids}},
                {"id": 1, "username": 1, "avatar_url": 1, "rank": 1}
            ).to_list(length=None)
            
            user_dict = {user["id"]: user for user in users}
            
            for i, result in enumerate(results):
                user_id = result["_id"]
                user = user_dict.get(user_id, {})
                
                entry = LeaderboardEntry(
                    position=i + 1,
                    user_id=user_id,
                    username=user.get("username", "Unknown"),
                    avatar_url=user.get("avatar_url"),
                    score=result[score_field],
                    rank=user.get("rank", "Iniciante"),
                    badges=[]
                )
                entries.append(entry)
            
            return entries
            
        except Exception as e:
            logger.error(f"Error building leaderboard entries: {str(e)}")
            return []

    async def get_user_leaderboard_position(self, user_id: str, leaderboard_type: LeaderboardType) -> Optional[int]:
        """Get user's position in a specific leaderboard"""
        try:
            leaderboard = await self.leaderboards_collection.find_one({"leaderboard_type": leaderboard_type.value})
            if not leaderboard:
                return None
            
            for entry in leaderboard.get("entries", []):
                if entry.get("user_id") == user_id:
                    return entry.get("position")
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting user leaderboard position: {str(e)}")
            return None

    # ===========================================
    # COMPREHENSIVE DASHBOARD
    # ===========================================

    async def get_gamification_dashboard(self, user_id: str) -> GamificationDashboard:
        """Get comprehensive gamification dashboard for user"""
        try:
            # Get user profile
            user = await self.users_collection.find_one({"id": user_id})
            if not user:
                raise Exception("User not found")
            
            # Get user achievements
            achievements = await self.get_user_achievement_progress(user_id)
            recent_achievements = [a for a in achievements if a.is_earned][:5]
            
            # Get user badges
            badges = await self.get_user_badges(user_id)
            
            # Get user streaks
            streaks = await self.get_user_streaks(user_id)
            active_streaks = [s for s in streaks if s.is_active]
            
            # Get leaderboard positions
            leaderboard_positions = []
            for leaderboard_type in LeaderboardType:
                position = await self.get_user_leaderboard_position(user_id, leaderboard_type)
                if position and position <= 100:  # Only show if in top 100
                    # Get leaderboard to get entry details
                    leaderboard = await self.leaderboards_collection.find_one({"leaderboard_type": leaderboard_type.value})
                    if leaderboard:
                        for entry in leaderboard.get("entries", []):
                            if entry.get("user_id") == user_id:
                                leaderboard_positions.append(LeaderboardEntry(**entry))
                                break
            
            # Get suggested goals (unearned achievements with high progress)
            suggested_goals = [a.achievement for a in achievements if not a.is_earned and a.percentage > 50][:3]
            
            # Get gamification stats
            stats = await gamification_service.get_gamification_stats()
            
            # Create user profile
            user_profile = UserGamificationProfile(
                user_id=user_id,
                username=user["username"],
                pc_points=user.get("pc_points", 0),
                pcon_points=user.get("pcon_points", 0),
                rank=user.get("rank", "Iniciante"),
                level=self._calculate_user_level(user.get("pc_points", 0)),
                achievements=[UserAchievement(**a.model_dump()) for a in recent_achievements],
                badges=badges,
                streaks=active_streaks,
                leaderboard_positions={str(pos.position): pos.position for pos in leaderboard_positions},
                total_achievements=len([a for a in achievements if a.is_earned]),
                total_badges=len(badges),
                joined_at=user.get("created_at", datetime.now(timezone.utc))
            )
            
            # Create dashboard
            dashboard = GamificationDashboard(
                user_profile=user_profile,
                recent_achievements=[UserAchievement(**a.model_dump()) for a in recent_achievements],
                active_streaks=active_streaks,
                leaderboard_positions=leaderboard_positions,
                suggested_goals=suggested_goals,
                stats=stats
            )
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Error getting gamification dashboard: {str(e)}")
            raise

    def _calculate_user_level(self, pc_points: int) -> int:
        """Calculate user level based on PC points"""
        # Simple level calculation: every 100 PC points = 1 level
        return max(1, pc_points // 100)

    # ===========================================
    # REFERRAL SYSTEM
    # ===========================================

    async def create_referral(self, referrer_id: str, referred_id: str) -> ReferralReward:
        """Create a referral record"""
        try:
            # Check if referral already exists
            existing = await self.referrals_collection.find_one({"referred_id": referred_id})
            if existing:
                raise Exception("User already referred by someone")
            
            # Create referral record
            referral = {
                "id": generate_unique_id(),
                "referrer_id": referrer_id,
                "referred_id": referred_id,
                "milestone": "signup",
                "pc_reward": 10,
                "pcon_reward": 5,
                "created_at": datetime.now(timezone.utc)
            }
            
            await self.referrals_collection.insert_one(referral)
            
            # Award initial referral points
            await gamification_service.award_points(
                referrer_id,
                "referral_signup",
                target_id=referred_id,
                target_type="referral"
            )
            
            logger.info(f"Referral created: {referrer_id} referred {referred_id}")
            return ReferralReward(**referral)
            
        except Exception as e:
            logger.error(f"Error creating referral: {str(e)}")
            raise

    async def check_referral_milestones(self, user_id: str, milestone: str):
        """Check and award referral milestone rewards"""
        try:
            # Get referral record
            referral = await self.referrals_collection.find_one({"referred_id": user_id})
            if not referral:
                return
            
            referrer_id = referral["referrer_id"]
            
            # Award milestone rewards
            rewards = {
                "first_question": {"pc": 5, "pcon": 3},
                "first_answer": {"pc": 10, "pcon": 5},
                "active_user": {"pc": 25, "pcon": 15}  # After 1 week of activity
            }
            
            if milestone in rewards:
                reward = rewards[milestone]
                
                # Create milestone record
                milestone_reward = {
                    "id": generate_unique_id(),
                    "referrer_id": referrer_id,
                    "referred_id": user_id,
                    "milestone": milestone,
                    "pc_reward": reward["pc"],
                    "pcon_reward": reward["pcon"],
                    "created_at": datetime.now(timezone.utc)
                }
                
                await self.referrals_collection.insert_one(milestone_reward)
                
                # Award points to referrer
                await gamification_service.award_points(
                    referrer_id,
                    f"referral_{milestone}",
                    target_id=user_id,
                    target_type="referral_milestone"
                )
                
                logger.info(f"Referral milestone achieved: {milestone} for {referrer_id}")
            
        except Exception as e:
            logger.error(f"Error checking referral milestones: {str(e)}")


# Global service instance
advanced_gamification_service = AdvancedGamificationService()