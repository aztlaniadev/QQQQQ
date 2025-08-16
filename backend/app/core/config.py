"""
Configuration settings for Acode Lab Backend
"""
import os
from typing import List, Optional, Dict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # App Info
    app_name: str = "Acode Lab API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Database
    mongo_url: str = "mongodb://localhost:27017"
    db_name: str = "acode_lab"
    
    # Security
    secret_key: str = "your-super-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # CORS
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    
    # API Configuration
    api_prefix: str = "/api"
    max_upload_size: int = 10 * 1024 * 1024  # 10MB
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds
    
    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100
    
    # Email (for future notifications)
    smtp_server: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    
    # Redis (for caching - future)
    redis_url: Optional[str] = None
    
    # Logging
    log_level: str = "INFO"
    
    # Gamification
    pc_points_config: dict = {
        "question_created": 5,
        "answer_created": 10,
        "answer_accepted": 25,
        "received_upvote": 3,
        "received_downvote": -1,
        "daily_login": 1,
        "profile_completed": 10
    }
    
    pcon_points_config: Dict[str, int] = {
        "question_created": 2,
        "answer_created": 5,
        "answer_accepted": 15,
        "received_upvote": 1,
        "received_downvote": 0,
        "daily_login": 1,
        "profile_completed": 5
    }
    
    rank_config: Dict[str, Dict[str, int]] = {
        "Iniciante": {"pc_points": 0, "pcon_points": 0},
        "Colaborador": {"pc_points": 50, "pcon_points": 25},
        "Especialista": {"pc_points": 150, "pcon_points": 75},
        "Veterano": {"pc_points": 300, "pcon_points": 150},
        "Mestre": {"pc_points": 600, "pcon_points": 300},
        "Lenda": {"pc_points": 1200, "pcon_points": 600}
    }
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convert CORS origins string to list"""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings