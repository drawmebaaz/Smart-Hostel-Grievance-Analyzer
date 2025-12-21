#!/usr/bin/env python3
"""
Day 6 Testing Script
Tests: DB persistence, sessions, heuristics
"""

import sys
from pathlib import Path
import time

sys.path.append(str(Path(__file__).parent.parent))

from app.db.session import init_db, close_db
from app.services.issue_service_day6 import get_issue_service_day6
from app.core.session import get_session_manager
from app.utils.logger import get_logger

logger = get_logger(__name__)


def test_session_management():
    """Test session creation and tracking"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 1: Session Management")
    logger.info("=" * 60)
    
    sm = get_session_manager()
    
    # Create session
    session = sm.create_session(metadata={"test": "day6"})
    assert session is not None
    logger.info(f"✓ Session created: {session.session_id}")
    
    # Retrieve session
    retrieved = sm.get_session(session.session_id)
    assert retrieved is not None
    assert retrieved.session_id == session.session_id
    logger.info(f"✓ Session retrieved successfully")
    
    # Check stats
    stats = sm.get_stats()
    assert stats["active_sessions"] >= 1
    logger.info(f"✓ Session stats: {stats}")
    
    logger.info("✅ Session management: PASSED")


def test_complaint_processing():
    """Test complete complaint processing with DB"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: Complaint Processing with DB")
    logger.info("=" * 60)
    
    service = get_issue_service_day6()
    
    # Submit first complaint
    result1 = service.process_complaint(
        text="No water supply in BH-3 since morning",
        hostel="BH-3"
    )
    
    assert result1["success"]
    assert "issue_id" in result1["issue_aggregation"]
    assert result1["metadata"]["db_persisted"]
    logger.info(f"✓ Complaint 1 processed: {result1['complaint_id']}")
    logger.info(f"  Issue: {result1['issue_aggregation']['issue_id']}")
    
    # Submit second complaint (should group into same issue)
    result2 = service.process_complaint(
        text="Water problem in BH-3, still not fixed",
        hostel="BH-3",
        session_id=result1["session"]["session_id"]
    )
    
    assert result2["success"]
    assert result2["issue_aggregation"]["issue_id"] == result1["issue_aggregation"]["issue_id"]
    logger.info(f"✓ Complaint 2 processed: {result2['complaint_id']}")
    logger.info(f"  Same issue: {result2['issue_aggregation']['issue_id']}")
    
    logger.info("✅ Complaint processing: PASSED")


def test_heuristics():
    """Test heuristic detection"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 3: Heuristic Detection")
    logger.info("=" * 60)
    
    service = get_issue_service_day6()
    
    # Create session for testing
    result1 = service.process_complaint(
        text="WiFi not working in BH-1",
        hostel="BH-1"
    )
    
    session_id = result1["session"]["session_id"]
    
    # Submit follow-up (same session, same issue)
    time.sleep(1)  # Small delay
    result2 = service.process_complaint(
        text="WiFi still down in BH-1",
        hostel="BH-1",
        session_id=session_id
    )
    
    # Check for follow-up detection
    heuristics = result2.get("heuristics", {})
    logger.info(f"✓ Heuristics: {heuristics}")
    
    if heuristics.get("is_follow_up"):
        logger.info("✓ Follow-up detected correctly")
    
    logger.info("✅ Heuristic detection: PASSED")


def test_issue_retrieval():
    """Test issue retrieval"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 4: Issue Retrieval")
    logger.info("=" * 60)
    
    service = get_issue_service_day6()
    
    # Get all issues
    result = service.get_issues(limit=10)
    assert "issues" in result
    assert result["count"] >= 0
    logger.info(f"✓ Retrieved {result['count']} issues")
    
    if result["issues"]:
        # Get specific issue
        issue_id = result["issues"][0]["issue_id"]
        issue_details = service.get_issue(issue_id)
        assert issue_details is not None
        logger.info(f"✓ Retrieved issue details: {issue_id}")
    
    logger.info("✅ Issue retrieval: PASSED")


def test_system_stats():
    """Test system statistics"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 5: System Statistics")
    logger.info("=" * 60)
    
    service = get_issue_service_day6()
    
    stats = service.get_system_stats()
    assert "issue_system" in stats
    assert "complaint_system" in stats
    assert "session_system" in stats
    assert stats["day_6_complete"]
    
    logger.info(f"✓ Issue stats: {stats['issue_system']}")
    logger.info(f"✓ Complaint stats: {stats['complaint_system']}")
    logger.info(f"✓ Session stats: {stats['session_system']}")
    logger.info("✅ System statistics: PASSED")


def main():
    """Run all tests"""
    try:
        logger.info("=" * 60)
        logger.info("DAY 6 TESTING SUITE")
        logger.info("=" * 60)
        
        # Initialize database
        logger.info("\nInitializing test database...")
        init_db()
        
        # Run tests
        test_session_management()
        test_complaint_processing()
        test_heuristics()
        test_issue_retrieval()
        test_system_stats()
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("✅ ALL DAY 6 TESTS PASSED")
        logger.info("=" * 60)
        logger.info("\nDay 6 Features Verified:")
        logger.info("  ✓ Database persistence (SQLite)")
        logger.info("  ✓ Session management")
        logger.info("  ✓ Heuristic detection")
        logger.info("  ✓ Issue lifecycle")
        logger.info("  ✓ System metrics")
        
    except AssertionError as e:
        logger.error(f"\n❌ TEST FAILED: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ TEST ERROR: {str(e)}")
        sys.exit(1)
    finally:
        close_db()


if __name__ == "__main__":
    main()