"""
Security utilities for authentication and authorization
"""
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from .config import settings
from .database import get_users_collection

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Bearer token
security = HTTPBearer()


def hash_password(password: str) -> str:
    """Hash a password for storing in database"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create a JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        
        # Check token type
        if payload.get("type") != token_type:
            return None
            
        # Check expiration
        exp = payload.get("exp")
        if exp is None:
            return None
            
        if datetime.utcnow() > datetime.fromtimestamp(exp):
            return None
            
        return payload
        
    except JWTError:
        return None


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current authenticated user"""
    token = credentials.credentials
    
    # Verify token
    payload = verify_token(token, "access")
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    users_collection = get_users_collection()
    user = await users_collection.find_one({"id": user_id})
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is banned or inactive
    if user.get("is_banned", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is banned"
        )
    
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Remove sensitive data
    user_data = {k: v for k, v in user.items() if k != "password_hash"}
    return user_data


async def get_current_admin_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Get current authenticated admin user"""
    if not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def get_current_active_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Get current authenticated and active user"""
    if not current_user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def generate_unique_id() -> str:
    """Generate a unique ID for entities"""
    return secrets.token_urlsafe(16)


def generate_reset_token() -> str:
    """Generate a password reset token"""
    return secrets.token_urlsafe(32)


def simple_hash(data: str) -> str:
    """Simple hash function for non-sensitive data"""
    return hashlib.sha256(data.encode()).hexdigest()


class PermissionChecker:
    """Check user permissions for various actions"""
    
    @staticmethod
    def can_edit_question(user: Dict[str, Any], question: Dict[str, Any]) -> bool:
        """Check if user can edit a question"""
        return (
            user.get("is_admin", False) or 
            user.get("id") == question.get("author_id")
        )
    
    @staticmethod
    def can_delete_question(user: Dict[str, Any], question: Dict[str, Any]) -> bool:
        """Check if user can delete a question"""
        return (
            user.get("is_admin", False) or 
            user.get("id") == question.get("author_id")
        )
    
    @staticmethod
    def can_edit_answer(user: Dict[str, Any], answer: Dict[str, Any]) -> bool:
        """Check if user can edit an answer"""
        return (
            user.get("is_admin", False) or 
            user.get("id") == answer.get("author_id")
        )
    
    @staticmethod
    def can_accept_answer(user: Dict[str, Any], question: Dict[str, Any]) -> bool:
        """Check if user can accept an answer"""
        return (
            user.get("is_admin", False) or 
            user.get("id") == question.get("author_id")
        )
    
    @staticmethod
    def can_validate_answer(user: Dict[str, Any]) -> bool:
        """Check if user can validate answers"""
        return user.get("is_admin", False)
    
    @staticmethod
    def can_moderate_content(user: Dict[str, Any]) -> bool:
        """Check if user can moderate content"""
        return user.get("is_admin", False)
    
    @staticmethod
    def can_write_articles(user: Dict[str, Any]) -> bool:
        """Check if user can write articles"""
        rank = user.get("rank", "Iniciante")
        return rank in ["Mestre", "Guru"] or user.get("is_admin", False)


# Permission checker instance
permissions = PermissionChecker()