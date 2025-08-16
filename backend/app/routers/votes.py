"""
Votes Router Module
Handles voting on questions and answers
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Path, Query

from ..core.security import get_current_user
from ..models.qa import VoteCreate, VoteResponse
from ..services.qa_service import qa_service

router = APIRouter()


@router.post("/", response_model=VoteResponse)
async def vote(
    vote_data: VoteCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create or update a vote on a question or answer"""
    try:
        result = await qa_service.vote(vote_data, current_user["id"])
        return result
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{vote_data.target_type.title()} not found"
            )
        if "cannot vote" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot vote on your own content"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{target_type}/{target_id}/user-vote")
async def get_user_vote(
    target_type: str = Path(..., description="Type of target (question or answer)"),
    target_id: str = Path(..., description="ID of the target"),
    current_user: dict = Depends(get_current_user)
):
    """Get current user's vote on a specific target"""
    try:
        if target_type not in ["question", "answer"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Target type must be 'question' or 'answer'"
            )
        
        vote = await qa_service.get_user_vote(current_user["id"], target_id, target_type)
        return {
            "target_id": target_id,
            "target_type": target_type,
            "user_vote": vote
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Convenience endpoints for specific vote types
@router.post("/{target_type}/{target_id}/upvote", response_model=VoteResponse)
async def upvote(
    target_type: str = Path(..., description="Type of target (question or answer)"),
    target_id: str = Path(..., description="ID of the target"),
    current_user: dict = Depends(get_current_user)
):
    """Upvote a question or answer"""
    try:
        if target_type not in ["question", "answer"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Target type must be 'question' or 'answer'"
            )
        
        vote_data = VoteCreate(
            target_id=target_id,
            target_type=target_type,
            vote_type="upvote"
        )
        
        result = await qa_service.vote(vote_data, current_user["id"])
        return result
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{target_type.title()} not found"
            )
        if "cannot vote" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot vote on your own content"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{target_type}/{target_id}/downvote", response_model=VoteResponse)
async def downvote(
    target_type: str = Path(..., description="Type of target (question or answer)"),
    target_id: str = Path(..., description="ID of the target"),
    current_user: dict = Depends(get_current_user)
):
    """Downvote a question or answer"""
    try:
        if target_type not in ["question", "answer"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Target type must be 'question' or 'answer'"
            )
        
        vote_data = VoteCreate(
            target_id=target_id,
            target_type=target_type,
            vote_type="downvote"
        )
        
        result = await qa_service.vote(vote_data, current_user["id"])
        return result
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{target_type.title()} not found"
            )
        if "cannot vote" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot vote on your own content"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )