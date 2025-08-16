"""
Answers Router Module
Handles all answer-related endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Path

from ..core.security import get_current_user, get_current_admin_user
from ..models.qa import AnswerCreate, AnswerUpdate, AnswerResponse
from ..models.base import MessageResponse
from ..services.qa_service import qa_service

router = APIRouter()


@router.post("/", response_model=AnswerResponse, status_code=status.HTTP_201_CREATED)
async def create_answer(
    answer_data: AnswerCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new answer"""
    try:
        result = await qa_service.create_answer(answer_data, current_user["id"])
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


@router.get("/{answer_id}", response_model=AnswerResponse)
async def get_answer(answer_id: str = Path(..., description="Answer ID")):
    """Get answer by ID"""
    try:
        result = await qa_service.get_answer_by_id(answer_id)
        return result
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Answer not found"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{answer_id}", response_model=AnswerResponse)
async def update_answer(
    answer_id: str,
    update_data: AnswerUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update an answer (only by author or admin)"""
    try:
        result = await qa_service.update_answer(answer_id, update_data, current_user["id"])
        return result
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Answer not found"
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


@router.post("/{answer_id}/accept", response_model=AnswerResponse)
async def accept_answer(
    answer_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Accept an answer (only by question author)"""
    try:
        result = await qa_service.accept_answer(answer_id, current_user["id"])
        return result
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Answer not found"
            )
        if "permission denied" in str(e).lower() or "only question author" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only question author can accept answers"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{answer_id}/validate", response_model=AnswerResponse)
async def validate_answer(
    answer_id: str,
    current_admin: dict = Depends(get_current_admin_user)
):
    """Validate an answer (admin only) - this awards points"""
    try:
        result = await qa_service.validate_answer(answer_id, current_admin["id"])
        return result
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Answer not found"
            )
        if "already validated" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Answer is already validated"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Questions-related answer endpoints
@router.get("/", response_model=List[AnswerResponse], deprecated=True)
async def get_answers():
    """
    This endpoint is deprecated. Use GET /questions/{question_id}/answers instead.
    """
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="This endpoint is deprecated. Use GET /questions/{question_id}/answers instead."
    )