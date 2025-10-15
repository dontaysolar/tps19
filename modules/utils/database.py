#!/usr/bin/env python3
"""TPS19 Database Utilities"""

import sqlite3
import threading
from contextlib import contextmanager
from typing import Optional, Generator
from pathlib import Path
from .config import config
from .logger import get_logger

logger = get_logger(__name__)


class DatabaseConnectionPool:
    """Simple connection pool for SQLite databases"""
    
    _pools = {}
    _lock = threading.Lock()
    
    @classmethod
    def get_connection(cls, db_name: str) -> sqlite3.Connection:
        """Get a database connection
        
        Args:
            db_name: Database filename (e.g., 'trading.db')
            
        Returns:
            SQLite connection
        """
        db_path = config.get_database_path(db_name)
        
        # Ensure parent directory exists
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create connection with proper settings
        conn = sqlite3.connect(
            str(db_path),
            check_same_thread=False,
            timeout=30.0
        )
        
        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON")
        
        # Set row factory for dict-like access
        conn.row_factory = sqlite3.Row
        
        return conn
    
    @classmethod
    @contextmanager
    def get_connection_context(cls, db_name: str) -> Generator[sqlite3.Connection, None, None]:
        """Context manager for database connections
        
        Usage:
            with DatabaseConnectionPool.get_connection_context('trading.db') as conn:
                cursor = conn.cursor()
                cursor.execute(...)
                conn.commit()
        
        Args:
            db_name: Database filename
            
        Yields:
            SQLite connection
        """
        conn = cls.get_connection(db_name)
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error in {db_name}: {e}")
            raise
        finally:
            conn.close()


@contextmanager
def get_db_connection(db_name: str) -> Generator[sqlite3.Connection, None, None]:
    """Convenience function for database connections
    
    Args:
        db_name: Database filename
        
    Yields:
        SQLite connection
    """
    with DatabaseConnectionPool.get_connection_context(db_name) as conn:
        yield conn


def init_database(db_name: str, schema_sql: str) -> bool:
    """Initialize a database with schema
    
    Args:
        db_name: Database filename
        schema_sql: SQL schema to execute
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with get_db_connection(db_name) as conn:
            cursor = conn.cursor()
            cursor.executescript(schema_sql)
            logger.info(f"Database {db_name} initialized successfully")
            return True
    except Exception as e:
        logger.error(f"Failed to initialize database {db_name}: {e}")
        return False
