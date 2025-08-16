"""
Q&A System models (Questions, Answers, Votes)
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from ..core.security import generate_unique_id


class QuestionCreate(BaseModel):
    """Question creation model"""
    title: str = Field(..., min_length=10, max_length=200)
    content: str = Field(..., min_length=20, max_length=10000)
    tags: List[str] = Field(..., min_items=1, max_items=5)
    category: Optional[str] = Field(None, max_length=50)
    difficulty: Optional[str] = Field(None, pattern=r'^(beginner|intermediate|advanced|expert)$')
    
    @validator('tags')
    def validate_tags(cls, v):
        cleaned_tags = []
        for tag in v:
            tag = tag.strip().lower()
            if tag and len(tag) >= 2 and len(tag) <= 30:
                cleaned_tags.append(tag)
        if not cleaned_tags:
            raise ValueError('At least one valid tag is required')
        return cleaned_tags[:5]  # Max 5 tags
    
    @validator('title')
    def validate_title(cls, v):
        # Remove extra whitespace
        return ' '.join(v.split())


class QuestionUpdate(BaseModel):
    """Question update model"""
    title: Optional[str] = Field(None, min_length=10, max_length=200)
    content: Optional[str] = Field(None, min_length=20, max_length=10000)
    tags: Optional[List[str]] = Field(None, min_items=1, max_items=5)
    category: Optional[str] = Field(None, max_length=50)
    difficulty: Optional[str] = Field(None, pattern=r'^(beginner|intermediate|advanced|expert)$')
    
    @validator('tags')
    def validate_tags(cls, v):
        if v is None:
            return v
        cleaned_tags = []
        for tag in v:
            tag = tag.strip().lower()
            if tag and len(tag) >= 2 and len(tag) <= 30:
                cleaned_tags.append(tag)
        if not cleaned_tags:
            raise ValueError('At least one valid tag is required')
        return cleaned_tags[:5]


class QuestionResponse(BaseModel):
    """Question response model"""
    id: str
    title: str
    content: str
    author_id: str
    author_username: str
    author_rank: str
    tags: List[str]
    category: Optional[str] = None
    difficulty: Optional[str] = None
    views: int = 0
    upvotes: int = 0
    downvotes: int = 0
    score: int = 0
    answers_count: int = 0
    is_solved: bool = False
    accepted_answer_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # User-specific fields (filled if user is authenticated)
    user_vote: Optional[str] = None  # "up", "down", or None


class QuestionDetailResponse(QuestionResponse):
    """Detailed question response with answers"""
    answers: List["AnswerResponse"] = []
    
    class Config:
        # Enable forward references for answers
        arbitrary_types_allowed = True


class AnswerCreate(BaseModel):
    """Answer creation model"""
    content: str = Field(..., min_length=20, max_length=10000)
    question_id: str
    
    @validator('content')
    def validate_content(cls, v):
        # Remove extra whitespace but preserve line breaks
        return '\n'.join(' '.join(line.split()) for line in v.split('\n'))


class AnswerUpdate(BaseModel):
    """Answer update model"""
    content: str = Field(..., min_length=20, max_length=10000)
    
    @validator('content')
    def validate_content(cls, v):
        return '\n'.join(' '.join(line.split()) for line in v.split('\n'))


class AnswerResponse(BaseModel):
    """Answer response model"""
    id: str
    content: str
    question_id: str
    author_id: str
    author_username: str
    author_rank: str
    upvotes: int = 0
    downvotes: int = 0
    score: int = 0
    is_accepted: bool = False
    is_validated: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # User-specific fields
    user_vote: Optional[str] = None  # "up", "down", or None


class VoteCreate(BaseModel):
    """Vote creation model"""
    target_id: str
    target_type: str = Field(..., pattern=r'^(question|answer)$')
    vote_type: str = Field(..., pattern=r'^(upvote|downvote|up|down)$')
    
    @validator('vote_type')
    def normalize_vote_type(cls, v):
        # Normalize vote types
        if v in ['upvote', 'up']:
            return 'up'
        elif v in ['downvote', 'down']:
            return 'down'
        return v


class VoteResponse(BaseModel):
    """Vote response model"""
    message: str
    vote_type: str
    target_id: str
    target_type: str
    new_score: int
    user_previous_vote: Optional[str] = None


class Question(BaseModel):
    """Full question model for database storage"""
    id: str = Field(default_factory=generate_unique_id)
    title: str
    content: str
    author_id: str
    tags: List[str]
    category: Optional[str] = None
    difficulty: Optional[str] = None
    views: int = 0
    upvotes: int = 0
    downvotes: int = 0
    answers_count: int = 0
    is_solved: bool = False
    accepted_answer_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    # Moderation
    is_flagged: bool = False
    flag_reason: Optional[str] = None
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[str] = None
    
    @property
    def score(self) -> int:
        """Calculate question score"""
        return self.upvotes - self.downvotes


class Answer(BaseModel):
    """Full answer model for database storage"""
    id: str = Field(default_factory=generate_unique_id)
    content: str
    question_id: str
    author_id: str
    upvotes: int = 0
    downvotes: int = 0
    is_accepted: bool = False
    is_validated: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    # Moderation
    is_flagged: bool = False
    flag_reason: Optional[str] = None
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[str] = None
    
    @property
    def score(self) -> int:
        """Calculate answer score"""
        return self.upvotes - self.downvotes


class Vote(BaseModel):
    """Full vote model for database storage"""
    id: str = Field(default_factory=generate_unique_id)
    user_id: str
    target_id: str
    target_type: str  # "question" or "answer"
    vote_type: str    # "up" or "down"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


class SearchQuery(BaseModel):
    """Search query model"""
    q: Optional[str] = Field(None, max_length=200)  # Search text
    tags: Optional[List[str]] = Field(None, max_items=5)
    category: Optional[str] = Field(None, max_length=50)
    difficulty: Optional[str] = Field(None, pattern=r'^(beginner|intermediate|advanced|expert)$')
    solved: Optional[bool] = None
    author: Optional[str] = Field(None, max_length=50)
    sort_by: str = Field("created_at", pattern=r'^(created_at|updated_at|views|score|answers_count)$')
    sort_order: str = Field("desc", pattern=r'^(asc|desc)$')
    skip: int = Field(0, ge=0)
    limit: int = Field(20, ge=1, le=100)


class QuestionFilters(BaseModel):
    """Question filtering options"""
    tags: Optional[List[str]] = None
    category: Optional[str] = None
    difficulty: Optional[str] = None
    is_solved: Optional[bool] = None
    author_id: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    min_score: Optional[int] = None
    max_score: Optional[int] = None
    has_accepted_answer: Optional[bool] = None


class QAStats(BaseModel):
    """Q&A Statistics model"""
    total_questions: int = 0
    total_answers: int = 0
    solved_questions: int = 0
    unsolved_questions: int = 0
    avg_answers_per_question: float = 0.0
    total_votes: int = 0
    most_used_tags: List[Dict[str, Any]] = []
    top_contributors: List[Dict[str, Any]] = []


# Forward reference resolution
QuestionDetailResponse.model_rebuild()