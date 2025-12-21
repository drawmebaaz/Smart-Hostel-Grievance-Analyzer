#!/usr/bin/env python3
"""
Database session management
Day 6.1 & 7A - Engine and session factory with constraint enforcement
"""

import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator

from app.db.base import Base
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Database URL - defaults to SQLite in data directory
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/hostel_grievance.db")

# Create engine with optimized settings for SQLite
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL debugging
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)

# Day 7A: Enable SQLite constraints
if "sqlite" in DATABASE_URL:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")  # Better concurrency
        cursor.close()
        logger.debug("SQLite pragmas enabled: foreign_keys, WAL mode")

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """
    Initialize database - create all tables.
    Safe to call multiple times (idempotent).
    """
    try:
        # Import all models to register them
        from app.db.models import issue, complaint  # noqa
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI endpoints.
    Provides database session with automatic cleanup.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """
    Context manager for database sessions.
    Use in service layer.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def close_db():
    """Close database connections (for cleanup)"""
    engine.dispose()
    logger.info("Database connections closed")