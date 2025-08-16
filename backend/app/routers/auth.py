"""
Authentication routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from ..core.security import get_current_user
from ..models.user import UserCreate, UserLogin, UserResponse
from ..models.base import TokenResponse, MessageResponse
from ..services.auth_service import auth_service

router = APIRouter()
security = HTTPBearer()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """
    Register a new user
    
    Creates a new user account and returns authentication tokens.
    """
    return await auth_service.register_user(user_data)


@router.post("/login", response_model=TokenResponse)
async def login(login_data: UserLogin):
    """
    Login user
    
    Authenticate user with email and password, returns tokens.
    """
    return await auth_service.login_user(login_data)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str):
    """
    Refresh access token
    
    Use refresh token to get new access token.
    """
    return await auth_service.refresh_access_token(refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current user information
    
    Returns detailed information about the authenticated user.
    """
    return await auth_service.get_current_user_info(current_user["id"])


@router.post("/logout", response_model=MessageResponse)
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout user
    
    Invalidates the current session (client-side token removal).
    """
    # For stateless JWT, logout is primarily client-side
    # In a more advanced implementation, you might maintain a blacklist
    return MessageResponse(message="Successfully logged out")


@router.get("/validate", response_model=MessageResponse)
async def validate_token(current_user: dict = Depends(get_current_user)):
    """
    Validate current token
    
    Check if the current token is valid and user is authenticated.
    """
    return MessageResponse(message="Token is valid")


@router.post("/check-username")
async def check_username_availability(username: str):
    """
    Check if username is available
    
    Returns whether the username is already taken.
    """
    exists = await auth_service.check_user_exists(username=username)
    return {
        "username": username,
        "available": not exists,
        "message": "Username is available" if not exists else "Username is already taken"
    }


@router.post("/check-email")
async def check_email_availability(email: str):
    """
    Check if email is available
    
    Returns whether the email is already registered.
    """
    exists = await auth_service.check_user_exists(email=email)
    return {
        "email": email,
        "available": not exists,
        "message": "Email is available" if not exists else "Email is already registered"
    }