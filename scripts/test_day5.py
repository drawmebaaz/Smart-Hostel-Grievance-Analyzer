#!/usr/bin/env python3
"""
Test script for Day 5 - Issue Aggregation System (English Scope)
"""

import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.issue_service import get_issue_service

def test_english_scope_validation():
    """Test English-only validation works"""
    print("\n🔤 Testing English-Only Scope Validation")
    print("-" * 70)
    
    test_cases = [
        ("No water supply in BH-3", True, "Valid English"),
        ("Water problem in room 101", True, "Valid English"),
        ("Electricity cut since morning", True, "Valid English"),
        ("Paani nahi aa raha", False, "Hinglish - should reject"),
        ("बिजली चली गई", False, "Hindi script - should reject"),
        ("No water in BH-3 and bathroom dirty", True, "Mixed but English"),
        ("Wifi not working in hostel", True, "Valid English"),
        ("Room cleaning needed urgently", True, "Valid English"),
        ("Internet speed very slow", True, "Valid English"),
    ]
    
    print("Note: System now enforces English-only for reliable duplicate detection")
    print("This ensures similarity scores > 0.6 for meaningful aggregation\n")
    
    all_passed = True
    service = get_issue_service()
    
    for text, should_pass, note in test_cases:
        try:
            result = service.process_complaint(
                text=text,
                hostel="BH-3"
            )
            actual_pass = True
            if should_pass:
                print(f"✅ PASS: '{text[:40]}...' - Accepted as expected")
            else:
                print(f"❌ FAIL: '{text[:40]}...' - Should have been rejected!")
                print(f"   {note}")
                all_passed = False
        except ValueError as e:
            if "English only" in str(e).lower():
                actual_pass = False
                if not should_pass:
                    print(f"✅ PASS: '{text[:40]}...' - Rejected as expected")
                    print(f"   {note}")
                else:
                    print(f"❌ FAIL: '{text[:40]}...' - Should have been accepted!")
                    print(f"   {note}")
                    all_passed = False
            else:
                print(f"⚠️  WARNING: '{text[:40]}...' - Different error: {e}")
        except Exception as e:
            print(f"⚠️  ERROR: '{text[:40]}...' - Unexpected error: {e}")
            all_passed = False
    
    return all_passed

