"""
Q&A System Tests
Tests for questions, answers, and voting functionality
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from app.main import app

pytestmark = pytest.mark.asyncio


class TestQASystem:
    """Test Q&A system functionality"""

    @pytest_asyncio.fixture
    async def client(self):
        """Create async test client"""
        from httpx import ASGITransport
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            yield client

    @pytest.fixture
    def mock_user(self):
        """Mock authenticated user"""
        return {
            "id": "test_user_123",
            "username": "testuser",
            "email": "test@example.com",
            "is_admin": False,
            "is_active": True
        }

    @pytest.fixture
    def mock_admin(self):
        """Mock admin user"""
        return {
            "id": "admin_user_123",
            "username": "admin",
            "email": "admin@example.com",
            "is_admin": True,
            "is_active": True
        }

    @pytest.fixture
    def mock_question_data(self):
        """Mock question creation data"""
        return {
            "title": "Como implementar autenticação JWT?",
            "content": "Estou desenvolvendo uma API e preciso implementar autenticação JWT.",
            "tags": ["jwt", "authentication", "api"],
            "category": "backend",
            "difficulty": "intermediate"
        }

    @pytest.fixture
    def mock_answer_data(self):
        """Mock answer creation data"""
        return {
            "content": "Para implementar JWT, você pode usar a biblioteca python-jose...",
            "question_id": "question_123"
        }

    @pytest.fixture
    def mock_vote_data(self):
        """Mock vote data"""
        return {
            "target_id": "question_123",
            "target_type": "question",
            "vote_type": "upvote"
        }

    # ===========================================
    # QUESTIONS TESTS
    # ===========================================

    async def test_create_question_success(self, client, mock_user, mock_question_data):
        """Test successful question creation"""
        with patch("app.core.security.get_current_user", return_value=mock_user):
            with patch("app.services.qa_service.qa_service.create_question") as mock_create:
                # Mock service response
                mock_response = {
                    "id": "question_123",
                    **mock_question_data,
                    "author_id": mock_user["id"],
                    "views": 0,
                    "upvotes": 0,
                    "downvotes": 0,
                    "score": 0,
                    "answers_count": 0,
                    "is_solved": False,
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z",
                    "author": {
                        "id": mock_user["id"],
                        "username": mock_user["username"],
                        "avatar_url": None
                    }
                }
                mock_create.return_value = mock_response

                response = await client.post("/api/questions/", json=mock_question_data)

                assert response.status_code == 201
                data = response.json()
                assert data["title"] == mock_question_data["title"]
                assert data["author"]["username"] == mock_user["username"]
                mock_create.assert_called_once()

    async def test_create_question_unauthenticated(self, client, mock_question_data):
        """Test question creation without authentication"""
        response = await client.post("/api/questions/", json=mock_question_data)
        assert response.status_code == 403

    async def test_get_questions_success(self, client):
        """Test getting questions list"""
        with patch("app.services.qa_service.qa_service.get_questions") as mock_get:
            mock_response = {
                "items": [
                    {
                        "id": "question_123",
                        "title": "Test Question",
                        "content": "Test content",
                        "author": {"id": "user_123", "username": "testuser"},
                        "tags": ["test"],
                        "views": 10,
                        "upvotes": 5,
                        "score": 5
                    }
                ],
                "total": 1,
                "page": 1,
                "pages": 1,
                "limit": 20
            }
            mock_get.return_value = mock_response

            response = await client.get("/api/questions/")

            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 1
            assert len(data["items"]) == 1
            assert data["items"][0]["title"] == "Test Question"

    async def test_get_question_by_id_success(self, client):
        """Test getting question by ID"""
        question_id = "question_123"
        with patch("app.services.qa_service.qa_service.get_question_by_id") as mock_get:
            mock_response = {
                "id": question_id,
                "title": "Test Question",
                "content": "Test content",
                "author": {"id": "user_123", "username": "testuser"},
                "tags": ["test"],
                "views": 10,
                "upvotes": 5,
                "score": 5,
                "answers": []
            }
            mock_get.return_value = mock_response

            response = await client.get(f"/api/questions/{question_id}")

            assert response.status_code == 200
            data = response.json()
            assert data["id"] == question_id
            assert data["title"] == "Test Question"
            assert "answers" in data

    async def test_get_question_not_found(self, client):
        """Test getting non-existent question"""
        question_id = "nonexistent"
        with patch("app.services.qa_service.qa_service.get_question_by_id") as mock_get:
            mock_get.side_effect = Exception("Question not found")

            response = await client.get(f"/api/questions/{question_id}")

            assert response.status_code == 404

    async def test_update_question_success(self, client, mock_user):
        """Test successful question update"""
        question_id = "question_123"
        update_data = {"title": "Updated Title", "content": "Updated content"}

        with patch("app.core.security.get_current_user", return_value=mock_user):
            with patch("app.services.qa_service.qa_service.update_question") as mock_update:
                mock_response = {
                    "id": question_id,
                    **update_data,
                    "author": {"id": mock_user["id"], "username": mock_user["username"]}
                }
                mock_update.return_value = mock_response

                response = await client.put(f"/api/questions/{question_id}", json=update_data)

                assert response.status_code == 200
                data = response.json()
                assert data["title"] == update_data["title"]
                mock_update.assert_called_once()

    async def test_delete_question_success(self, client, mock_user):
        """Test successful question deletion"""
        question_id = "question_123"

        with patch("app.core.security.get_current_user", return_value=mock_user):
            with patch("app.services.qa_service.qa_service.delete_question") as mock_delete:
                mock_delete.return_value = True

                response = await client.delete(f"/api/questions/{question_id}")

                assert response.status_code == 200
                data = response.json()
                assert "deleted successfully" in data["message"]
                mock_delete.assert_called_once_with(question_id, mock_user["id"])

    async def test_search_questions_success(self, client):
        """Test question search"""
        search_params = {"q": "jwt", "tags": ["authentication"], "difficulty": "intermediate"}

        with patch("app.services.qa_service.qa_service.search_questions") as mock_search:
            mock_response = {
                "items": [
                    {
                        "id": "question_123",
                        "title": "JWT Authentication",
                        "tags": ["jwt", "authentication"],
                        "difficulty": "intermediate"
                    }
                ],
                "total": 1,
                "page": 1,
                "pages": 1,
                "limit": 20
            }
            mock_search.return_value = mock_response

            response = await client.get("/api/questions/search", params=search_params)

            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 1
            assert "jwt" in data["items"][0]["title"].lower()

    # ===========================================
    # ANSWERS TESTS
    # ===========================================

    async def test_create_answer_success(self, client, mock_user, mock_answer_data):
        """Test successful answer creation"""
        with patch("app.core.security.get_current_user", return_value=mock_user):
            with patch("app.services.qa_service.qa_service.create_answer") as mock_create:
                mock_response = {
                    "id": "answer_123",
                    **mock_answer_data,
                    "author_id": mock_user["id"],
                    "upvotes": 0,
                    "downvotes": 0,
                    "score": 0,
                    "is_accepted": False,
                    "is_validated": False,
                    "created_at": "2024-01-01T00:00:00Z",
                    "author": {
                        "id": mock_user["id"],
                        "username": mock_user["username"],
                        "avatar_url": None
                    }
                }
                mock_create.return_value = mock_response

                response = await client.post("/api/answers/", json=mock_answer_data)

                assert response.status_code == 201
                data = response.json()
                assert data["content"] == mock_answer_data["content"]
                assert data["is_validated"] == False
                mock_create.assert_called_once()

    async def test_get_answer_by_id_success(self, client):
        """Test getting answer by ID"""
        answer_id = "answer_123"
        with patch("app.services.qa_service.qa_service.get_answer_by_id") as mock_get:
            mock_response = {
                "id": answer_id,
                "content": "Test answer content",
                "author": {"id": "user_123", "username": "testuser"},
                "upvotes": 3,
                "score": 3,
                "is_accepted": False
            }
            mock_get.return_value = mock_response

            response = await client.get(f"/api/answers/{answer_id}")

            assert response.status_code == 200
            data = response.json()
            assert data["id"] == answer_id
            assert data["content"] == "Test answer content"

    async def test_accept_answer_success(self, client, mock_user):
        """Test accepting an answer"""
        answer_id = "answer_123"

        with patch("app.core.security.get_current_user", return_value=mock_user):
            with patch("app.services.qa_service.qa_service.accept_answer") as mock_accept:
                mock_response = {
                    "id": answer_id,
                    "content": "Accepted answer",
                    "is_accepted": True,
                    "author": {"id": "author_123", "username": "author"}
                }
                mock_accept.return_value = mock_response

                response = await client.post(f"/api/answers/{answer_id}/accept")

                assert response.status_code == 200
                data = response.json()
                assert data["is_accepted"] == True
                mock_accept.assert_called_once_with(answer_id, mock_user["id"])

    async def test_validate_answer_admin_success(self, client, mock_admin):
        """Test admin validating an answer"""
        answer_id = "answer_123"

        with patch("app.core.security.get_current_admin_user", return_value=mock_admin):
            with patch("app.services.qa_service.qa_service.validate_answer") as mock_validate:
                mock_response = {
                    "id": answer_id,
                    "content": "Validated answer",
                    "is_validated": True,
                    "author": {"id": "author_123", "username": "author"}
                }
                mock_validate.return_value = mock_response

                response = await client.post(f"/api/answers/{answer_id}/validate")

                assert response.status_code == 200
                data = response.json()
                assert data["is_validated"] == True
                mock_validate.assert_called_once_with(answer_id, mock_admin["id"])

    async def test_validate_answer_non_admin_forbidden(self, client, mock_user):
        """Test non-admin cannot validate answers"""
        answer_id = "answer_123"

        with patch("app.core.security.get_current_admin_user") as mock_admin_check:
            mock_admin_check.side_effect = Exception("Admin access required")

            response = await client.post(f"/api/answers/{answer_id}/validate")

            assert response.status_code == 403

    # ===========================================
    # VOTES TESTS
    # ===========================================

    async def test_vote_question_success(self, client, mock_user, mock_vote_data):
        """Test voting on a question"""
        with patch("app.core.security.get_current_user", return_value=mock_user):
            with patch("app.services.qa_service.qa_service.vote") as mock_vote:
                mock_response = {
                    "target_id": mock_vote_data["target_id"],
                    "target_type": mock_vote_data["target_type"],
                    "user_vote": "upvote",
                    "upvotes": 6,
                    "downvotes": 1,
                    "score": 5
                }
                mock_vote.return_value = mock_response

                response = await client.post("/api/votes/", json=mock_vote_data)

                assert response.status_code == 200
                data = response.json()
                assert data["user_vote"] == "upvote"
                assert data["upvotes"] == 6
                mock_vote.assert_called_once()

    async def test_upvote_convenience_endpoint(self, client, mock_user):
        """Test upvote convenience endpoint"""
        target_type = "question"
        target_id = "question_123"

        with patch("app.core.security.get_current_user", return_value=mock_user):
            with patch("app.services.qa_service.qa_service.vote") as mock_vote:
                mock_response = {
                    "target_id": target_id,
                    "target_type": target_type,
                    "user_vote": "upvote",
                    "upvotes": 6,
                    "downvotes": 1,
                    "score": 5
                }
                mock_vote.return_value = mock_response

                response = await client.post(f"/api/votes/{target_type}/{target_id}/upvote")

                assert response.status_code == 200
                data = response.json()
                assert data["user_vote"] == "upvote"

    async def test_downvote_convenience_endpoint(self, client, mock_user):
        """Test downvote convenience endpoint"""
        target_type = "answer"
        target_id = "answer_123"

        with patch("app.core.security.get_current_user", return_value=mock_user):
            with patch("app.services.qa_service.qa_service.vote") as mock_vote:
                mock_response = {
                    "target_id": target_id,
                    "target_type": target_type,
                    "user_vote": "downvote",
                    "upvotes": 5,
                    "downvotes": 2,
                    "score": 3
                }
                mock_vote.return_value = mock_response

                response = await client.post(f"/api/votes/{target_type}/{target_id}/downvote")

                assert response.status_code == 200
                data = response.json()
                assert data["user_vote"] == "downvote"

    async def test_get_user_vote_success(self, client, mock_user):
        """Test getting user's vote on a target"""
        target_type = "question"
        target_id = "question_123"

        with patch("app.core.security.get_current_user", return_value=mock_user):
            with patch("app.services.qa_service.qa_service.get_user_vote") as mock_get_vote:
                mock_get_vote.return_value = "upvote"

                response = await client.get(f"/api/votes/{target_type}/{target_id}/user-vote")

                assert response.status_code == 200
                data = response.json()
                assert data["user_vote"] == "upvote"
                assert data["target_id"] == target_id
                assert data["target_type"] == target_type

    async def test_vote_invalid_target_type(self, client, mock_user):
        """Test voting with invalid target type"""
        target_type = "invalid"
        target_id = "target_123"

        with patch("app.core.security.get_current_user", return_value=mock_user):
            response = await client.post(f"/api/votes/{target_type}/{target_id}/upvote")

            assert response.status_code == 400
            data = response.json()
            assert "must be 'question' or 'answer'" in data["detail"]

    async def test_vote_own_content_forbidden(self, client, mock_user):
        """Test that users cannot vote on their own content"""
        vote_data = {
            "target_id": "question_123",
            "target_type": "question",
            "vote_type": "upvote"
        }

        with patch("app.core.security.get_current_user", return_value=mock_user):
            with patch("app.services.qa_service.qa_service.vote") as mock_vote:
                mock_vote.side_effect = Exception("Cannot vote on your own content")

                response = await client.post("/api/votes/", json=vote_data)

                assert response.status_code == 403
                data = response.json()
                assert "Cannot vote on your own content" in data["detail"]

    # ===========================================
    # QUESTION ANSWERS ENDPOINT TESTS
    # ===========================================

    async def test_get_question_answers_success(self, client):
        """Test getting answers for a specific question"""
        question_id = "question_123"

        with patch("app.services.qa_service.qa_service.get_question_answers") as mock_get_answers:
            mock_response = [
                {
                    "id": "answer_1",
                    "content": "First answer",
                    "author": {"id": "user_1", "username": "user1"},
                    "score": 5,
                    "is_accepted": True
                },
                {
                    "id": "answer_2",
                    "content": "Second answer",
                    "author": {"id": "user_2", "username": "user2"},
                    "score": 2,
                    "is_accepted": False
                }
            ]
            mock_get_answers.return_value = mock_response

            response = await client.get(f"/api/questions/{question_id}/answers")

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["is_accepted"] == True
            assert data[1]["is_accepted"] == False

    # ===========================================
    # ERROR HANDLING TESTS
    # ===========================================

    async def test_create_question_invalid_data(self, client, mock_user):
        """Test question creation with invalid data"""
        invalid_data = {"title": "", "content": "too short", "tags": []}

        with patch("app.core.security.get_current_user", return_value=mock_user):
            response = await client.post("/api/questions/", json=invalid_data)

            # Should be 422 for validation error
            assert response.status_code == 422

    async def test_create_answer_question_not_found(self, client, mock_user):
        """Test creating answer for non-existent question"""
        answer_data = {
            "content": "Test answer",
            "question_id": "nonexistent_question"
        }

        with patch("app.core.security.get_current_user", return_value=mock_user):
            with patch("app.services.qa_service.qa_service.create_answer") as mock_create:
                mock_create.side_effect = Exception("Question not found")

                response = await client.post("/api/answers/", json=answer_data)

                assert response.status_code == 404

    async def test_update_question_permission_denied(self, client, mock_user):
        """Test updating question without permission"""
        question_id = "question_123"
        update_data = {"title": "Updated title"}

        with patch("app.core.security.get_current_user", return_value=mock_user):
            with patch("app.services.qa_service.qa_service.update_question") as mock_update:
                mock_update.side_effect = Exception("Permission denied")

                response = await client.put(f"/api/questions/{question_id}", json=update_data)

                assert response.status_code == 403