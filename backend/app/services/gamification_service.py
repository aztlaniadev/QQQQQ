"""
Gamification Service Module
Handles PC/PCon points, ranks, achievements, and user progression
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import logging

from ..core.database import get_users_collection, get_points_history_collection, get_achievements_collection
from ..core.config import settings
from ..core.security import generate_unique_id

logger = logging.getLogger(__name__)


class GamificationService:
    """Gamification service for points, ranks, and achievements"""
    
    def __init__(self):
        self._users_collection = None
        self._points_history_collection = None
        self._achievements_collection = None
    
    @property
    def users_collection(self):
        """Lazy load users collection"""
        if self._users_collection is None:
            self._users_collection = get_users_collection()
        return self._users_collection
    
    @property
    def points_history_collection(self):
        """Lazy load points history collection"""
        if self._points_history_collection is None:
            self._points_history_collection = get_points_history_collection()
        return self._points_history_collection
    
    @property
    def achievements_collection(self):
        """Lazy load achievements collection"""
        if self._achievements_collection is None:
            self._achievements_collection = get_achievements_collection()
        return self._achievements_collection

    # ===========================================
    # POINTS SYSTEM
    # ===========================================

    async def award_points(self, user_id: str, action: str, target_id: str = None, target_type: str = None) -> Dict[str, Any]:
        """Award points to a user for a specific action"""
        try:
            # Get point configuration for action
            pc_config = settings.pc_points_config
            pcon_config = settings.pcon_points_config
            
            pc_points = pc_config.get(action, 0)
            pcon_points = pcon_config.get(action, 0)
            
            if pc_points == 0 and pcon_points == 0:
                logger.warning(f"No points configured for action: {action}")
                return {"pc_points": 0, "pcon_points": 0}
            
            # Get current user
            user = await self.users_collection.find_one({"id": user_id})
            if not user:
                raise Exception("User not found")
            
            current_pc = user.get("pc_points", 0)
            current_pcon = user.get("pcon_points", 0)
            
            # Calculate new totals
            new_pc = max(0, current_pc + pc_points)  # PC points can't go below 0
            new_pcon = max(0, current_pcon + pcon_points)  # PCon points can't go below 0
            
            # Update user points
            await self.users_collection.update_one(
                {"id": user_id},
                {
                    "$set": {
                        "pc_points": new_pc,
                        "pcon_points": new_pcon,
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
            
            # Record points history
            history_entry = {
                "id": generate_unique_id(),
                "user_id": user_id,
                "action": action,
                "pc_points_change": pc_points,
                "pcon_points_change": pcon_points,
                "pc_points_total": new_pc,
                "pcon_points_total": new_pcon,
                "target_id": target_id,
                "target_type": target_type,
                "created_at": datetime.now(timezone.utc)
            }
            
            await self.points_history_collection.insert_one(history_entry)
            
            # Update user rank based on new points
            await self.update_user_rank(user_id, new_pc, new_pcon)
            
            # Check for achievements
            await self.check_achievements(user_id, action, new_pc, new_pcon)
            
            logger.info(f"Points awarded to user {user_id}: {action} -> PC:{pc_points}, PCon:{pcon_points}")
            
            return {
                "pc_points": pc_points,
                "pcon_points": pcon_points,
                "total_pc": new_pc,
                "total_pcon": new_pcon,
                "action": action
            }
            
        except Exception as e:
            logger.error(f"Error awarding points: {str(e)}")
            raise Exception(f"Failed to award points: {str(e)}")

    async def get_user_points_history(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user's points history"""
        try:
            cursor = self.points_history_collection.find(
                {"user_id": user_id}
            ).sort("created_at", -1).limit(limit)
            
            history = await cursor.to_list(length=None)
            return history
            
        except Exception as e:
            logger.error(f"Error getting points history for user {user_id}: {str(e)}")
            return []

    # ===========================================
    # RANKING SYSTEM
    # ===========================================

    async def update_user_rank(self, user_id: str, pc_points: int, pcon_points: int) -> str:
        """Update user rank based on points"""
        try:
            # Get rank configuration
            rank_config = settings.rank_config
            
            # Determine rank based on PC points (primary) and PCon points (secondary)
            current_rank = "Iniciante"
            
            for rank_name, requirements in rank_config.items():
                required_pc = requirements.get("pc_points", 0)
                required_pcon = requirements.get("pcon_points", 0)
                
                if pc_points >= required_pc and pcon_points >= required_pcon:
                    current_rank = rank_name
            
            # Update user rank
            await self.users_collection.update_one(
                {"id": user_id},
                {
                    "$set": {
                        "rank": current_rank,
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
            
            logger.info(f"User {user_id} rank updated to: {current_rank}")
            return current_rank
            
        except Exception as e:
            logger.error(f"Error updating user rank: {str(e)}")
            return "Iniciante"

    async def get_leaderboard(self, limit: int = 50, rank_by: str = "pc_points") -> List[Dict[str, Any]]:
        """Get user leaderboard"""
        try:
            sort_field = rank_by if rank_by in ["pc_points", "pcon_points"] else "pc_points"
            
            cursor = self.users_collection.find(
                {},
                {
                    "id": 1,
                    "username": 1,
                    "avatar_url": 1,
                    "rank": 1,
                    "pc_points": 1,
                    "pcon_points": 1,
                    "created_at": 1
                }
            ).sort(sort_field, -1).limit(limit)
            
            leaderboard = await cursor.to_list(length=None)
            
            # Add position
            for i, user in enumerate(leaderboard):
                user["position"] = i + 1
            
            return leaderboard
            
        except Exception as e:
            logger.error(f"Error getting leaderboard: {str(e)}")
            return []

    # ===========================================
    # ACHIEVEMENTS SYSTEM
    # ===========================================

    async def check_achievements(self, user_id: str, action: str, pc_points: int, pcon_points: int):
        """Check and award achievements"""
        try:
            # Get user's current achievements
            user = await self.users_collection.find_one({"id": user_id})
            current_achievements = user.get("achievements", [])
            
            new_achievements = []
            
            # Define achievement criteria
            achievement_criteria = {
                "primeira_pergunta": {
                    "name": "Primeira Pergunta",
                    "description": "Criou sua primeira pergunta",
                    "condition": lambda: action == "question_created",
                    "badge": "🤔"
                },
                "primeira_resposta": {
                    "name": "Primeira Resposta",
                    "description": "Criou sua primeira resposta",
                    "condition": lambda: action == "answer_created",
                    "badge": "💡"
                },
                "resposta_aceita": {
                    "name": "Resposta Aceita",
                    "description": "Teve uma resposta aceita",
                    "condition": lambda: action == "answer_accepted",
                    "badge": "✅"
                },
                "veterano": {
                    "name": "Veterano",
                    "description": "Alcançou 100 pontos PC",
                    "condition": lambda: pc_points >= 100,
                    "badge": "🏆"
                },
                "especialista": {
                    "name": "Especialista",
                    "description": "Alcançou 500 pontos PC",
                    "condition": lambda: pc_points >= 500,
                    "badge": "🎯"
                },
                "mestre": {
                    "name": "Mestre",
                    "description": "Alcançou 1000 pontos PC",
                    "condition": lambda: pc_points >= 1000,
                    "badge": "👑"
                },
                "pcon_iniciante": {
                    "name": "PCon Iniciante",
                    "description": "Alcançou 50 pontos PCon",
                    "condition": lambda: pcon_points >= 50,
                    "badge": "💰"
                },
                "pcon_profissional": {
                    "name": "PCon Profissional",
                    "description": "Alcançou 200 pontos PCon",
                    "condition": lambda: pcon_points >= 200,
                    "badge": "💎"
                }
            }
            
            # Check each achievement
            for achievement_id, criteria in achievement_criteria.items():
                if achievement_id not in current_achievements:
                    if criteria["condition"]():
                        new_achievements.append(achievement_id)
                        
                        # Create achievement record
                        achievement_doc = {
                            "id": generate_unique_id(),
                            "user_id": user_id,
                            "achievement_id": achievement_id,
                            "name": criteria["name"],
                            "description": criteria["description"],
                            "badge": criteria["badge"],
                            "earned_at": datetime.now(timezone.utc)
                        }
                        
                        await self.achievements_collection.insert_one(achievement_doc)
                        logger.info(f"Achievement earned by user {user_id}: {criteria['name']}")
            
            # Update user achievements
            if new_achievements:
                await self.users_collection.update_one(
                    {"id": user_id},
                    {
                        "$addToSet": {"achievements": {"$each": new_achievements}},
                        "$set": {"updated_at": datetime.now(timezone.utc)}
                    }
                )
            
        except Exception as e:
            logger.error(f"Error checking achievements: {str(e)}")

    async def get_user_achievements(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's achievements"""
        try:
            cursor = self.achievements_collection.find({"user_id": user_id}).sort("earned_at", -1)
            achievements = await cursor.to_list(length=None)
            return achievements
            
        except Exception as e:
            logger.error(f"Error getting achievements for user {user_id}: {str(e)}")
            return []

    # ===========================================
    # DAILY ACTIVITIES
    # ===========================================

    async def award_daily_login(self, user_id: str) -> Dict[str, Any]:
        """Award daily login points"""
        try:
            # Check if user already got daily login points today
            today = datetime.now(timezone.utc).date()
            
            # Check points history for today
            today_start = datetime.combine(today, datetime.min.time().replace(tzinfo=timezone.utc))
            today_end = datetime.combine(today, datetime.max.time().replace(tzinfo=timezone.utc))
            
            existing_login = await self.points_history_collection.find_one({
                "user_id": user_id,
                "action": "daily_login",
                "created_at": {"$gte": today_start, "$lte": today_end}
            })
            
            if existing_login:
                return {"message": "Daily login already claimed today", "points": 0}
            
            # Award daily login points
            result = await self.award_points(user_id, "daily_login")
            result["message"] = "Daily login bonus claimed!"
            
            return result
            
        except Exception as e:
            logger.error(f"Error awarding daily login: {str(e)}")
            raise Exception(f"Failed to award daily login: {str(e)}")

    # ===========================================
    # STATISTICS
    # ===========================================

    async def get_gamification_stats(self) -> Dict[str, Any]:
        """Get gamification statistics"""
        try:
            # Total points distributed
            pipeline = [
                {"$group": {
                    "_id": None,
                    "total_pc_distributed": {"$sum": "$pc_points_change"},
                    "total_pcon_distributed": {"$sum": "$pcon_points_change"},
                    "total_transactions": {"$sum": 1}
                }}
            ]
            
            result = await self.points_history_collection.aggregate(pipeline).to_list(1)
            stats = result[0] if result else {
                "total_pc_distributed": 0,
                "total_pcon_distributed": 0,
                "total_transactions": 0
            }
            
            # Top users by PC points
            top_pc_users = await self.get_leaderboard(10, "pc_points")
            
            # Top users by PCon points
            top_pcon_users = await self.get_leaderboard(10, "pcon_points")
            
            # Achievement statistics
            total_achievements = await self.achievements_collection.count_documents({})
            
            # Active users (users with points)
            active_users = await self.users_collection.count_documents({
                "$or": [
                    {"pc_points": {"$gt": 0}},
                    {"pcon_points": {"$gt": 0}}
                ]
            })
            
            return {
                "total_pc_distributed": stats["total_pc_distributed"],
                "total_pcon_distributed": stats["total_pcon_distributed"],
                "total_transactions": stats["total_transactions"],
                "total_achievements": total_achievements,
                "active_users": active_users,
                "top_pc_users": top_pc_users[:5],  # Top 5 for summary
                "top_pcon_users": top_pcon_users[:5]  # Top 5 for summary
            }
            
        except Exception as e:
            logger.error(f"Error getting gamification stats: {str(e)}")
            return {
                "total_pc_distributed": 0,
                "total_pcon_distributed": 0,
                "total_transactions": 0,
                "total_achievements": 0,
                "active_users": 0,
                "top_pc_users": [],
                "top_pcon_users": []
            }


# Global service instance
gamification_service = GamificationService()