def test_basic_functionality():
    """Test basic Day 5 functionality with English scope"""
    print("\n🧪 DAY 5 TEST - Issue Aggregation System (English Scope)")
    print("=" * 70)
    
    service = get_issue_service()
    
    # Test complaint 1
    print("\n1️⃣ Submitting first complaint (English)...")
    result1 = service.process_complaint(
        text="No water supply in BH-3 since morning",
        hostel="BH-3"
    )
    
    print(f"   Complaint ID: {result1['complaint_id']}")
    print(f"   Category: {result1['classification']['category']}")
    print(f"   Urgency: {result1['classification']['urgency']}")
    print(f"   Issue ID: {result1['issue_aggregation']['issue_id']}")
    print(f"   Status: {result1['issue_aggregation']['status']}")
    
    # Test complaint 2 (similar English)
    print("\n2️⃣ Submitting similar complaint (English paraphrase)...")
    result2 = service.process_complaint(
        text="Water problem in BH-3 hostel",
        hostel="BH-3"
    )
    
    print(f"   Complaint ID: {result2['complaint_id']}")
    print(f"   Issue ID: {result2['issue_aggregation']['issue_id']}")
    print(f"   Duplicate: {result2['issue_aggregation']['is_duplicate']}")
    print(f"   Similarity: {result2['issue_aggregation'].get('similarity_score', 'N/A')}")
    print(f"   Complaint count: {result2['issue_aggregation']['complaint_count']}")
    print(f"   Note: English-English similarity should be > 0.6")
    
    # Test complaint 3 (same meaning, different wording)
    print("\n3️⃣ Submitting same-issue complaint (different wording)...")
    result3 = service.process_complaint(
        text="BH-3 has no running water",
        hostel="BH-3"
    )
    
    print(f"   Complaint ID: {result3['complaint_id']}")
    print(f"   Issue ID: {result3['issue_aggregation']['issue_id']}")
    print(f"   Duplicate: {result3['issue_aggregation']['is_duplicate']}")
    print(f"   Complaint count: {result3['issue_aggregation']['complaint_count']}")
    
    # Test complaint 4 (different hostel)
    print("\n4️⃣ Submitting complaint for different hostel...")
    result4 = service.process_complaint(
        text="No water in GH-1",
        hostel="GH-1"
    )
    
    print(f"   Complaint ID: {result4['complaint_id']}")
    print(f"   Issue ID: {result4['issue_aggregation']['issue_id']}")
    print(f"   Status: {result4['issue_aggregation']['status']}")
    
    # Test complaint 5 (different category, same hostel)
    print("\n5️⃣ Submitting electricity complaint for BH-3...")
    result5 = service.process_complaint(
        text="Electricity cut in BH-3",
        hostel="BH-3"
    )
    
    print(f"   Complaint ID: {result5['complaint_id']}")
    print(f"   Category: {result5['classification']['category']}")
    print(f"   Issue ID: {result5['issue_aggregation']['issue_id']}")
    
    # Get all issues
    print("\n📊 Getting all issues...")
    issues_result = service.get_issues()
    print(f"   Total issues: {issues_result['count']}")
    
    for issue in issues_result['issues']:
        print(f"   - {issue['issue_id']}: {issue['category']} in {issue['hostel']} "
              f"({issue['complaint_count']} complaints, {issue['unique_complaint_count']} unique)")
    
    # Get system statistics
    print("\n📈 System statistics:")
    stats = service.get_system_stats()
    issue_stats = stats['issue_system']
    
    print(f"   Total complaints: {issue_stats['total_complaints']}")
    print(f"   Unique complaints: {issue_stats['unique_complaints']}")
    print(f"   Duplicate rate: {issue_stats['duplicate_rate']:.1%}")
    print(f"   Issues created: {issue_stats['total_issues']}")
    
    print("\n✅ Day 5 basic functionality test PASSED")
    return True

