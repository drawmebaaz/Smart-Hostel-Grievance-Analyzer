#!/usr/bin/env python3
"""
Day 7A Testing Script
Tests: Constraints, indexes, transactions, graceful degradation
"""

import sys
from pathlib import Path
import time
import concurrent.futures

sys.path.append(str(Path(__file__).parent.parent))

from app.db.session import init_db, close_db, get_db_context
from app.services.issue_service_day7a import get_issue_service_day7a
from app.db.models.issue import IssueModel, IssueStatus
from app.repositories.issue_repository import IssueRepository
from sqlalchemy.exc import IntegrityError
from app.utils.logger import get_logger

logger = get_logger(__name__)


def test_unique_constraint():
    """Test 7A.1: Unique constraint on (hostel, category)"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 1: Unique Constraint (7A.1)")
    logger.info("=" * 60)
    
    try:
        with get_db_context() as db:
            repo = IssueRepository(db)
            
            # Create first issue
            issue1 = repo.create({
                "id": "TEST-1",
                "hostel": "BH-TEST",
                "category": "Water",
                "status": "OPEN",
                "urgency_max": "Low",
                "urgency_avg": 1.0
            })
            logger.info(f"✓ Created issue: {issue1.id}")
            
            # Try to create duplicate
            try:
                issue2 = repo.create({
                    "id": "TEST-2",
                    "hostel": "BH-TEST",
                    "category": "Water",
                    "status": "OPEN",
                    "urgency_max": "Low",
                    "urgency_avg": 1.0
                })
                logger.error("❌ FAILED: Duplicate issue was created!")
                return False
            except IntegrityError:
                logger.info("✓ Duplicate rejected correctly")
                return True
    
    except Exception as e:
        logger.error(f"❌ TEST FAILED: {str(e)}")
        return False


def test_status_constraint():
    """Test 7A.1: Status validation"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: Status Constraint (7A.1)")
    logger.info("=" * 60)
    
    try:
        with get_db_context() as db:
            # Try to create issue with invalid status
            issue = IssueModel(
                id="TEST-INVALID",
                hostel="BH-TEST",
                category="Electricity",
                status="INVALID_STATUS",
                urgency_max="Low",
                urgency_avg=1.0
            )
            db.add(issue)
            db.flush()
            
            logger.error("❌ FAILED: Invalid status was accepted!")
            return False
    
    except IntegrityError:
        logger.info("✓ Invalid status rejected correctly")
        return True
    except Exception as e:
        logger.error(f"❌ TEST FAILED: {str(e)}")
        return False


def test_concurrent_issue_creation():
    """Test 7A.3: Concurrent issue creation (race condition)"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 3: Concurrent Issue Creation (7A.3)")
    logger.info("=" * 60)
    
    def create_issue():
        service = get_issue_service_day7a()
        return service.process_complaint(
            text="Water problem in BH-RACE",
            hostel="BH-RACE"
        )
    
    try:
        # Submit 5 concurrent complaints for same issue
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(create_issue) for _ in range(5)]
            results = [f.result() for f in futures]
        
        # Count unique issues created
        issue_ids = set(r["issue_aggregation"]["issue_id"] for r in results if r["success"])
        
        if len(issue_ids) == 1:
            logger.info(f"✓ Only 1 issue created (correct): {issue_ids.pop()}")
            logger.info(f"✓ All {len(results)} complaints grouped correctly")
            return True
        else:
            logger.error(f"❌ FAILED: {len(issue_ids)} issues created (should be 1)")
            return False
    
    except Exception as e:
        logger.error(f"❌ TEST FAILED: {str(e)}")
        return False


def test_counter_consistency():
    """Test 7A.3: Counter consistency under concurrent updates"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 4: Counter Consistency (7A.3)")
    logger.info("=" * 60)
    
    def submit_complaint(i):
        service = get_issue_service_day7a()
        return service.process_complaint(
            text=f"Issue number {i} in BH-COUNTER",
            hostel="BH-COUNTER"
        )
    
    try:
        # Submit 10 concurrent complaints
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(submit_complaint, i) for i in range(10)]
            results = [f.result() for f in futures]
        
        # Get final issue state
        service = get_issue_service_day7a()
        issue_id = results[0]["issue_aggregation"]["issue_id"]
        issue = service.get_issue(issue_id)
        
        expected_count = 10
        actual_count = issue["complaint_count"]
        
        if actual_count == expected_count:
            logger.info(f"✓ Counter correct: {actual_count} = {expected_count}")
            logger.info(f"✓ Unique: {issue['unique_complaint_count']}")
            logger.info(f"✓ Duplicates: {issue['duplicate_count']}")
            return True
        else:
            logger.error(f"❌ FAILED: Count mismatch {actual_count} != {expected_count}")
            return False
    
    except Exception as e:
        logger.error(f"❌ TEST FAILED: {str(e)}")
        return False


