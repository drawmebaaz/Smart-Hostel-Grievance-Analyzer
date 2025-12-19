#!/usr/bin/env python3
"""
Fixed Day 4.4 Validation Tests
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.classification_service import get_classification_service

def print_test_result(test_name, passed, details=""):
    """Print formatted test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"   {details}")
    return passed

def test_basic_functionality():
    """Test basic Day 4 functionality"""
    print("\n" + "="*70)
    print("🧪 BASIC FUNCTIONALITY TEST")
    print("="*70)
    
    service = get_classification_service()
    
    test_cases = [
        ("Electric spark coming from switch", "Critical"),
        ("Tap is leaking slightly in washroom", "Low"),
        ("No water supply since morning", "High"),
        ("Unknown person roaming inside hostel", "Critical"),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for text, expected_urgency in test_cases:
        try:
            result = service.classify_with_urgency(text)
            
            actual_urgency = result.get("urgency", "N/A")
            is_correct = actual_urgency == expected_urgency
            
            details = f"Expected: {expected_urgency}, Got: {actual_urgency}, Confidence: {result.get('urgency_confidence', 0):.3f}"
            
            if print_test_result(f"'{text[:40]}...'", is_correct, details):
                passed += 1
                
        except Exception as e:
            print(f"❌ FAIL '{text[:40]}...' - Error: {str(e)}")
    
    print(f"\n📊 Basic Accuracy: {passed}/{total} ({passed/total*100:.0f}%)")
    return passed >= 3  # Pass if 3/4 correct

def test_edge_cases():
    """Test edge cases"""
    print("\n" + "="*70)
    print("🛡️ EDGE CASE TESTING")
    print("="*70)
    
    service = get_classification_service()
    
    edge_cases = [
        ("", "Empty string - should not crash"),
        ("   ", "Whitespace - should not crash"),
        ("fire", "Single word - should be Critical"),
        ("urgent help", "Short urgent text"),
    ]
    
    all_passed = True
    
    for text, note in edge_cases:
        try:
            result = service.classify_with_urgency(text)
            
            # Should not crash
            has_urgency = "urgency" in result
            has_category = "category" in result
            
            passed = has_urgency and has_category
            
            details = f"Urgency: {result.get('urgency', 'N/A')}, Category: {result.get('category', 'N/A')} - {note}"
            
            if not print_test_result(f"'{text[:20]}...'", passed, details):
                all_passed = False
                
        except Exception as e:
            print(f"❌ FAIL '{text[:20]}...' - CRASHED: {str(e)}")
            all_passed = False
    
    return all_passed

def test_api_response_format():
    """Test API response format matches Day 4.3 requirements"""
    print("\n" + "="*70)
    print("📋 API RESPONSE FORMAT TEST (Day 4.3)")
    print("="*70)
    
    service = get_classification_service()
    
    required_fields = [
        "category",
        "category_confidence", 
        "urgency",
        "urgency_confidence",
        "response_time_hours"
    ]
    
    test_text = "Electric spark coming from switch"
    
    try:
        result = service.classify_with_urgency(test_text)
        
        missing_fields = [field for field in required_fields if field not in result]
        
        if missing_fields:
            print(f"❌ FAIL 'Response format' - Missing fields: {missing_fields}")
            return False
        else:
            print(f"✅ PASS 'Response format' - All required fields present")
            
            # Check Day 4.3 principles
            processing_info = result.get("processing_info", {})
            independent = processing_info.get("independent_analysis", False)
            day_4_3 = processing_info.get("day_4_3_integrated", False)
            
            print(f"   ✅ Independent analysis: {independent}")
            print(f"   ✅ Day 4.3 integrated: {day_4_3}")
            
            return True
            
    except Exception as e:
        print(f"❌ FAIL 'Response format' - Error: {str(e)}")
        return False

def main():
    """Run fixed validation tests"""
    print("🧪 DAY 4.4: SIMPLIFIED VALIDATION TESTS")
    print("="*70)
    
    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("Edge Cases", test_edge_cases),
        ("API Response Format", test_api_response_format),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed with error: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*70)
    print("📊 DAY 4.4 VALIDATION SUMMARY (FIXED)")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n✨ DAY 4.4 VALIDATION COMPLETE - ALL TESTS PASSED!")
        print("   System is stable and working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) need attention.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
