#!/usr/bin/env python3
"""
Test hostel-category integrity - P0 bug fix verification
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.issue_service import get_issue_service
from app.issues.issue_manager import get_issue_manager

def test_hostel_category_integrity():
    """Test that complaints never cross hostel/category boundaries"""
    print("🔒 TESTING HOSTEL-CATEGORY INTEGRITY (P0 BUG FIX)")
    print("=" * 70)
    
    service = get_issue_service()
    manager = get_issue_manager()
    
    # Reset system
    manager.reset()
    
    print("\n1. Creating BH-3 Water issue...")
    result1 = service.process_complaint(
        text="No water in BH-3",
        hostel="BH-3"
    )
    
    print(f"   Issue created: {result1['issue_aggregation']['issue_id']}")
    print(f"   Hostel: BH-3, Category: {result1['classification']['category']}")
    
    print("\n2. Adding to same issue (should work)...")
    result2 = service.process_complaint(
        text="Water problem BH-3",
        hostel="BH-3"  # Same hostel
    )
    
    print(f"   Same issue: {result1['issue_aggregation']['issue_id'] == result2['issue_aggregation']['issue_id']}")
    
    print("\n3. Creating GH-1 Water issue (different hostel)...")
    result3 = service.process_complaint(
        text="No water in GH-1",
        hostel="GH-1"  # Different hostel
    )
    
    print(f"   New issue: {result3['issue_aggregation']['issue_id']}")
    print(f"   Different from BH-3 issue: {result1['issue_aggregation']['issue_id'] != result3['issue_aggregation']['issue_id']}")
    
    print("\n4. Creating BH-3 Electricity issue (different category)...")
    result4 = service.process_complaint(
        text="Electricity cut BH-3",
        hostel="BH-3"
    )
    
    print(f"   New issue: {result4['issue_aggregation']['issue_id']}")
    print(f"   Different from Water issue: {result1['issue_aggregation']['issue_id'] != result4['issue_aggregation']['issue_id']}")
    
    # Check statistics
    print("\n5. Verifying system integrity...")
    stats = manager.get_statistics()
    
    print(f"   Total issues: {stats['total_issues']} (expected: 3)")
    print(f"   Cross-hostel attempts: {stats['consistency_checks']['cross_hostel_attempts']} (must be 0)")
    print(f"   Cross-category attempts: {stats['consistency_checks']['cross_category_attempts']} (must be 0)")
    print(f"   System consistent: {stats['consistency_checks']['consistent']}")
    
    # Manual verification
    print("\n6. Manual verification of each issue:")
    for issue_id, issue in manager.issues.items():
        print(f"\n   Issue: {issue_id}")
        print(f"   Hostel: {issue.hostel}, Category: {issue.category}")
        print(f"   Complaints: {issue.complaint_count}")
        
        # Check each complaint
        for i, complaint in enumerate(issue.complaints, 1):
            hostel_ok = complaint.hostel == issue.hostel
            category_ok = complaint.category == issue.category
            print(f"   Complaint {i}: {complaint.id[:8]}...")
            print(f"     Hostel match: {hostel_ok} ({complaint.hostel})")
            print(f"     Category match: {category_ok} ({complaint.category})")
            
            if not hostel_ok or not category_ok:
                print("     ⚠️  INTEGRITY VIOLATION!")
    
    # Final check
    all_good = stats['consistency_checks']['consistent']
    if all_good:
        print("\n✅ HOSTEL-CATEGORY INTEGRITY PASSED!")
        print("   No cross-boundary complaints detected.")
    else:
        print("\n❌ HOSTEL-CATEGORY INTEGRITY FAILED!")
        print("   Cross-boundary complaints detected!")
    
    return all_good

if __name__ == "__main__":
    success = test_hostel_category_integrity()
    sys.exit(0 if success else 1)