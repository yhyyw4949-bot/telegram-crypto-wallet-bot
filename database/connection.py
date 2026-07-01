"""
Database connection and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import logging
from config.settings import DATABASE_TYPE, DATABASE_URL
from .models import Base

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self):
        self.database_type = DATABASE_TYPE
        self.database_url = DATABASE_URL
        self.engine = None
        self.SessionLocal = None
    
    def initialize(self):
        """Initialize database connection and create tables"""
        try:
            # SQLite specific configuration
            if self.database_type == 'sqlite':
                self.engine = create_engine(
                    self.database_url,
                    connect_args={"check_same_thread": False},
                    poolclass=StaticPool,
                    echo=False
                )
            else:
                # PostgreSQL configuration
                self.engine = create_engine(
                    self.database_url,
                    echo=False,
                    pool_size=20,
                    max_overflow=40
                )
            
            # Create all tables
            Base.metadata.create_all(self.engine)
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            logger.info(f"✓ Database initialized ({self.database_type})")
            return True
        except Exception as e:
            logger.error(f"✗ Database initialization failed: {e}")
            return False
    
    def get_session(self) -> Session:
        """Get a new database session"""
        if self.SessionLocal is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self.SessionLocal()
    
    def close(self):
        """Close database connections"""
        if self.engine:
            self.engine.dispose()
            logger.info("✓ Database connection closed")

# Global database manager instance
db_manager = DatabaseManager()

def get_db() -> Session:
    """Get database session (for dependency injection)"""
    return db_manager.get_session()
