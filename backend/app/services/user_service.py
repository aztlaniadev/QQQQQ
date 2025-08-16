"""
User service - handles user management and statistics
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from fastapi import HTTPException, status
from ..core.database import get_users_collection, get_questions_collection, get_answers_collection, get_votes_collection
from ..core.security import hash_password, generate_unique_id
from ..core.config import settings
from ..models.user import (
    UserUpdate, UserResponse, UserStats, 
    BotUserCreate, UserModerationAction,
    User
)
from ..models.base import PaginatedResponse

logger = logging.getLogger(__name__)


class UserService:
    """User service class"""
    
    def __init__(self):
        self._users_collection = None
        self._questions_collection = None
        self._answers_collection = None
        self._votes_collection = None
    
    @property
    def users_collection(self):
        """Lazy load users collection"""
        if self._users_collection is None:
            self._users_collection = get_users_collection()
        return self._users_collection
    
    @property
    def questions_collection(self):
        """Lazy load questions collection"""
        if self._questions_collection is None:
            self._questions_collection = get_questions_collection()
        return self._questions_collection
    
    @property
    def answers_collection(self):
        """Lazy load answers collection"""
        if self._answers_collection is None:
            self._answers_collection = get_answers_collection()
        return self._answers_collection
    
    @property
    def votes_collection(self):
        """Lazy load votes collection"""
        if self._votes_collection is None:
            self._votes_collection = get_votes_collection()
        return self._votes_collection
    
    async def update_user_profile(self, user_id: str, update_data: UserUpdate) -> UserResponse:
        """Update user profile"""
        try:
            # Check if user exists
            user = await self.users_collection.find_one({"id": user_id})
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Prepare update data
            update_dict = {}
            for field, value in update_data.dict(exclude_unset=True).items():
                if value is not None:
                    update_dict[field] = value
            
            if update_dict:
                update_dict["updated_at"] = datetime.utcnow()
                
                # Check if username is being updated and is unique
                if "username" in update_dict:
                    existing_user = await self.users_collection.find_one({
                        "username": update_dict["username"],
                        "id": {"$ne": user_id}
                    })
                    if existing_user:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Username already taken"
                        )
                
                # Update user
                await self.users_collection.update_one(
                    {"id": user_id},
                    {"$set": update_dict}
                )
            
            # Get updated user
            updated_user = await self.users_collection.find_one({"id": user_id})
            user_dict = {k: v for k, v in updated_user.items() if k != "password_hash"}
            
            return UserResponse(**user_dict)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating user profile: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    async def get_user_by_id(self, user_id: str) -> UserResponse:
        """Get user by ID"""
        try:
            user = await self.users_collection.find_one({"id": user_id})
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            user_dict = {k: v for k, v in user.items() if k != "password_hash"}
            return UserResponse(**user_dict)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    async def get_user_stats(self, user_id: str) -> UserStats:
        """Get detailed user statistics"""
        try:
            # Get user
            user = await self.users_collection.find_one({"id": user_id})
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Get statistics
            questions_count = await self.questions_collection.count_documents({
                "author_id": user_id,
                "is_deleted": {"$ne": True}
            })
            
            answers_count = await self.answers_collection.count_documents({
                "author_id": user_id,
                "is_deleted": {"$ne": True}
            })
            
            accepted_answers = await self.answers_collection.count_documents({
                "author_id": user_id,
                "is_accepted": True,
                "is_deleted": {"$ne": True}
            })
            
            # Get vote statistics
            upvotes_received = await self.answers_collection.aggregate([
                {"$match": {"author_id": user_id, "is_deleted": {"$ne": True}}},
                {"$group": {"_id": None, "total": {"$sum": "$upvotes"}}}
            ]).to_list(1)
            
            downvotes_received = await self.answers_collection.aggregate([
                {"$match": {"author_id": user_id, "is_deleted": {"$ne": True}}},
                {"$group": {"_id": None, "total": {"$sum": "$downvotes"}}}
            ]).to_list(1)
            
            votes_given = await self.votes_collection.count_documents({"user_id": user_id})
            
            # Get questions solved (where user's answer was accepted)
            questions_solved = await self.questions_collection.count_documents({
                "accepted_answer_id": {"$exists": True},
                "accepted_answer_id": {"$ne": None}
            })
            
            # Calculate reputation score
            reputation_score = (
                user.get("pc_points", 0) + 
                (upvotes_received[0]["total"] if upvotes_received else 0) * 3 -
                (downvotes_received[0]["total"] if downvotes_received else 0)
            )
            
            return UserStats(
                total_questions=questions_count,
                total_answers=answers_count,
                accepted_answers=accepted_answers,
                total_upvotes_received=upvotes_received[0]["total"] if upvotes_received else 0,
                total_downvotes_received=downvotes_received[0]["total"] if downvotes_received else 0,
                total_votes_given=votes_given,
                pc_points=user.get("pc_points", 0),
                pcon_points=user.get("pcon_points", 0),
                rank=user.get("rank", "Iniciante"),
                achievements=user.get("achievements", []),
                join_date=user.get("created_at"),
                last_activity=user.get("last_login"),
                questions_solved=questions_solved,
                reputation_score=reputation_score
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    async def get_users_list(self, skip: int = 0, limit: int = 20, admin_user: dict = None) -> PaginatedResponse[UserResponse]:
        """Get paginated list of users (admin only)"""
        try:
            # Build query
            query = {"is_deleted": {"$ne": True}}
            
            # Count total
            total = await self.users_collection.count_documents(query)
            
            # Get users
            cursor = self.users_collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
            users = await cursor.to_list(length=limit)
            
            # Convert to response models
            user_responses = []
            for user in users:
                user_dict = {k: v for k, v in user.items() if k != "password_hash"}
                user_responses.append(UserResponse(**user_dict))
            
            # Calculate pagination info
            pages = (total + limit - 1) // limit
            current_page = skip // limit
            
            return PaginatedResponse(
                items=user_responses,
                total=total,
                page=current_page,
                size=limit,
                pages=pages,
                has_next=current_page < pages - 1,
                has_prev=current_page > 0
            )
            
        except Exception as e:
            logger.error(f"Error getting users list: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    async def create_bot_user(self, bot_data: BotUserCreate) -> UserResponse:
        """Create a bot user (admin only)"""
        try:
            # Check if username/email already exists
            existing_user = await self.users_collection.find_one({
                "$or": [
                    {"email": bot_data.email},
                    {"username": bot_data.username}
                ]
            })
            
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email or username already exists"
                )
            
            # Create bot user
            user_id = generate_unique_id()
            bot_password = generate_unique_id()  # Random password for bot
            
            new_bot = User(
                id=user_id,
                username=bot_data.username,
                email=bot_data.email,
                password_hash=hash_password(bot_password),
                is_bot=True,
                bot_description=bot_data.description,
                bot_auto_answer=bot_data.auto_answer,
                bot_source_api=bot_data.source_api,
                created_at=datetime.utcnow()
            )
            
            await self.users_collection.insert_one(new_bot.dict())
            
            # Return response
            bot_dict = new_bot.dict()
            del bot_dict["password_hash"]
            
            logger.info(f"Bot user created: {bot_data.username}")
            
            return UserResponse(**bot_dict)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating bot user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    async def moderate_user(self, user_id: str, action_data: UserModerationAction) -> dict:
        """Moderate user (ban, mute, silence, etc.)"""
        try:
            user = await self.users_collection.find_one({"id": user_id})
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Check if trying to moderate an admin
            if user.get("is_admin", False):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot moderate admin users"
                )
            
            update_data = {"updated_at": datetime.utcnow()}
            action = action_data.action
            
            # Calculate end date if duration is specified
            end_date = None
            if action_data.duration_hours:
                end_date = datetime.utcnow() + timedelta(hours=action_data.duration_hours)
            
            if action == "ban":
                update_data.update({
                    "is_banned": True,
                    "ban_reason": action_data.reason,
                    "ban_until": end_date
                })
            elif action == "unban":
                update_data.update({
                    "is_banned": False,
                    "ban_reason": None,
                    "ban_until": None
                })
            elif action == "mute":
                update_data.update({
                    "is_muted": True,
                    "mute_reason": action_data.reason,
                    "mute_until": end_date
                })
            elif action == "unmute":
                update_data.update({
                    "is_muted": False,
                    "mute_reason": None,
                    "mute_until": None
                })
            elif action == "silence":
                update_data.update({
                    "is_silenced": True,
                    "silence_reason": action_data.reason,
                    "silence_until": end_date
                })
            elif action == "unsilence":
                update_data.update({
                    "is_silenced": False,
                    "silence_reason": None,
                    "silence_until": None
                })
            
            await self.users_collection.update_one(
                {"id": user_id},
                {"$set": update_data}
            )
            
            logger.info(f"User {user_id} moderated: {action}")
            
            return {
                "message": f"User {action}ned successfully",
                "action": action,
                "user_id": user_id,
                "reason": action_data.reason,
                "duration_hours": action_data.duration_hours,
                "end_date": end_date.isoformat() if end_date else None
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error moderating user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    async def delete_user(self, user_id: str) -> dict:
        """Permanently delete user (admin only)"""
        try:
            user = await self.users_collection.find_one({"id": user_id})
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Check if trying to delete an admin
            if user.get("is_admin", False):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot delete admin users"
                )
            
            # Soft delete - mark as deleted instead of removing
            await self.users_collection.update_one(
                {"id": user_id},
                {
                    "$set": {
                        "is_deleted": True,
                        "deleted_at": datetime.utcnow(),
                        "is_active": False
                    }
                }
            )
            
            logger.info(f"User {user_id} marked as deleted")
            
            return {
                "message": "User deleted successfully",
                "user_id": user_id,
                "deleted_at": datetime.utcnow().isoformat()
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    async def get_user_vote(self, user_id: str, target_id: str) -> Optional[str]:
        """Get user's vote on a specific target"""
        try:
            vote = await self.votes_collection.find_one({
                "user_id": user_id,
                "target_id": target_id
            })
            return vote["vote_type"] if vote else None
            
        except Exception as e:
            logger.error(f"Error getting user vote: {e}")
            return None


# Global user service instance
user_service = UserService()