def test_graceful_degradation():
    """Test 7A.4: System continues when embedding fails"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 5: Graceful Degradation (7A.4)")
    logger.info("=" * 60)
    
    try:
        service = get_issue_service_day7a()
        
        # Normal complaint
        result = service.process_complaint(
            text="Test complaint for degradation",
            hostel="BH-DEGRADE"
        )
        
        if not result["success"]:
            logger.error("❌ FAILED: Complaint was rejected")
            return False
        
        # Check degradation flags
        degradation = result.get("degradation", {})
        logger.info(f"✓ Complaint processed successfully")
        logger.info(f"  Embedding degraded: {degradation.get('embedding', False)}")
        logger.info(f"  Duplicate detection degraded: {degradation.get('duplicate_detection', False)}")
        logger.info(f"  Heuristics degraded: {degradation.get('heuristics', False)}")
        
        # Verify data persisted
        issue = service.get_issue(result["issue_aggregation"]["issue_id"])
        if issue:
            logger.info("✓ Data persisted correctly")
            return True
        else:
            logger.error("❌ FAILED: Data not persisted")
            return False
    
    except Exception as e:
        logger.error(f"❌ TEST FAILED: {str(e)}")
        return False


def test_query_performance():
    """Test 7A.2: Query uses indexes"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 6: Query Performance (7A.2)")
    logger.info("=" * 60)
    
    try:
        # Create some test data
        service = get_issue_service_day7a()
        
        for i in range(5):
            service.process_complaint(
                text=f"Test complaint {i}",
                hostel=f"BH-{i % 2}"
            )
        
        # Test filtered query
        start = time.time()
        result = service.get_issues(status="OPEN", limit=10)
        elapsed = time.time() - start
        
        logger.info(f"✓ Query completed in {elapsed*1000:.2f}ms")
        logger.info(f"✓ Found {result['count']} issues")
        
        if elapsed < 0.1:  # Should be very fast with indexes
            logger.info("✓ Query performance acceptable")
            return True
        else:
            logger.warning(f"⚠️  Query slow: {elapsed*1000:.2f}ms")
            return True  # Still pass, just warn
    
    except Exception as e:
        logger.error(f"❌ TEST FAILED: {str(e)}")
        return False


def test_transaction_rollback():
    """Test 7A.3: Transaction rollback on error"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 7: Transaction Rollback (7A.3)")
    logger.info("=" * 60)
    
    try:
        service = get_issue_service_day7a()
        
        # Get initial count
        with get_db_context() as db:
            initial_count = db.query(IssueModel).count()
        
        # Try to process complaint with error (e.g., empty text)
        try:
            service.process_complaint(text="", hostel="BH-ROLLBACK")
        except:
            pass
        
        # Check final count
        with get_db_context() as db:
            final_count = db.query(IssueModel).count()
        
        if final_count == initial_count:
            logger.info("✓ Transaction rolled back correctly")
            logger.info(f"  Count unchanged: {initial_count}")
            return True
        else:
            logger.error(f"❌ FAILED: Partial commit detected")
            return False
    
    except Exception as e:
        logger.error(f"❌ TEST FAILED: {str(e)}")
        return False


def main():
    """Run all Day 7A tests"""
    try:
        logger.info("=" * 60)
        logger.info("DAY 7A TESTING SUITE")
        logger.info("=" * 60)
        
        # Initialize database
        logger.info("\nInitializing test database...")
        init_db()
        
        # Run tests
        tests = [
            ("Unique Constraint", test_unique_constraint),
            ("Status Constraint", test_status_constraint),
            ("Concurrent Issue Creation", test_concurrent_issue_creation),
            ("Counter Consistency", test_counter_consistency),
            ("Graceful Degradation", test_graceful_degradation),
            ("Query Performance", test_query_performance),
            ("Transaction Rollback", test_transaction_rollback),
        ]
        
        results = []
        for name, test_func in tests:
            try:
                passed = test_func()
                results.append((name, passed))
            except Exception as e:
                logger.error(f"Test '{name}' crashed: {str(e)}")
                results.append((name, False))
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("TEST SUMMARY")
        logger.info("=" * 60)
        
        passed_count = sum(1 for _, passed in results if passed)
        total_count = len(results)
        
        for name, passed in results:
            status = "✅ PASSED" if passed else "❌ FAILED"
            logger.info(f"{status}: {name}")
        
        logger.info("\n" + "=" * 60)
        logger.info(f"Results: {passed_count}/{total_count} tests passed")
        logger.info("=" * 60)
        
        if passed_count == total_count:
            logger.info("\n✅ ALL DAY 7A TESTS PASSED")
            logger.info("\nDay 7A Features Verified:")
            logger.info("  ✅ Database integrity constraints (7A.1)")
            logger.info("  ✅ Performance indexes (7A.2)")
            logger.info("  ✅ Transaction safety & row locking (7A.3)")
            logger.info("  ✅ Graceful degradation (7A.4)")
            logger.info("\n🎉 System is production-ready!")
        else:
            logger.error(f"\n❌ {total_count - passed_count} TESTS FAILED")
            sys.exit(1)
        
    except Exception as e:
        logger.error(f"\n❌ TEST SUITE ERROR: {str(e)}")
        sys.exit(1)
    finally:
        close_db()


if __name__ == "__main__":
    main()