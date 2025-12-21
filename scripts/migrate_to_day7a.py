#!/usr/bin/env python3
"""
Day 7A Migration Script
Upgrades database schema with integrity constraints and indexes
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.db.session import engine, close_db
from app.db.base import Base
from app.utils.logger import get_logger

logger = get_logger(__name__)


def migrate_to_day7a():
    """
    Migrate database to Day 7A schema
    
    ⚠️  WARNING: This will DROP and RECREATE all tables!
    Only use in development or with proper backup.
    """
    try:
        logger.info("=" * 60)
        logger.info("DAY 7A MIGRATION - SCHEMA UPGRADE")
        logger.info("=" * 60)
        
        logger.warning("\n⚠️  This will DROP all existing tables!")
        logger.warning("⚠️  All data will be lost!")
        
        response = input("\nContinue? (type 'YES' to proceed): ")
        
        if response != "YES":
            logger.info("Migration cancelled")
            return
        
        # Drop all tables
        logger.info("\n1️⃣ Dropping existing tables...")
        Base.metadata.drop_all(bind=engine)
        logger.info("✓ Tables dropped")
        
        # Create new tables with Day 7A enhancements
        logger.info("\n2️⃣ Creating tables with Day 7A schema...")
        Base.metadata.create_all(bind=engine)
        logger.info("✓ Tables created with:")
        logger.info("   - Unique constraints")
        logger.info("   - Check constraints")
        logger.info("   - Foreign key constraints")
        logger.info("   - Performance indexes")
        
        # Verify schema
        logger.info("\n3️⃣ Verifying schema...")
        from sqlalchemy import inspect
        inspector = inspect(engine)
        
        tables = inspector.get_table_names()
        logger.info(f"✓ Found {len(tables)} tables: {', '.join(tables)}")
        
        # Check issues table
        issues_indexes = inspector.get_indexes("issues")
        logger.info(f"✓ Issues table has {len(issues_indexes)} indexes")
        
        # Check complaints table
        complaints_indexes = inspector.get_indexes("complaints")
        logger.info(f"✓ Complaints table has {len(complaints_indexes)} indexes")
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ DAY 7A MIGRATION COMPLETE")
        logger.info("=" * 60)
        
        logger.info("\nDay 7A Features Enabled:")
        logger.info("  ✅ Database integrity constraints (7A.1)")
        logger.info("  ✅ Performance indexes (7A.2)")
        logger.info("  ✅ Row-level locking support (7A.3)")
        logger.info("  ✅ Transaction safety (7A.3)")
        logger.info("  ✅ Graceful degradation (7A.4)")
        
        logger.info("\nNext steps:")
        logger.info("  1. Test with: python scripts/test_day7a.py")
        logger.info("  2. Start server: python -m app.main")
        logger.info("  3. Monitor metrics: GET /admin/metrics")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {str(e)}")
        sys.exit(1)
    finally:
        close_db()


if __name__ == "__main__":
    migrate_to_day7a()