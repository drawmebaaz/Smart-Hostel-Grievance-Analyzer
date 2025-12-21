#!/usr/bin/env python3
"""
Database Initialization Script
Day 6.1 - Create database and tables
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.db.session import init_db, close_db
from app.utils.logger import get_logger

logger = get_logger(__name__)


def main():
    """Initialize database"""
    try:
        logger.info("=" * 60)
        logger.info("DATABASE INITIALIZATION - DAY 6")
        logger.info("=" * 60)
        
        # Create data directory if it doesn't exist
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        logger.info(f"Data directory: {data_dir.absolute()}")
        
        # Initialize database
        logger.info("Creating database tables...")
        init_db()
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ DATABASE INITIALIZED SUCCESSFULLY")
        logger.info("=" * 60)
        logger.info("\nTables created:")
        logger.info("  - issues")
        logger.info("  - complaints")
        logger.info("\nReady to process complaints with persistence!")
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {str(e)}")
        sys.exit(1)
    finally:
        close_db()


if __name__ == "__main__":
    main()