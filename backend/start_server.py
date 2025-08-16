#!/usr/bin/env python3
"""
Acode Lab Backend Server Startup Script
"""
import asyncio
import os
import sys
import uvicorn
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings


def main():
    """Start the FastAPI server"""
    
    print("🚀 Starting Acode Lab Backend Server...")
    print(f"📍 Environment: {'Development' if settings.debug else 'Production'}")
    print(f"🔗 MongoDB URL: {settings.mongo_url}")
    print(f"🗄️  Database: {settings.db_name}")
    print(f"🌐 CORS Origins: {settings.cors_origins}")
    print(f"📊 Log Level: {settings.log_level}")
    print("-" * 50)
    
    # Start server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        reload_dirs=["app"] if settings.debug else None,
        log_level=settings.log_level.lower(),
        access_log=True,
        server_header=False,
        date_header=False,
    )


if __name__ == "__main__":
    main()