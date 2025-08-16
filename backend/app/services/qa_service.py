"""
Q&A Service Module
Handles all business logic for questions, answers, and voting system
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timezone
from bson import ObjectId
from pymongo import ASCENDING, DESCENDING
import logging

from ..core.database import get_questions_collection, get_answers_collection, get_votes_collection, get_users_collection
from ..core.security import generate_unique_id
from ..models.qa import (
    QuestionCreate, QuestionUpdate, QuestionResponse, QuestionDetailResponse,
    AnswerCreate, AnswerUpdate, AnswerResponse, 
    VoteCreate, VoteResponse,
    SearchQuery, QuestionFilters, QAStats,
    Question, Answer, Vote
)
from ..models.base import PaginatedResponse
from .gamification_service import gamification_service

logger = logging.getLogger(__name__)


class QAService:
    """Q&A service class for questions, answers, and voting"""
    
    def __init__(self):
        self._questions_collection = None
        self._answers_collection = None
        self._votes_collection = None
        self._users_collection = None
    
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
    
    @property
    def users_collection(self):
        """Lazy load users collection"""
        if self._users_collection is None:
            self._users_collection = get_users_collection()
        return self._users_collection

    # ===========================================
    # QUESTIONS CRUD
    # ===========================================

    async def create_question(self, question_data: QuestionCreate, author_id: str) -> QuestionResponse:
        """Create a new question"""
        try:
            # Prepare question document
            question_doc = {
                "id": generate_unique_id(),
                "title": question_data.title,
                "content": question_data.content,
                "author_id": author_id,
                "tags": question_data.tags,
                "category": question_data.category,
                "difficulty": question_data.difficulty,
                "views": 0,
                "upvotes": 0,
                "downvotes": 0,
                "score": 0,
                "answers_count": 0,
                "is_solved": False,
                "accepted_answer_id": None,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            
            # Insert question
            await self.questions_collection.insert_one(question_doc)
            
            # Award points for creating question
            await gamification_service.award_points(
                user_id=author_id,
                action="question_created",
                target_id=question_doc["id"],
                target_type="question"
            )
            
            logger.info(f"Question created: {question_doc['id']} by user {author_id}")
            
            # Get author info for response
            author = await self.users_collection.find_one({"id": author_id})
            author_info = {
                "id": author["id"],
                "username": author.get("username"),
                "avatar_url": author.get("avatar_url")
            } if author else {"id": author_id, "username": "Unknown"}
            
            return QuestionResponse(
                **question_doc,
                author=author_info
            )
            
        except Exception as e:
            logger.error(f"Error creating question: {str(e)}")
            raise Exception(f"Failed to create question: {str(e)}")

    async def get_questions(self, filters: QuestionFilters) -> PaginatedResponse:
        """Get questions with filters and pagination"""
        try:
            # Build MongoDB query
            query = {}
            
            # Text search
            if filters.q:
                query["$or"] = [
                    {"title": {"$regex": filters.q, "$options": "i"}},
                    {"content": {"$regex": filters.q, "$options": "i"}},
                    {"tags": {"$in": [filters.q]}}
                ]
            
            # Tags filter
            if filters.tags:
                query["tags"] = {"$in": filters.tags}
            
            # Category filter
            if filters.category:
                query["category"] = filters.category
            
            # Difficulty filter
            if filters.difficulty:
                query["difficulty"] = filters.difficulty
            
            # Solved status
            if filters.solved is not None:
                query["is_solved"] = filters.solved
            
            # Author filter
            if filters.author:
                query["author_id"] = filters.author
            
            # Count total for pagination
            total = await self.questions_collection.count_documents(query)
            
            # Build sort criteria
            sort_field = filters.sort_by
            sort_direction = DESCENDING if filters.sort_order == "desc" else ASCENDING
            
            # Execute query with pagination
            cursor = self.questions_collection.find(query).sort(sort_field, sort_direction).skip(filters.skip).limit(filters.limit)
            questions = await cursor.to_list(length=None)
            
            # Enrich with author information
            enriched_questions = []
            for question in questions:
                author = await self.users_collection.find_one({"id": question["author_id"]})
                author_info = {
                    "id": author["id"],
                    "username": author.get("username"),
                    "avatar_url": author.get("avatar_url")
                } if author else {"id": question["author_id"], "username": "Unknown"}
                
                enriched_questions.append(QuestionResponse(
                    **question,
                    author=author_info
                ))
            
            return PaginatedResponse(
                items=enriched_questions,
                total=total,
                page=filters.skip // filters.limit + 1,
                pages=(total + filters.limit - 1) // filters.limit,
                limit=filters.limit
            )
            
        except Exception as e:
            logger.error(f"Error getting questions: {str(e)}")
            raise Exception(f"Failed to get questions: {str(e)}")

    async def get_question_by_id(self, question_id: str, increment_views: bool = True) -> QuestionDetailResponse:
        """Get question by ID with detailed information"""
        try:
            # Get question
            question = await self.questions_collection.find_one({"id": question_id})
            if not question:
                raise Exception("Question not found")
            
            # Increment views if requested
            if increment_views:
                await self.questions_collection.update_one(
                    {"id": question_id},
                    {"$inc": {"views": 1}, "$set": {"updated_at": datetime.now(timezone.utc)}}
                )
                question["views"] += 1
            
            # Get author info
            author = await self.users_collection.find_one({"id": question["author_id"]})
            author_info = {
                "id": author["id"],
                "username": author.get("username"),
                "avatar_url": author.get("avatar_url")
            } if author else {"id": question["author_id"], "username": "Unknown"}
            
            # Get answers
            answers = await self.get_question_answers(question_id)
            
            return QuestionDetailResponse(
                **question,
                author=author_info,
                answers=answers
            )
            
        except Exception as e:
            logger.error(f"Error getting question {question_id}: {str(e)}")
            raise Exception(f"Failed to get question: {str(e)}")

    async def update_question(self, question_id: str, update_data: QuestionUpdate, user_id: str) -> QuestionResponse:
        """Update a question (only by author or admin)"""
        try:
            # Check if question exists and user has permission
            question = await self.questions_collection.find_one({"id": question_id})
            if not question:
                raise Exception("Question not found")
            
            # Check permission (author or admin)
            user = await self.users_collection.find_one({"id": user_id})
            if question["author_id"] != user_id and not user.get("is_admin", False):
                raise Exception("Permission denied")
            
            # Prepare update data
            update_doc = {"updated_at": datetime.now(timezone.utc)}
            
            if update_data.title is not None:
                update_doc["title"] = update_data.title
            if update_data.content is not None:
                update_doc["content"] = update_data.content
            if update_data.tags is not None:
                update_doc["tags"] = update_data.tags
            if update_data.category is not None:
                update_doc["category"] = update_data.category
            if update_data.difficulty is not None:
                update_doc["difficulty"] = update_data.difficulty
            
            # Update question
            await self.questions_collection.update_one(
                {"id": question_id},
                {"$set": update_doc}
            )
            
            # Get updated question
            updated_question = await self.questions_collection.find_one({"id": question_id})
            
            # Get author info
            author = await self.users_collection.find_one({"id": updated_question["author_id"]})
            author_info = {
                "id": author["id"],
                "username": author.get("username"),
                "avatar_url": author.get("avatar_url")
            } if author else {"id": updated_question["author_id"], "username": "Unknown"}
            
            logger.info(f"Question updated: {question_id} by user {user_id}")
            
            return QuestionResponse(
                **updated_question,
                author=author_info
            )
            
        except Exception as e:
            logger.error(f"Error updating question {question_id}: {str(e)}")
            raise Exception(f"Failed to update question: {str(e)}")

    async def delete_question(self, question_id: str, user_id: str) -> bool:
        """Delete a question (only by author or admin)"""
        try:
            # Check if question exists and user has permission
            question = await self.questions_collection.find_one({"id": question_id})
            if not question:
                raise Exception("Question not found")
            
            # Check permission (author or admin)
            user = await self.users_collection.find_one({"id": user_id})
            if question["author_id"] != user_id and not user.get("is_admin", False):
                raise Exception("Permission denied")
            
            # Delete associated answers and votes
            await self.answers_collection.delete_many({"question_id": question_id})
            await self.votes_collection.delete_many({"target_id": question_id, "target_type": "question"})
            
            # Delete question
            result = await self.questions_collection.delete_one({"id": question_id})
            
            logger.info(f"Question deleted: {question_id} by user {user_id}")
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Error deleting question {question_id}: {str(e)}")
            raise Exception(f"Failed to delete question: {str(e)}")

    # ===========================================
    # ANSWERS CRUD
    # ===========================================

    async def create_answer(self, answer_data: AnswerCreate, author_id: str) -> AnswerResponse:
        """Create a new answer"""
        try:
            # Check if question exists
            question = await self.questions_collection.find_one({"id": answer_data.question_id})
            if not question:
                raise Exception("Question not found")
            
            # Prepare answer document
            answer_doc = {
                "id": generate_unique_id(),
                "question_id": answer_data.question_id,
                "author_id": author_id,
                "content": answer_data.content,
                "upvotes": 0,
                "downvotes": 0,
                "score": 0,
                "is_accepted": False,
                "is_validated": False,  # Requires admin validation
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            
            # Insert answer
            await self.answers_collection.insert_one(answer_doc)
            
            # Update question answers count
            await self.questions_collection.update_one(
                {"id": answer_data.question_id},
                {"$inc": {"answers_count": 1}, "$set": {"updated_at": datetime.now(timezone.utc)}}
            )
            
            # Note: Points are NOT awarded immediately - requires admin validation
            
            logger.info(f"Answer created: {answer_doc['id']} by user {author_id}")
            
            # Get author info for response
            author = await self.users_collection.find_one({"id": author_id})
            author_info = {
                "id": author["id"],
                "username": author.get("username"),
                "avatar_url": author.get("avatar_url")
            } if author else {"id": author_id, "username": "Unknown"}
            
            return AnswerResponse(
                **answer_doc,
                author=author_info
            )
            
        except Exception as e:
            logger.error(f"Error creating answer: {str(e)}")
            raise Exception(f"Failed to create answer: {str(e)}")

    async def get_question_answers(self, question_id: str) -> List[AnswerResponse]:
        """Get all answers for a question"""
        try:
            # Get answers sorted by score and creation date
            cursor = self.answers_collection.find({"question_id": question_id}).sort([("score", DESCENDING), ("created_at", ASCENDING)])
            answers = await cursor.to_list(length=None)
            
            # Enrich with author information
            enriched_answers = []
            for answer in answers:
                author = await self.users_collection.find_one({"id": answer["author_id"]})
                author_info = {
                    "id": author["id"],
                    "username": author.get("username"),
                    "avatar_url": author.get("avatar_url")
                } if author else {"id": answer["author_id"], "username": "Unknown"}
                
                enriched_answers.append(AnswerResponse(
                    **answer,
                    author=author_info
                ))
            
            return enriched_answers
            
        except Exception as e:
            logger.error(f"Error getting answers for question {question_id}: {str(e)}")
            raise Exception(f"Failed to get answers: {str(e)}")

    async def get_answer_by_id(self, answer_id: str) -> AnswerResponse:
        """Get answer by ID"""
        try:
            answer = await self.answers_collection.find_one({"id": answer_id})
            if not answer:
                raise Exception("Answer not found")
            
            # Get author info
            author = await self.users_collection.find_one({"id": answer["author_id"]})
            author_info = {
                "id": author["id"],
                "username": author.get("username"),
                "avatar_url": author.get("avatar_url")
            } if author else {"id": answer["author_id"], "username": "Unknown"}
            
            return AnswerResponse(
                **answer,
                author=author_info
            )
            
        except Exception as e:
            logger.error(f"Error getting answer {answer_id}: {str(e)}")
            raise Exception(f"Failed to get answer: {str(e)}")

    async def update_answer(self, answer_id: str, update_data: AnswerUpdate, user_id: str) -> AnswerResponse:
        """Update an answer (only by author or admin)"""
        try:
            # Check if answer exists and user has permission
            answer = await self.answers_collection.find_one({"id": answer_id})
            if not answer:
                raise Exception("Answer not found")
            
            # Check permission (author or admin)
            user = await self.users_collection.find_one({"id": user_id})
            if answer["author_id"] != user_id and not user.get("is_admin", False):
                raise Exception("Permission denied")
            
            # Prepare update data
            update_doc = {"updated_at": datetime.now(timezone.utc)}
            
            if update_data.content is not None:
                update_doc["content"] = update_data.content
            
            # Update answer
            await self.answers_collection.update_one(
                {"id": answer_id},
                {"$set": update_doc}
            )
            
            # Get updated answer
            updated_answer = await self.answers_collection.find_one({"id": answer_id})
            
            # Get author info
            author = await self.users_collection.find_one({"id": updated_answer["author_id"]})
            author_info = {
                "id": author["id"],
                "username": author.get("username"),
                "avatar_url": author.get("avatar_url")
            } if author else {"id": updated_answer["author_id"], "username": "Unknown"}
            
            logger.info(f"Answer updated: {answer_id} by user {user_id}")
            
            return AnswerResponse(
                **updated_answer,
                author=author_info
            )
            
        except Exception as e:
            logger.error(f"Error updating answer {answer_id}: {str(e)}")
            raise Exception(f"Failed to update answer: {str(e)}")

    async def accept_answer(self, answer_id: str, user_id: str) -> AnswerResponse:
        """Accept an answer (only by question author)"""
        try:
            # Get answer and question
            answer = await self.answers_collection.find_one({"id": answer_id})
            if not answer:
                raise Exception("Answer not found")
            
            question = await self.questions_collection.find_one({"id": answer["question_id"]})
            if not question:
                raise Exception("Question not found")
            
            # Check permission (only question author can accept)
            if question["author_id"] != user_id:
                raise Exception("Only question author can accept answers")
            
            # Unaccept previous accepted answer if exists
            if question.get("accepted_answer_id"):
                await self.answers_collection.update_one(
                    {"id": question["accepted_answer_id"]},
                    {"$set": {"is_accepted": False, "updated_at": datetime.now(timezone.utc)}}
                )
            
            # Accept this answer
            await self.answers_collection.update_one(
                {"id": answer_id},
                {"$set": {"is_accepted": True, "updated_at": datetime.now(timezone.utc)}}
            )
            
            # Update question with accepted answer
            await self.questions_collection.update_one(
                {"id": answer["question_id"]},
                {"$set": {
                    "accepted_answer_id": answer_id,
                    "is_solved": True,
                    "updated_at": datetime.now(timezone.utc)
                }}
            )
            
            # Award points for accepted answer
            await gamification_service.award_points(
                user_id=answer["author_id"],
                action="answer_accepted",
                target_id=answer_id,
                target_type="answer"
            )
            
            logger.info(f"Answer accepted: {answer_id} by user {user_id}")
            
            # Return updated answer
            updated_answer = await self.answers_collection.find_one({"id": answer_id})
            author = await self.users_collection.find_one({"id": updated_answer["author_id"]})
            author_info = {
                "id": author["id"],
                "username": author.get("username"),
                "avatar_url": author.get("avatar_url")
            } if author else {"id": updated_answer["author_id"], "username": "Unknown"}
            
            return AnswerResponse(
                **updated_answer,
                author=author_info
            )
            
        except Exception as e:
            logger.error(f"Error accepting answer {answer_id}: {str(e)}")
            raise Exception(f"Failed to accept answer: {str(e)}")

    async def validate_answer(self, answer_id: str, user_id: str) -> AnswerResponse:
        """Validate an answer (admin only) - this awards points"""
        try:
            # Check if user is admin
            user = await self.users_collection.find_one({"id": user_id})
            if not user.get("is_admin", False):
                raise Exception("Only admins can validate answers")
            
            # Get answer
            answer = await self.answers_collection.find_one({"id": answer_id})
            if not answer:
                raise Exception("Answer not found")
            
            if answer.get("is_validated", False):
                raise Exception("Answer is already validated")
            
            # Validate answer
            await self.answers_collection.update_one(
                {"id": answer_id},
                {"$set": {"is_validated": True, "updated_at": datetime.now(timezone.utc)}}
            )
            
            # Award points for validated answer
            await gamification_service.award_points(
                user_id=answer["author_id"],
                action="answer_created",
                target_id=answer_id,
                target_type="answer"
            )
            
            logger.info(f"Answer validated: {answer_id} by admin {user_id}")
            
            # Return updated answer
            updated_answer = await self.answers_collection.find_one({"id": answer_id})
            author = await self.users_collection.find_one({"id": updated_answer["author_id"]})
            author_info = {
                "id": author["id"],
                "username": author.get("username"),
                "avatar_url": author.get("avatar_url")
            } if author else {"id": updated_answer["author_id"], "username": "Unknown"}
            
            return AnswerResponse(
                **updated_answer,
                author=author_info
            )
            
        except Exception as e:
            logger.error(f"Error validating answer {answer_id}: {str(e)}")
            raise Exception(f"Failed to validate answer: {str(e)}")

    # ===========================================
    # VOTING SYSTEM
    # ===========================================

    async def vote(self, vote_data: VoteCreate, user_id: str) -> VoteResponse:
        """Create or update a vote"""
        try:
            # Normalize vote type
            vote_type = "upvote" if vote_data.vote_type in ["upvote", "up"] else "downvote"
            
            # Check target exists
            if vote_data.target_type == "question":
                target = await self.questions_collection.find_one({"id": vote_data.target_id})
                collection = self.questions_collection
            elif vote_data.target_type == "answer":
                target = await self.answers_collection.find_one({"id": vote_data.target_id})
                collection = self.answers_collection
            else:
                raise Exception("Invalid target type")
            
            if not target:
                raise Exception(f"{vote_data.target_type.title()} not found")
            
            # Prevent self-voting
            if target["author_id"] == user_id:
                raise Exception("Cannot vote on your own content")
            
            # Check existing vote
            existing_vote = await self.votes_collection.find_one({
                "user_id": user_id,
                "target_id": vote_data.target_id,
                "target_type": vote_data.target_type
            })
            
            vote_changes = {"upvotes": 0, "downvotes": 0}
            
            if existing_vote:
                # Remove old vote effects
                if existing_vote["vote_type"] == "upvote":
                    vote_changes["upvotes"] -= 1
                else:
                    vote_changes["downvotes"] -= 1
                
                # Same vote type = remove vote
                if existing_vote["vote_type"] == vote_type:
                    await self.votes_collection.delete_one({"_id": existing_vote["_id"]})
                    logger.info(f"Vote removed: {vote_data.target_type} {vote_data.target_id} by user {user_id}")
                else:
                    # Different vote type = update vote
                    await self.votes_collection.update_one(
                        {"_id": existing_vote["_id"]},
                        {"$set": {
                            "vote_type": vote_type,
                            "created_at": datetime.now(timezone.utc)
                        }}
                    )
                    
                    # Add new vote effects
                    if vote_type == "upvote":
                        vote_changes["upvotes"] += 1
                    else:
                        vote_changes["downvotes"] += 1
                    
                    logger.info(f"Vote updated: {vote_data.target_type} {vote_data.target_id} to {vote_type} by user {user_id}")
            else:
                # Create new vote
                vote_doc = {
                    "id": generate_unique_id(),
                    "user_id": user_id,
                    "target_id": vote_data.target_id,
                    "target_type": vote_data.target_type,
                    "vote_type": vote_type,
                    "created_at": datetime.now(timezone.utc)
                }
                
                await self.votes_collection.insert_one(vote_doc)
                
                # Add vote effects
                if vote_type == "upvote":
                    vote_changes["upvotes"] += 1
                else:
                    vote_changes["downvotes"] += 1
                
                logger.info(f"Vote created: {vote_data.target_type} {vote_data.target_id} {vote_type} by user {user_id}")
            
            # Update target vote counts
            score_change = vote_changes["upvotes"] - vote_changes["downvotes"]
            await collection.update_one(
                {"id": vote_data.target_id},
                {
                    "$inc": {
                        "upvotes": vote_changes["upvotes"],
                        "downvotes": vote_changes["downvotes"],
                        "score": score_change
                    },
                    "$set": {"updated_at": datetime.now(timezone.utc)}
                }
            )
            
            # Award/deduct points for voting
            if vote_changes["upvotes"] > 0:
                await gamification_service.award_points(
                    user_id=target["author_id"],
                    action="received_upvote",
                    target_id=vote_data.target_id,
                    target_type=vote_data.target_type
                )
            elif vote_changes["downvotes"] > 0:
                await gamification_service.award_points(
                    user_id=target["author_id"],
                    action="received_downvote",
                    target_id=vote_data.target_id,
                    target_type=vote_data.target_type
                )
            
            # Get current vote state
            current_vote = await self.votes_collection.find_one({
                "user_id": user_id,
                "target_id": vote_data.target_id,
                "target_type": vote_data.target_type
            })
            
            # Get updated target with new vote counts
            updated_target = await collection.find_one({"id": vote_data.target_id})
            
            return VoteResponse(
                target_id=vote_data.target_id,
                target_type=vote_data.target_type,
                user_vote=current_vote["vote_type"] if current_vote else None,
                upvotes=updated_target["upvotes"],
                downvotes=updated_target["downvotes"],
                score=updated_target["score"]
            )
            
        except Exception as e:
            logger.error(f"Error voting: {str(e)}")
            raise Exception(f"Failed to vote: {str(e)}")

    async def get_user_vote(self, user_id: str, target_id: str, target_type: str) -> Optional[str]:
        """Get user's vote on a target"""
        try:
            vote = await self.votes_collection.find_one({
                "user_id": user_id,
                "target_id": target_id,
                "target_type": target_type
            })
            
            return vote["vote_type"] if vote else None
            
        except Exception as e:
            logger.error(f"Error getting user vote: {str(e)}")
            return None

    # ===========================================
    # STATISTICS AND ANALYTICS
    # ===========================================

    async def get_qa_stats(self) -> QAStats:
        """Get Q&A statistics"""
        try:
            # Basic counts
            total_questions = await self.questions_collection.count_documents({})
            total_answers = await self.answers_collection.count_documents({})
            total_votes = await self.votes_collection.count_documents({})
            
            # Advanced stats
            solved_questions = await self.questions_collection.count_documents({"is_solved": True})
            pending_answers = await self.answers_collection.count_documents({"is_validated": False})
            
            # Top tags
            pipeline = [
                {"$unwind": "$tags"},
                {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 10}
            ]
            top_tags_cursor = self.questions_collection.aggregate(pipeline)
            top_tags = [{"tag": doc["_id"], "count": doc["count"]} async for doc in top_tags_cursor]
            
            # Recent activity (last 7 days)
            from datetime import timedelta
            week_ago = datetime.now(timezone.utc) - timedelta(days=7)
            
            recent_questions = await self.questions_collection.count_documents({
                "created_at": {"$gte": week_ago}
            })
            recent_answers = await self.answers_collection.count_documents({
                "created_at": {"$gte": week_ago}
            })
            
            return QAStats(
                total_questions=total_questions,
                total_answers=total_answers,
                total_votes=total_votes,
                solved_questions=solved_questions,
                pending_answers=pending_answers,
                top_tags=top_tags,
                recent_questions=recent_questions,
                recent_answers=recent_answers
            )
            
        except Exception as e:
            logger.error(f"Error getting Q&A stats: {str(e)}")
            raise Exception(f"Failed to get statistics: {str(e)}")

    async def search_questions(self, query: SearchQuery) -> PaginatedResponse:
        """Advanced search for questions"""
        try:
            # Build search filters from query
            filters = QuestionFilters(
                q=query.q,
                tags=query.tags,
                category=query.category,
                difficulty=query.difficulty,
                solved=query.solved,
                author=query.author,
                sort_by=query.sort_by,
                sort_order=query.sort_order,
                skip=query.skip,
                limit=query.limit
            )
            
            return await self.get_questions(filters)
            
        except Exception as e:
            logger.error(f"Error searching questions: {str(e)}")
            raise Exception(f"Failed to search questions: {str(e)}")


# Global service instance
qa_service = QAService()