"""
Database configuration and connection management
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import asyncio
from typing import AsyncGenerator
import logging

from models import Base

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite+aiosqlite:///./ai_ppt_system.db"
)

# For production, use PostgreSQL
# DATABASE_URL = "postgresql+asyncpg://user:password@localhost/ai_ppt_system"

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL logging
    poolclass=StaticPool if "sqlite" in DATABASE_URL else None,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

async def init_db():
    """Initialize database tables"""
    try:
        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("✅ Database initialized successfully")
        
        # Create initial data if needed
        await create_initial_data()
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise

async def create_initial_data():
    """Create initial data for the system"""
    try:
        async with AsyncSessionLocal() as db:
            # Check if we need to create initial data
            from models import AIModel
            
            # Create initial AI model record
            existing_model = await db.execute(
                "SELECT id FROM ai_models WHERE name = 'atomic_predictor' LIMIT 1"
            )
            
            if not existing_model.fetchone():
                initial_model = AIModel(
                    name="atomic_predictor",
                    version="1.0.0",
                    model_type="prediction",
                    accuracy=0.0,
                    training_samples=0,
                    config={
                        "model_type": "neural_network",
                        "input_features": [
                            "current_slide_elements",
                            "slide_layout",
                            "user_patterns",
                            "presentation_context"
                        ],
                        "output_classes": [
                            "ADD_text", "ADD_image", "ADD_shape", "ADD_chart", "ADD_table",
                            "MODIFY_position", "MODIFY_style", "MODIFY_content",
                            "CREATE_slide", "DELETE_slide", "REORDER_slides",
                            "APPLY_theme", "APPLY_layout"
                        ]
                    }
                )
                db.add(initial_model)
                await db.commit()
                logger.info("Created initial AI model record")
                
    except Exception as e:
        logger.error(f"Failed to create initial data: {e}")

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise
        finally:
            await session.close()

async def close_db():
    """Close database connections"""
    await engine.dispose()
    logger.info("Database connections closed")

# Database utilities
class DatabaseManager:
    """Database management utilities"""
    
    @staticmethod
    async def execute_raw_query(query: str, params: dict = None):
        """Execute raw SQL query"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(query, params or {})
            await session.commit()
            return result
    
    @staticmethod
    async def get_table_stats():
        """Get statistics about database tables"""
        stats = {}
        
        async with AsyncSessionLocal() as session:
            # Get row counts for each table
            tables = [
                "atomic_operations",
                "presentations", 
                "operation_sequences",
                "user_sessions",
                "ai_models",
                "user_preferences",
                "operation_patterns",
                "learning_data"
            ]
            
            for table in tables:
                try:
                    result = await session.execute(f"SELECT COUNT(*) FROM {table}")
                    count = result.scalar()
                    stats[table] = count
                except Exception as e:
                    stats[table] = f"Error: {e}"
        
        return stats
    
    @staticmethod
    async def cleanup_old_data(days: int = 30):
        """Clean up old data (older than specified days)"""
        async with AsyncSessionLocal() as session:
            try:
                # Clean up old sessions
                await session.execute(
                    "DELETE FROM user_sessions WHERE start_time < datetime('now', '-{} days')".format(days)
                )
                
                # Clean up old operations (keep learning data)
                await session.execute(
                    "DELETE FROM atomic_operations WHERE timestamp < datetime('now', '-{} days') AND id NOT IN (SELECT operation_id FROM learning_data WHERE operation_id IS NOT NULL)".format(days)
                )
                
                await session.commit()
                logger.info(f"Cleaned up data older than {days} days")
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to cleanup old data: {e}")
                raise

# Redis configuration for caching and real-time features
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

try:
    import redis.asyncio as redis
    
    redis_client = redis.from_url(
        REDIS_URL,
        encoding="utf-8",
        decode_responses=True
    )
    
    async def init_redis():
        """Initialize Redis connection"""
        try:
            await redis_client.ping()
            logger.info("✅ Redis connected successfully")
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed: {e}")
            # Continue without Redis for development
    
    async def close_redis():
        """Close Redis connection"""
        await redis_client.close()
        logger.info("Redis connection closed")
        
except ImportError:
    logger.warning("Redis not available, using in-memory cache")
    redis_client = None
    
    async def init_redis():
        pass
    
    async def close_redis():
        pass

# Cache utilities
class CacheManager:
    """Cache management utilities"""
    
    @staticmethod
    async def set(key: str, value: str, expire: int = 3600):
        """Set cache value"""
        if redis_client:
            await redis_client.setex(key, expire, value)
    
    @staticmethod
    async def get(key: str) -> str:
        """Get cache value"""
        if redis_client:
            return await redis_client.get(key)
        return None
    
    @staticmethod
    async def delete(key: str):
        """Delete cache value"""
        if redis_client:
            await redis_client.delete(key)
    
    @staticmethod
    async def exists(key: str) -> bool:
        """Check if cache key exists"""
        if redis_client:
            return await redis_client.exists(key)
        return False