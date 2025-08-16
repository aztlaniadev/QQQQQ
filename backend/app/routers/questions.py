"""
Questions Router Module
Handles all question-related endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from fastapi.responses import JSONResponse

from ..core.security import get_current_user, get_current_admin_user
from ..models.qa import (
    QuestionCreate, QuestionUpdate, QuestionResponse, QuestionDetailResponse,
    QuestionFilters, SearchQuery, AnswerResponse
)
from ..models.base import PaginatedResponse, MessageResponse
from ..services.qa_service import qa_service

router = APIRouter()


@router.post("/", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
async def create_question(
    question_data: QuestionCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new question"""
    try:
        result = await qa_service.create_question(question_data, current_user["id"])
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=PaginatedResponse)
async def get_questions(
    q: Optional[str] = Query(None, description="Search text"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    category: Optional[str] = Query(None, description="Filter by category"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty"),
    solved: Optional[bool] = Query(None, description="Filter by solved status"),
    author: Optional[str] = Query(None, description="Filter by author"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order"),
    skip: int = Query(0, ge=0, description="Skip items"),
    limit: int = Query(20, ge=1, le=100, description="Limit items")
):
    """Get questions with filters and pagination"""
    try:
        filters = QuestionFilters(
            q=q,
            tags=tags,
            category=category,
            difficulty=difficulty,
            solved=solved,
            author=author,
            sort_by=sort_by,
            sort_order=sort_order,
            skip=skip,
            limit=limit
        )
        
        result = await qa_service.get_questions(filters)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/search", response_model=PaginatedResponse)
async def search_questions(
    q: Optional[str] = Query(None, description="Search text"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    category: Optional[str] = Query(None, description="Filter by category"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty"),
    solved: Optional[bool] = Query(None, description="Filter by solved status"),
    author: Optional[str] = Query(None, description="Filter by author"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order"),
    skip: int = Query(0, ge=0, description="Skip items"),
    limit: int = Query(20, ge=1, le=100, description="Limit items")
):
    """Advanced search for questions"""
    try:
        search_query = SearchQuery(
            q=q,
            tags=tags,
            category=category,
            difficulty=difficulty,
            solved=solved,
            author=author,
            sort_by=sort_by,
            sort_order=sort_order,
            skip=skip,
            limit=limit
        )
        
        result = await qa_service.search_questions(search_query)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{question_id}", response_model=QuestionDetailResponse)
async def get_question(
    question_id: str,
    increment_views: bool = Query(True, description="Increment view count")
):
    """Get question by ID with detailed information"""
    try:
        result = await qa_service.get_question_by_id(question_id, increment_views)
        return result
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{question_id}", response_model=QuestionResponse)
async def update_question(
    question_id: str,
    update_data: QuestionUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update a question (only by author or admin)"""
    try:
        result = await qa_service.update_question(question_id, update_data, current_user["id"])
        return result
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        if "permission denied" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{question_id}", response_model=MessageResponse)
async def delete_question(
    question_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a question (only by author or admin)"""
    try:
        result = await qa_service.delete_question(question_id, current_user["id"])
        if result:
            return MessageResponse(message="Question deleted successfully")
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete question"
            )
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        if "permission denied" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{question_id}/answers", response_model=List[AnswerResponse])
async def get_question_answers(question_id: str = Path(..., description="Question ID")):
    """Get all answers for a specific question"""
    try:
        result = await qa_service.get_question_answers(question_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )