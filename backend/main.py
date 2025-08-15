from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
import motor.motor_asyncio
import uvicorn

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Acode Lab API",
    description="API para plataforma de Q&A com sistema de gamificação",
    version="1.0.0"
)

# CORS configuration
cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "test_database")

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# Security
security = HTTPBearer(auto_error=False)

# Models
class QuestionResponse(BaseModel):
    id: str
    title: str
    content: str
    tags: List[str] = []
    author_id: str
    author_username: str
    created_at: str
    views: int = 0
    upvotes: int = 0
    downvotes: int = 0

class UserModel(BaseModel):
    id: str
    username: str
    email: str
    is_admin: bool = False

# Helper functions
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[dict]:
    """Get current user from token (simplified for demo)"""
    if not credentials:
        return None
    
    # Simplified - in real app, decode JWT token
    # For now, return a mock admin user for testing
    token = credentials.credentials
    
    # Mock different users based on token
    if "admin" in token.lower():
        return {
            "id": "admin-user-id",
            "username": "admin_user",
            "email": "admin@example.com", 
            "is_admin": True
        }
    else:
        return {
            "id": "mock-user-id",
            "username": "test_user",
            "email": "test@example.com",
            "is_admin": False
        }

# Routes
@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Acode Lab API is running", "status": "healthy"}

@app.get("/api/")
async def api_root():
    """API root endpoint"""
    return {"message": "Acode Lab API v1.0", "status": "healthy"}

@app.get("/api/questions/", response_model=List[QuestionResponse])
async def get_questions(skip: int = 0, limit: int = 20):
    """Get list of questions"""
    try:
        # Mock data for now - replace with actual database query
        questions = []
        for i in range(min(limit, 5)):  # Return max 5 mock questions
            questions.append({
                "id": f"question-{i+1}",
                "title": f"Pergunta de Exemplo {i+1}",
                "content": f"Este é o conteúdo da pergunta {i+1}. Como resolver este problema?",
                "tags": ["python", "fastapi", "exemplo"],
                "author_id": f"user-{i+1}",
                "author_username": f"usuario{i+1}",
                "created_at": "2024-08-15T18:00:00Z",
                "views": 10 + i,
                "upvotes": 5 + i,
                "downvotes": 0
            })
        
        return questions
        
    except Exception as e:
        print(f"Error getting questions: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/questions/{question_id}")
async def get_question(question_id: str):
    """Get specific question by ID"""
    try:
        # Mock data - replace with actual database query
        return {
            "id": question_id,
            "title": "Pergunta de Exemplo",
            "content": "Este é o conteúdo detalhado da pergunta.",
            "tags": ["python", "fastapi"],
            "author_id": "user-1",
            "author_username": "usuario1",
            "created_at": "2024-08-15T18:00:00Z",
            "views": 15,
            "upvotes": 8,
            "downvotes": 1
        }
    except Exception as e:
        print(f"Error getting question {question_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/auth/login")
async def login(credentials: dict):
    """User login endpoint"""
    try:
        email = credentials.get("email")
        password = credentials.get("password")
        
        if not email or not password:
            raise HTTPException(status_code=400, detail="Email e senha são obrigatórios")
        
        # Mock authentication - return admin user for admin email
        is_admin = "admin" in email.lower()
        token = "admin-token" if is_admin else "user-token"
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": "admin-1" if is_admin else "user-1",
                "username": "admin_user" if is_admin else "test_user",
                "email": email,
                "is_admin": is_admin,
                "pc_points": 1000 if is_admin else 50,
                "pcon_points": 500 if is_admin else 100,
                "rank": "Especialista" if is_admin else "Iniciante"
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error during login: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/auth/register")
async def register(user_data: dict):
    """User registration endpoint"""
    try:
        username = user_data.get("username")
        email = user_data.get("email")
        password = user_data.get("password")
        
        if not username or not email or not password:
            raise HTTPException(status_code=400, detail="Username, email e senha são obrigatórios")
        
        # Mock registration
        user_id = f"user-{hash(email) % 10000}"
        
        return {
            "message": "Usuário criado com sucesso",
            "user": {
                "id": user_id,
                "username": username,
                "email": email,
                "is_admin": False,
                "pc_points": 0,
                "pcon_points": 50,
                "rank": "Iniciante"
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error during registration: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Token inválido")
    
    return current_user

# Admin endpoints
class BotCreateRequest(BaseModel):
    username: str
    email: str
    pc_points: int = 0
    pcon_points: int = 0
    rank: str = "Iniciante"
    bio: str = ""
    location: str = ""
    skills: List[str] = []

@app.post("/api/admin/bots/")
async def create_bot(bot_data: BotCreateRequest, current_user: dict = Depends(get_current_user)):
    """Create a bot user (admin only)"""
    try:
        if not current_user or not current_user.get("is_admin"):
            raise HTTPException(status_code=403, detail="Acesso negado - Admin necessário")
        
        # Create bot user - mock implementation
        bot_id = f"bot-{bot_data.username}-{hash(bot_data.email) % 10000}"
        
        return {
            "bot_id": bot_id,
            "message": f"Bot {bot_data.username} criado com sucesso",
            "bot": {
                "id": bot_id,
                "username": bot_data.username,
                "email": bot_data.email,
                "pc_points": bot_data.pc_points,
                "pcon_points": bot_data.pcon_points,
                "rank": bot_data.rank,
                "bio": bot_data.bio,
                "location": bot_data.location,
                "skills": bot_data.skills,
                "is_bot": True,
                "created_at": "2024-08-15T18:00:00Z"
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating bot: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/api/admin/stats")
async def get_admin_stats(current_user: dict = Depends(get_current_user)):
    """Get admin statistics"""
    try:
        if not current_user or not current_user.get("is_admin"):
            raise HTTPException(status_code=403, detail="Acesso negado - Admin necessário")
        
        # Mock stats
        return {
            "total_users": 150,
            "total_companies": 25,
            "total_questions": 350,
            "total_answers": 1250,
            "pending_answers": 45,
            "total_articles": 75,
            "active_today": 35
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting admin stats: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/api/admin/answers/pending")
async def get_pending_answers(current_user: dict = Depends(get_current_user)):
    """Get pending answers for validation"""
    try:
        if not current_user or not current_user.get("is_admin"):
            raise HTTPException(status_code=403, detail="Acesso negado - Admin necessário")
        
        # Mock pending answers
        return [
            {
                "id": "answer-1",
                "content": "Esta é uma resposta aguardando validação...",
                "question_id": "question-1",
                "question_title": "Como implementar JWT?",
                "author_id": "user-1",
                "author_username": "developer1",
                "created_at": "2024-08-15T17:30:00Z"
            }
        ]
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting pending answers: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    print(f"Global exception: {exc}")
    return {"detail": f"Internal server error: {str(exc)}"}

if __name__ == "__main__":
    print("Starting Acode Lab API server...")
    print(f"MongoDB URL: {MONGO_URL}")
    print(f"Database: {DB_NAME}")
    print(f"CORS Origins: {cors_origins}")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )