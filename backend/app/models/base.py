"""
Base models and common response schemas
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar('T')


class BaseResponse(BaseModel):
    """Base response model"""
    success: bool = True
    message: str = "Operation completed successfully"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = False
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response model"""
    items: List[T]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool


class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]


class MessageResponse(BaseModel):
    """Simple message response"""
    message: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0.0"
    database: str = "connected"


class StatsResponse(BaseModel):
    """Statistics response"""
    total_users: int = 0
    total_companies: int = 0
    total_questions: int = 0
    total_answers: int = 0
    pending_answers: int = 0
    total_articles: int = 0


class AdvancedStatsResponse(BaseModel):
    """Advanced statistics response"""
    basic_stats: StatsResponse
    moderation_stats: Dict[str, int]
    activity_stats: Dict[str, int]
    top_users: List[Dict[str, Any]]


class VoteResponse(BaseModel):
    """Vote response"""
    message: str
    vote_type: str
    target_id: str
    target_type: str
    new_score: int


class PointsResponse(BaseModel):
    """Points calculation response"""
    pc_points_awarded: int
    pcon_points_awarded: int
    total_pc_points: int
    total_pcon_points: int
    rank_updated: bool
    new_rank: Optional[str] = None
    achievements_unlocked: List[str] = []