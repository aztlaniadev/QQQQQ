"""
Authentication service - handles user registration, login, and token management
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from fastapi import HTTPException, status
from ..core.database import get_users_collection
from ..core.security import (
    hash_password, 
    verify_password, 
    create_access_token, 
    create_refresh_token,
    verify_token,
    generate_unique_id
)
from ..core.config import settings
from ..models.user import User, UserCreate, UserLogin, UserResponse
from ..models.base import TokenResponse

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service class"""
    
    def __init__(self):
        self._users_collection = None
    
    @property
    def users_collection(self):
        """Lazy load users collection"""
        if self._users_collection is None:
            self._users_collection = get_users_collection()
        return self._users_collection
    
    async def register_user(self, user_data: UserCreate) -> TokenResponse:
        """Register a new user"""
        try:
            # Check if user already exists
            existing_user = await self.users_collection.find_one({
                "$or": [
                    {"email": user_data.email},
                    {"username": user_data.username}
                ]
            })
            
            if existing_user:
                if existing_user["email"] == user_data.email:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email already registered"
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Username already taken"
                    )
            
            # Create new user
            user_id = generate_unique_id()
            hashed_password = hash_password(user_data.password)
            
            new_user = User(
                id=user_id,
                username=user_data.username,
                email=user_data.email,
                password_hash=hashed_password,
                created_at=datetime.utcnow(),
                achievements=["first_join"]  # First achievement
            )
            
            # Insert user into database
            await self.users_collection.insert_one(new_user.dict())
            
            # Create tokens
            token_data = {"sub": user_id, "email": user_data.email}
            access_token = create_access_token(token_data)
            refresh_token = create_refresh_token(token_data)
            
            # Prepare user response (without password hash)
            user_dict = new_user.dict()
            del user_dict["password_hash"]
            
            logger.info(f"User registered successfully: {user_data.email}")
            
            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=settings.access_token_expire_minutes * 60,
                user=user_dict
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error during registration"
            )
    
    async def login_user(self, login_data: UserLogin) -> TokenResponse:
        """Login user with email and password"""
        try:
            # Find user by email
            user = await self.users_collection.find_one({"email": login_data.email})
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )
            
            # Verify password
            if not verify_password(login_data.password, user["password_hash"]):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )
            
            # Check if user is banned or inactive
            if user.get("is_banned", False):
                ban_until = user.get("ban_until")
                if ban_until and ban_until > datetime.utcnow():
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Account is banned until {ban_until.isoformat()}"
                    )
                elif not ban_until:  # Permanent ban
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Account is permanently banned"
                    )
            
            if not user.get("is_active", True):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Account is inactive"
                )
            
            # Update last login
            await self.users_collection.update_one(
                {"id": user["id"]},
                {
                    "$set": {"last_login": datetime.utcnow()},
                    "$inc": {"pc_points": settings.pc_points_config["daily_login"]}
                }
            )
            
            # Create tokens
            token_data = {"sub": user["id"], "email": user["email"]}
            access_token = create_access_token(token_data)
            refresh_token = create_refresh_token(token_data)
            
            # Prepare user response
            user_dict = {k: v for k, v in user.items() if k != "password_hash"}
            user_dict["pc_points"] += settings.pc_points_config["daily_login"]
            
            logger.info(f"User logged in successfully: {login_data.email}")
            
            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=settings.access_token_expire_minutes * 60,
                user=user_dict
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error logging in user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error during login"
            )
    
    async def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        """Refresh access token using refresh token"""
        try:
            # Verify refresh token
            payload = verify_token(refresh_token, "refresh")
            if not payload:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )
            
            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload"
                )
            
            # Get user from database
            user = await self.users_collection.find_one({"id": user_id})
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )
            
            # Check if user is still active
            if not user.get("is_active", True) or user.get("is_banned", False):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Account is no longer active"
                )
            
            # Create new tokens
            token_data = {"sub": user["id"], "email": user["email"]}
            new_access_token = create_access_token(token_data)
            new_refresh_token = create_refresh_token(token_data)
            
            # Prepare user response
            user_dict = {k: v for k, v in user.items() if k != "password_hash"}
            
            return TokenResponse(
                access_token=new_access_token,
                refresh_token=new_refresh_token,
                expires_in=settings.access_token_expire_minutes * 60,
                user=user_dict
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error during token refresh"
            )
    
    async def get_current_user_info(self, user_id: str) -> UserResponse:
        """Get current user information"""
        try:
            user = await self.users_collection.find_one({"id": user_id})
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Remove password hash and convert to response model
            user_dict = {k: v for k, v in user.items() if k != "password_hash"}
            return UserResponse(**user_dict)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    async def validate_user_credentials(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Validate user credentials (internal use)"""
        try:
            user = await self.users_collection.find_one({"email": email})
            if user and verify_password(password, user["password_hash"]):
                return {k: v for k, v in user.items() if k != "password_hash"}
            return None
        except Exception as e:
            logger.error(f"Error validating credentials: {e}")
            return None
    
    async def check_user_exists(self, email: str = None, username: str = None) -> bool:
        """Check if user exists by email or username"""
        try:
            query = {}
            if email:
                query["email"] = email
            if username:
                query["username"] = username
            
            if not query:
                return False
                
            user = await self.users_collection.find_one(query)
            return user is not None
            
        except Exception as e:
            logger.error(f"Error checking user existence: {e}")
            return False
    
    async def update_user_rank(self, user_id: str) -> Tuple[str, bool]:
        """Update user rank based on PC points"""
        try:
            user = await self.users_collection.find_one({"id": user_id})
            if not user:
                return "Iniciante", False
            
            pc_points = user.get("pc_points", 0)
            current_rank = user.get("rank", "Iniciante")
            
            # Determine new rank
            new_rank = "Iniciante"
            for points_threshold, rank in sorted(settings.ranks_config.items(), reverse=True):
                if pc_points >= points_threshold:
                    new_rank = rank
                    break
            
            # Update rank if changed
            rank_updated = new_rank != current_rank
            if rank_updated:
                await self.users_collection.update_one(
                    {"id": user_id},
                    {"$set": {"rank": new_rank, "updated_at": datetime.utcnow()}}
                )
                logger.info(f"User {user_id} rank updated from {current_rank} to {new_rank}")
            
            return new_rank, rank_updated
            
        except Exception as e:
            logger.error(f"Error updating user rank: {e}")
            return "Iniciante", False
    
    async def award_achievement(self, user_id: str, achievement: str) -> bool:
        """Award achievement to user"""
        try:
            # Check if user already has this achievement
            user = await self.users_collection.find_one({"id": user_id})
            if not user:
                return False
            
            current_achievements = user.get("achievements", [])
            if achievement in current_achievements:
                return False  # Already has this achievement
            
            # Add achievement and award PCon points
            pcon_reward = settings.pcon_points_config.get("achievement_unlocked", 10)
            await self.users_collection.update_one(
                {"id": user_id},
                {
                    "$addToSet": {"achievements": achievement},
                    "$inc": {"pcon_points": pcon_reward},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            logger.info(f"Achievement '{achievement}' awarded to user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error awarding achievement: {e}")
            return False


# Global auth service instance
auth_service = AuthService()