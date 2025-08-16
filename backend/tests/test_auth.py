"""
Tests for authentication endpoints
"""
import pytest
import asyncio
from httpx import AsyncClient
from unittest.mock import patch

from app.main import app
from app.core.database import database
from app.models.user import UserCreate, UserLogin


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def client():
    """Create test client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def test_user_data():
    """Test user data"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPass123!"
    }


class TestAuth:
    """Authentication tests"""
    
    async def test_health_check(self, client: AsyncClient):
        """Test health check endpoint"""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "unhealthy"]
        assert "version" in data
    
    async def test_root_endpoint(self, client: AsyncClient):
        """Test root endpoint"""
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
    
    @patch('app.services.auth_service.auth_service.register_user')
    async def test_register_user(self, mock_register, client: AsyncClient, test_user_data):
        """Test user registration"""
        # Mock successful registration
        mock_register.return_value = {
            "access_token": "test_token",
            "refresh_token": "test_refresh",
            "token_type": "bearer",
            "expires_in": 1800,
            "user": {
                "id": "test_id",
                "username": test_user_data["username"],
                "email": test_user_data["email"]
            }
        }
        
        response = await client.post("/api/auth/register", json=test_user_data)
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "user" in data
    
    @patch('app.services.auth_service.auth_service.login_user')
    async def test_login_user(self, mock_login, client: AsyncClient):
        """Test user login"""
        login_data = {
            "email": "test@example.com",
            "password": "TestPass123!"
        }
        
        # Mock successful login
        mock_login.return_value = {
            "access_token": "test_token",
            "refresh_token": "test_refresh",
            "token_type": "bearer",
            "expires_in": 1800,
            "user": {
                "id": "test_id",
                "username": "testuser",
                "email": "test@example.com"
            }
        }
        
        response = await client.post("/api/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data
    
    async def test_register_invalid_data(self, client: AsyncClient):
        """Test registration with invalid data"""
        invalid_data = {
            "username": "te",  # Too short
            "email": "invalid-email",
            "password": "weak"
        }
        
        response = await client.post("/api/auth/register", json=invalid_data)
        assert response.status_code == 422  # Validation error
    
    async def test_login_invalid_data(self, client: AsyncClient):
        """Test login with invalid data"""
        invalid_data = {
            "email": "invalid-email",
            "password": ""
        }
        
        response = await client.post("/api/auth/login", json=invalid_data)
        assert response.status_code == 422  # Validation error
    
    @patch('app.core.security.get_current_user')
    async def test_get_current_user(self, mock_get_user, client: AsyncClient):
        """Test get current user endpoint"""
        # Mock current user
        mock_get_user.return_value = {
            "id": "test_id",
            "username": "testuser",
            "email": "test@example.com"
        }
        
        headers = {"Authorization": "Bearer test_token"}
        response = await client.get("/api/auth/me", headers=headers)
        assert response.status_code == 200
    
    async def test_unauthorized_access(self, client: AsyncClient):
        """Test unauthorized access to protected endpoint"""
        response = await client.get("/api/auth/me")
        assert response.status_code == 403  # Forbidden - no token
    
    async def test_check_username_availability(self, client: AsyncClient):
        """Test username availability check"""
        response = await client.post("/api/auth/check-username", params={"username": "newuser"})
        assert response.status_code == 200
        data = response.json()
        assert "username" in data
        assert "available" in data
    
    async def test_check_email_availability(self, client: AsyncClient):
        """Test email availability check"""
        response = await client.post("/api/auth/check-email", params={"email": "new@example.com"})
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert "available" in data