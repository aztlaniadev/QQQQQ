"""
Database connection and configuration
"""
import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING
from .config import settings

logger = logging.getLogger(__name__)


class Database:
    """Database connection manager"""
    
    def __init__(self):
        self.client: AsyncIOMotorClient = None
        self.database: AsyncIOMotorDatabase = None
    
    async def connect(self):
        """Connect to MongoDB"""
        try:
            logger.info(f"Connecting to MongoDB at {settings.mongo_url}")
            self.client = AsyncIOMotorClient(settings.mongo_url)
            self.database = self.client[settings.db_name]
            
            # Test connection
            await self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
            
            # Create indexes
            await self.create_indexes()
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    async def create_indexes(self):
        """Create database indexes for optimal performance"""
        try:
            # Users collection indexes
            await self.database.users.create_index([("email", ASCENDING)], unique=True)
            await self.database.users.create_index([("username", ASCENDING)], unique=True)
            await self.database.users.create_index([("is_admin", ASCENDING)])
            await self.database.users.create_index([("is_company", ASCENDING)])
            await self.database.users.create_index([("pc_points", DESCENDING)])
            await self.database.users.create_index([("rank", ASCENDING)])
            await self.database.users.create_index([("created_at", DESCENDING)])
            
            # Questions collection indexes
            await self.database.questions.create_index([("author_id", ASCENDING)])
            await self.database.questions.create_index([("tags", ASCENDING)])
            await self.database.questions.create_index([("category", ASCENDING)])
            await self.database.questions.create_index([("is_solved", ASCENDING)])
            await self.database.questions.create_index([("created_at", DESCENDING)])
            await self.database.questions.create_index([("views", DESCENDING)])
            await self.database.questions.create_index([("upvotes", DESCENDING)])
            # Text search index
            await self.database.questions.create_index([
                ("title", "text"), 
                ("content", "text")
            ])
            
            # Answers collection indexes
            await self.database.answers.create_index([("question_id", ASCENDING)])
            await self.database.answers.create_index([("author_id", ASCENDING)])
            await self.database.answers.create_index([("is_accepted", ASCENDING)])
            await self.database.answers.create_index([("created_at", DESCENDING)])
            await self.database.answers.create_index([("upvotes", DESCENDING)])
            await self.database.answers.create_index([("is_validated", ASCENDING)])
            
            # Votes collection indexes
            await self.database.votes.create_index([
                ("user_id", ASCENDING), 
                ("target_id", ASCENDING), 
                ("target_type", ASCENDING)
            ], unique=True)
            await self.database.votes.create_index([("target_id", ASCENDING)])
            await self.database.votes.create_index([("user_id", ASCENDING)])
            
            # Achievements collection indexes
            await self.database.achievements.create_index([("user_id", ASCENDING)])
            await self.database.achievements.create_index([("achievement_type", ASCENDING)])
            await self.database.achievements.create_index([("created_at", DESCENDING)])
            
            # Points history collection indexes
            await self.database.points_history.create_index([("user_id", ASCENDING)])
            await self.database.points_history.create_index([("created_at", DESCENDING)])
            await self.database.points_history.create_index([("point_type", ASCENDING)])
            
            # Companies collection indexes
            await self.database.companies.create_index([("email", ASCENDING)], unique=True)
            await self.database.companies.create_index([("name", ASCENDING)])
            await self.database.companies.create_index([("created_at", DESCENDING)])
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
            # Don't raise here as indexes might already exist


# Global database instance
database = Database()


async def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    return database.database


# Collection getters for easy access
def get_users_collection():
    """Get users collection"""
    return database.database.users

def get_questions_collection():
    """Get questions collection"""
    return database.database.questions

def get_answers_collection():
    """Get answers collection"""
    return database.database.answers

def get_votes_collection():
    """Get votes collection"""
    return database.database.votes

def get_achievements_collection():
    """Get achievements collection"""
    return database.database.achievements

def get_points_history_collection():
    """Get points history collection"""
    return database.database.points_history

def get_companies_collection():
    """Get companies collection"""
    return database.database.companies