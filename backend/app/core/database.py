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
            
            # Advanced Gamification indexes
            
            # Badges collection indexes
            await self.database.badges.create_index([("badge_type", ASCENDING)])
            await self.database.badges.create_index([("is_rare", ASCENDING)])
            await self.database.badges.create_index([("sort_order", ASCENDING)])
            
            # User badges collection indexes
            await self.database.user_badges.create_index([("user_id", ASCENDING)])
            await self.database.user_badges.create_index([("badge_id", ASCENDING)])
            await self.database.user_badges.create_index([
                ("user_id", ASCENDING), 
                ("badge_id", ASCENDING)
            ], unique=True)
            await self.database.user_badges.create_index([("is_featured", ASCENDING)])
            await self.database.user_badges.create_index([("earned_at", DESCENDING)])
            
            # Streaks collection indexes
            await self.database.streaks.create_index([("user_id", ASCENDING)])
            await self.database.streaks.create_index([("streak_type", ASCENDING)])
            await self.database.streaks.create_index([
                ("user_id", ASCENDING), 
                ("streak_type", ASCENDING)
            ], unique=True)
            await self.database.streaks.create_index([("is_active", ASCENDING)])
            await self.database.streaks.create_index([("current_count", DESCENDING)])
            await self.database.streaks.create_index([("best_count", DESCENDING)])
            
            # User achievements enhanced indexes  
            await self.database.user_achievements.create_index([("user_id", ASCENDING)])
            await self.database.user_achievements.create_index([("achievement_id", ASCENDING)])
            await self.database.user_achievements.create_index([
                ("user_id", ASCENDING), 
                ("achievement_id", ASCENDING)
            ], unique=True)
            await self.database.user_achievements.create_index([("is_earned", ASCENDING)])
            await self.database.user_achievements.create_index([("earned_at", DESCENDING)])
            
            # Leaderboards collection indexes
            await self.database.leaderboards.create_index([("leaderboard_type", ASCENDING)])
            await self.database.leaderboards.create_index([("period_start", ASCENDING)])
            await self.database.leaderboards.create_index([("period_end", ASCENDING)])
            await self.database.leaderboards.create_index([("last_updated", DESCENDING)])
            
            # Referrals collection indexes
            await self.database.referrals.create_index([("referrer_id", ASCENDING)])
            await self.database.referrals.create_index([("referred_id", ASCENDING)], unique=True)
            await self.database.referrals.create_index([("milestone", ASCENDING)])
            await self.database.referrals.create_index([("created_at", DESCENDING)])
            
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


def get_points_history_collection():
    """Get points history collection"""
    return database.database.points_history


def get_achievements_collection():
    """Get achievements collection"""
    return database.database.achievements

def get_companies_collection():
    """Get companies collection"""
    return database.database.companies


# Advanced Gamification Collections
def get_badges_collection():
    """Get badges collection"""
    return database.database.badges


def get_user_badges_collection():
    """Get user badges collection"""
    return database.database.user_badges


def get_streaks_collection():
    """Get streaks collection"""
    return database.database.streaks


def get_user_achievements_collection():
    """Get user achievements collection"""
    return database.database.user_achievements


def get_leaderboards_collection():
    """Get leaderboards collection"""
    return database.database.leaderboards


def get_referrals_collection():
    """Get referrals collection"""
    return database.database.referrals