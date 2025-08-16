"""
User and Company models
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field, validator
from ..core.security import generate_unique_id


class UserCreate(BaseModel):
    """User creation model"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    
    @validator('username')
    def validate_username(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, underscores and hyphens')
        return v.lower()
    
    @validator('password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserLogin(BaseModel):
    """User login model"""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """User update model"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    bio: Optional[str] = Field(None, max_length=500)
    location: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=200)
    github: Optional[str] = Field(None, max_length=100)
    linkedin: Optional[str] = Field(None, max_length=100)
    skills: Optional[List[str]] = Field(None, max_items=20)
    theme_color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    custom_title: Optional[str] = Field(None, max_length=100)
    banner_image: Optional[str] = Field(None, max_length=500)
    
    @validator('skills')
    def validate_skills(cls, v):
        if v:
            return [skill.strip() for skill in v if skill.strip()]
        return v


class UserResponse(BaseModel):
    """User response model"""
    id: str
    username: str
    email: str
    pc_points: int = 0
    pcon_points: int = 0
    rank: str = "Iniciante"
    is_admin: bool = False
    is_company: bool = False
    is_active: bool = True
    is_banned: bool = False
    is_muted: bool = False
    is_silenced: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    github: Optional[str] = None
    linkedin: Optional[str] = None
    skills: List[str] = []
    theme_color: str = "#D97745"
    custom_title: Optional[str] = None
    banner_image: Optional[str] = None
    achievements: List[str] = []
    following: List[str] = []
    followers: List[str] = []
    questions_count: int = 0
    answers_count: int = 0
    accepted_answers_count: int = 0


class UserStats(BaseModel):
    """User statistics model"""
    total_questions: int = 0
    total_answers: int = 0
    accepted_answers: int = 0
    total_upvotes_received: int = 0
    total_downvotes_received: int = 0
    total_votes_given: int = 0
    pc_points: int = 0
    pcon_points: int = 0
    rank: str = "Iniciante"
    achievements: List[str] = []
    join_date: datetime
    last_activity: Optional[datetime] = None
    questions_solved: int = 0
    reputation_score: int = 0


class CompanyCreate(BaseModel):
    """Company creation model"""
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    website: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    size: Optional[str] = Field(None, pattern=r'^(1-10|11-50|51-200|201-1000|1000\+)$')
    industry: Optional[str] = Field(None, max_length=100)


class CompanyUpdate(BaseModel):
    """Company update model"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    website: Optional[str] = Field(None, max_length=200)
    size: Optional[str] = Field(None, pattern=r'^(1-10|11-50|51-200|201-1000|1000\+)$')
    industry: Optional[str] = Field(None, max_length=100)
    logo_url: Optional[str] = Field(None, max_length=500)


class CompanyResponse(BaseModel):
    """Company response model"""
    id: str
    name: str
    email: str
    website: Optional[str] = None
    description: Optional[str] = None
    size: Optional[str] = None
    industry: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: bool = True
    is_banned: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    jobs_posted: int = 0
    verified: bool = False


class UserModerationAction(BaseModel):
    """User moderation action model"""
    action: str = Field(..., pattern=r'^(ban|unban|mute|unmute|silence|unsilence)$')
    reason: Optional[str] = Field(None, max_length=500)
    duration_hours: Optional[int] = Field(None, ge=1, le=8760)  # Max 1 year


class BotUserCreate(BaseModel):
    """Bot user creation model"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    description: str = Field(..., max_length=500)
    auto_answer: bool = False
    source_api: Optional[str] = Field(None, max_length=200)
    
    @validator('username')
    def validate_bot_username(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, underscores and hyphens')
        if not v.endswith('_bot'):
            v = f"{v}_bot"
        return v.lower()


class User(BaseModel):
    """Full user model for database storage"""
    id: str = Field(default_factory=generate_unique_id)
    username: str
    email: str
    password_hash: str
    pc_points: int = 0
    pcon_points: int = 0
    rank: str = "Iniciante"
    is_admin: bool = False
    is_company: bool = False
    is_active: bool = True
    is_banned: bool = False
    is_muted: bool = False
    is_silenced: bool = False
    is_bot: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    github: Optional[str] = None
    linkedin: Optional[str] = None
    skills: List[str] = []
    theme_color: str = "#D97745"
    custom_title: Optional[str] = None
    banner_image: Optional[str] = None
    achievements: List[str] = []
    following: List[str] = []
    followers: List[str] = []
    questions_count: int = 0
    answers_count: int = 0
    accepted_answers_count: int = 0
    
    # Bot specific fields
    bot_description: Optional[str] = None
    bot_auto_answer: bool = False
    bot_source_api: Optional[str] = None
    
    # Moderation fields
    ban_reason: Optional[str] = None
    ban_until: Optional[datetime] = None
    mute_reason: Optional[str] = None
    mute_until: Optional[datetime] = None
    silence_reason: Optional[str] = None
    silence_until: Optional[datetime] = None


class Company(BaseModel):
    """Full company model for database storage"""
    id: str = Field(default_factory=generate_unique_id)
    name: str
    email: str
    password_hash: str
    website: Optional[str] = None
    description: Optional[str] = None
    size: Optional[str] = None
    industry: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: bool = True
    is_banned: bool = False
    is_verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    jobs_posted: int = 0
    
    # Moderation fields
    ban_reason: Optional[str] = None
    ban_until: Optional[datetime] = None