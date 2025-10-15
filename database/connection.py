"""
Database Connection Manager
Handles database connections, sessions, and migrations
"""

import os
from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from alembic import command
from alembic.config import Config

from config.settings import settings
from core.logging_config import get_logger
from database.models import Base


logger = get_logger(__name__)


class DatabaseManager:
    """Manages database connections and sessions"""
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url or settings.database.url
        self.engine = None
        self.SessionLocal = None
        self._initialized = False
        
    def initialize(self):
        """Initialize database connection"""
        if self._initialized:
            return
            
        try:
            # Create engine with connection pooling
            self.engine = create_engine(
                self.database_url,
                poolclass=QueuePool,
                pool_size=settings.database.pool_size,
                max_overflow=settings.database.max_overflow,
                pool_timeout=settings.database.pool_timeout,
                echo=settings.database.echo,
                pool_pre_ping=True,  # Verify connections before using
                connect_args={
                    "check_same_thread": False  # For SQLite
                } if "sqlite" in self.database_url else {}
            )
            
            # Add event listeners for connection debugging
            if settings.debug:
                @event.listens_for(self.engine, "connect")
                def receive_connect(dbapi_connection, connection_record):
                    logger.debug("Database connection established")
                
                @event.listens_for(self.engine, "close")
                def receive_close(dbapi_connection, connection_record):
                    logger.debug("Database connection closed")
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            self._initialized = True
            logger.info(
                "Database initialized",
                extra={"database_url": self._sanitize_url(self.database_url)}
            )
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def _sanitize_url(self, url: str) -> str:
        """Remove sensitive information from database URL for logging"""
        if "@" in url:
            # Hide password in connection string
            parts = url.split("@")
            if ":" in parts[0]:
                protocol_user = parts[0].split(":")
                if len(protocol_user) >= 3:
                    # Format: protocol://user:password@host
                    sanitized = f"{protocol_user[0]}:{protocol_user[1]}:****@{parts[1]}"
                    return sanitized
        return url
    
    def create_tables(self):
        """Create all database tables"""
        if not self._initialized:
            self.initialize()
            
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise
    
    def drop_tables(self):
        """Drop all database tables (use with caution!)"""
        if not self._initialized:
            self.initialize()
            
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.warning("All database tables dropped")
        except Exception as e:
            logger.error(f"Failed to drop tables: {e}")
            raise
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Get a database session with automatic cleanup
        
        Usage:
            with db_manager.get_session() as session:
                # Use session here
                session.query(...)
        """
        if not self._initialized:
            self.initialize()
            
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def get_new_session(self) -> Session:
        """
        Get a new database session
        Note: Caller is responsible for closing the session
        """
        if not self._initialized:
            self.initialize()
            
        return self.SessionLocal()
    
    def execute_raw_sql(self, sql: str, params: dict = None):
        """Execute raw SQL query"""
        if not self._initialized:
            self.initialize()
            
        with self.engine.connect() as connection:
            result = connection.execute(sql, params or {})
            connection.commit()
            return result
    
    def get_table_stats(self) -> dict:
        """Get statistics about database tables"""
        if not self._initialized:
            self.initialize()
            
        stats = {}
        
        with self.get_session() as session:
            for table in Base.metadata.tables.values():
                try:
                    count = session.execute(f"SELECT COUNT(*) FROM {table.name}").scalar()
                    stats[table.name] = {"row_count": count}
                except Exception as e:
                    stats[table.name] = {"error": str(e)}
        
        return stats
    
    def close(self):
        """Close database connections"""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connections closed")
            self._initialized = False


# Global database manager instance
db_manager = DatabaseManager()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI to get database session
    
    Usage in FastAPI:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    with db_manager.get_session() as session:
        yield session


# Alembic migration helpers
def init_alembic():
    """Initialize Alembic for database migrations"""
    alembic_cfg = Config("alembic.ini")
    command.init(alembic_cfg, "migrations")
    logger.info("Alembic initialized")


def create_migration(message: str):
    """Create a new migration"""
    alembic_cfg = Config("alembic.ini")
    command.revision(alembic_cfg, autogenerate=True, message=message)
    logger.info(f"Migration created: {message}")


def run_migrations():
    """Run pending migrations"""
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    logger.info("Migrations completed")


def rollback_migration(revision: str = "-1"):
    """Rollback migrations"""
    alembic_cfg = Config("alembic.ini")
    command.downgrade(alembic_cfg, revision)
    logger.info(f"Rolled back to revision: {revision}")


# CLI commands for database management
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python connection.py [create|drop|stats|migrate]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "create":
        db_manager.create_tables()
        print("Tables created successfully")
    
    elif command == "drop":
        response = input("Are you sure you want to drop all tables? (yes/no): ")
        if response.lower() == "yes":
            db_manager.drop_tables()
            print("Tables dropped successfully")
        else:
            print("Operation cancelled")
    
    elif command == "stats":
        stats = db_manager.get_table_stats()
        print("\nDatabase Statistics:")
        print("-" * 40)
        for table, info in stats.items():
            if "error" in info:
                print(f"{table}: Error - {info['error']}")
            else:
                print(f"{table}: {info['row_count']} rows")
    
    elif command == "migrate":
        if len(sys.argv) < 3:
            print("Usage: python connection.py migrate [init|create|run|rollback]")
            sys.exit(1)
        
        migrate_cmd = sys.argv[2]
        
        if migrate_cmd == "init":
            init_alembic()
        elif migrate_cmd == "create":
            message = input("Enter migration message: ")
            create_migration(message)
        elif migrate_cmd == "run":
            run_migrations()
        elif migrate_cmd == "rollback":
            revision = sys.argv[3] if len(sys.argv) > 3 else "-1"
            rollback_migration(revision)
        else:
            print(f"Unknown migration command: {migrate_cmd}")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)