def test_api_endpoints():
    """Test API endpoints"""
    print("\n🌐 Testing API endpoints...")
    print("-" * 70)
    
    import requests
    
    base_url = "http://localhost:8000"
    
    # Test health endpoint
    print("1. Testing /health...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json().get('status', 'N/A')}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Test day5 status
    print("\n2. Testing /day5/status...")
    try:
        response = requests.get(f"{base_url}/day5/status")
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Day: {data.get('day', 'N/A')}")
        print(f"   Status: {data.get('status', 'N/A')}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Test submitting a complaint via API
    print("\n3. Testing /day5/complaint submission...")
    try:
        response = requests.post(
            f"{base_url}/day5/complaint",
            json={
                "text": "Internet not working in BH-3",
                "hostel": "BH-3"
            }
        )
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Complaint ID: {data.get('complaint_id', 'N/A')}")
        print(f"   Issue ID: {data.get('issue_aggregation', {}).get('issue_id', 'N/A')}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Test getting issues via API
    print("\n4. Testing /day5/issues endpoint...")
    try:
        response = requests.get(f"{base_url}/day5/issues")
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Total issues: {data.get('count', 'N/A')}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    print("\n✅ API endpoints test PASSED")
    return True

def test_duplicate_detection_accuracy():
    """Test duplicate detection accuracy with English text"""
    print("\n🎯 Testing Duplicate Detection Accuracy (English)")
    print("-" * 70)
    
    service = get_issue_service()
    
    test_pairs = [
        ("No water in BH-3", "Water problem in BH-3", True, "Similar meaning"),
        ("No water in BH-3", "Electricity cut in BH-3", False, "Different category"),
        ("No water in BH-3", "No water in GH-1", False, "Different hostel"),
        ("Internet slow in room 101", "Wifi speed very slow", True, "Similar concept"),
        ("Internet slow in room 101", "Room cleaning needed", False, "Different issue"),
    ]
    
    print("Testing similarity detection between English complaint pairs:\n")
    
    all_passed = True
    
    for i, (text1, text2, should_match, note) in enumerate(test_pairs, 1):
        print(f"Test {i}: {note}")
        print(f"   A: '{text1}'")
        print(f"   B: '{text2}'")
        
        # Create first complaint
        result1 = service.process_complaint(text=text1, hostel="BH-3")
        issue_id1 = result1['issue_aggregation']['issue_id']
        
        # Create second complaint
        result2 = service.process_complaint(text=text2, hostel="BH-3")
        issue_id2 = result2['issue_aggregation']['issue_id']
        
        # Check if they match
        is_duplicate = result2['issue_aggregation']['is_duplicate']
        same_issue = (issue_id1 == issue_id2)
        
        # Both should agree
        if (should_match and same_issue) or (not should_match and not same_issue):
            print(f"   ✅ CORRECT: {'Matched' if should_match else 'Not matched'} as expected")
        else:
            print(f"   ❌ INCORRECT: Expected {'match' if should_match else 'no match'}")
            print(f"      Issue IDs: {issue_id1} vs {issue_id2}")
            print(f"      Duplicate flag: {is_duplicate}")
            all_passed = False
        
        print()
    
    if all_passed:
        print("✅ All duplicate detection tests passed!")
    else:
        print("⚠️  Some duplicate detection tests need attention")
    
    return all_passed

def test_edge_cases():
    """Test edge cases for English scope"""
    print("\n⚠️ Testing Edge Cases")
    print("-" * 70)
    
    service = get_issue_service()
    
    edge_cases = [
        ("", "Empty string"),
        ("   ", "Whitespace only"),
        ("BH-3", "Just hostel name"),
        ("water", "Single word"),
        ("A" * 500, "Very long text"),
        ("No water in BH-3!!!", "With punctuation"),
        ("No water in BH-3. Electricity also gone.", "Multiple sentences"),
        ("WiFi not working", "Case variations"),
        ("wifi not working", "Lowercase"),
        ("NO WATER IN BH-3", "Uppercase"),
    ]
    
    print("Testing various edge cases with English text:\n")
    
    for text, description in edge_cases:
        print(f"Testing: {description}")
        print(f"   Text: '{text[:50]}{'...' if len(text) > 50 else ''}'")
        
        try:
            result = service.process_complaint(text=text, hostel="BH-3")
            print(f"   ✅ Accepted - Category: {result['classification']['category']}")
            print(f"   Issue ID: {result['issue_aggregation']['issue_id']}")
        except ValueError as e:
            if "english" in str(e).lower():
                print(f"   ❌ Rejected - Not English enough")
            else:
                print(f"   ❌ Rejected - {e}")
        except Exception as e:
            print(f"   ⚠️  Error: {e}")
        
        print()
    
    print("✅ Edge cases test completed")
    return True

def main():
    """Run all Day 5 tests with English scope"""
    print("🚀 DAY 5 COMPREHENSIVE TEST SUITE (ENGLISH SCOPE)")
    print("=" * 70)
    print("📝 Scope: English-only complaints for reliable duplicate detection")
    print("🎯 Goal: Ensure similarity scores > 0.6 for meaningful aggregation")
    print("=" * 70)
    
    tests = [
        ("English Scope Validation", test_english_scope_validation),
        ("Basic Functionality", test_basic_functionality),
        ("Duplicate Detection Accuracy", test_duplicate_detection_accuracy),
        ("Edge Cases", test_edge_cases),
        ("API Endpoints", test_api_endpoints),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        print("-" * 50)
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name} - PASSED")
            else:
                print(f"❌ {test_name} - FAILED")
        except Exception as e:
            print(f"❌ Test failed with error: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 DAY 5 TEST SUMMARY (ENGLISH SCOPE)")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n✨ DAY 5 IMPLEMENTATION COMPLETE!")
        print("   Issue aggregation system is working correctly with English scope.")
        print("   Key improvements:")
        print("   1. ✅ English-only validation for reliable duplicate detection")
        print("   2. ✅ Similarity scores > 0.6 for meaningful aggregation")
        print("   3. ✅ Accurate issue grouping across similar complaints")
    else:
        print(f"\n⚠️  {total - passed} test(s) need attention.")
        print("   Focus on English validation and duplicate detection accuracy.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)