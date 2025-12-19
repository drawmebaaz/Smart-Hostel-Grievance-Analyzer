#!/usr/bin/env python3
"""
Day 4.4 Validation & Edge Case Hardening Tests
Validates: Cross-language consistency, independence, confidence sanity
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

def test_cross_language_consistency():
    """
    Test 1: Cross-language consistency
    Same meaning → same urgency, regardless of language
    """
    print("\n" + "="*70)
    print("🔤 TEST 1: CROSS-LANGUAGE CONSISTENCY")
    print("="*70)
    
    service = get_classification_service()
    
    # Test pairs: (English, Hindi, Expected Urgency)
    test_pairs = [
        # LOW urgency
        ("Tap is leaking slightly", "Nal se thoda pani leak ho raha hai", "Low"),
        
        # MEDIUM urgency  
        ("WiFi not working properly since yesterday", "Kal se wifi theek se kaam nahi kar raha", "Medium"),
        
        # HIGH urgency
        ("No water supply since morning", "Subah se pani nahi aa raha", "High"),
        
        # CRITICAL urgency
        ("Electric spark coming from switch", "Switch se chingari nikal rahi hai", "Critical"),
    ]
    
    passed_tests = 0
    total_tests = 0
    
    for eng, hindi, expected_urgency in test_pairs:
        total_tests += 2
        
        # Test English
        eng_result = service.classify_complaint(eng)
        eng_passed = eng_result["urgency"] == expected_urgency
        eng_conf = eng_result["urgency_confidence"]
        
        # Test Hindi
        hindi_result = service.classify_complaint(hindi)
        hindi_passed = hindi_result["urgency"] == expected_urgency
        hindi_conf = hindi_result["urgency_confidence"]
        
        # Both must pass
        pair_passed = eng_passed and hindi_passed
        
        details = f"Eng: {eng_result['urgency']}({eng_conf:.2f}), Hindi: {hindi_result['urgency']}({hindi_conf:.2f}), Expected: {expected_urgency}"
        
        if print_test_result(f"'{eng[:30]}...' / '{hindi[:30]}...'", pair_passed, details):
            passed_tests += 2
    
    accuracy = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    print(f"\n📊 Cross-language Accuracy: {accuracy:.1f}% ({passed_tests}/{total_tests})")
    
    return accuracy >= 80  # Pass if 80%+ accuracy

def test_category_urgency_independence():
    """
    Test 2: Category vs Urgency independence
    Same category should have different urgencies
    """
    print("\n" + "="*70)
    print("🔗 TEST 2: CATEGORY-URGENCY INDEPENDENCE")
    print("="*70)
    
    service = get_classification_service()
    
    # All Water-related, but different urgencies
    water_cases = [
        ("Tap is leaking slightly", "Water", "Low"),
        ("No water supply since morning", "Water", "High"),
        ("Water leakage near electric board", "Water", "Critical"),
    ]
    
    passed_tests = 0
    
    for text, expected_category, expected_urgency in water_cases:
        result = service.classify_complaint(text, detailed=True)
        
        cat_match = result["category"] == expected_category
        urg_match = result["urgency"] == expected_urgency
        
        passed = cat_match and urg_match
        
        details = f"Category: {result['category']}({cat_match}), Urgency: {result['urgency']}({urg_match})"
        
        if print_test_result(f"'{text[:40]}...'", passed, details):
            passed_tests += 1
    
    print(f"\n📊 Independence Test: {passed_tests}/{len(water_cases)} passed")
    
    # Success: Not all same urgency
    urgencies = [service.classify_complaint(t[0])["urgency"] for t in water_cases]
    unique_urgencies = len(set(urgencies))
    
    independence_passed = unique_urgencies > 1  # More than 1 unique urgency
    print(f"   Unique urgencies: {unique_urgencies} ({'✅ Independent' if independence_passed else '❌ Coupled'})")
    
    return independence_passed and passed_tests >= 2

def test_boundary_ambiguity():
    """
    Test 3: Boundary ambiguity (hard cases)
    """
    print("\n" + "="*70)
    print("🎯 TEST 3: BOUNDARY AMBIGUITY (HARD CASES)")
    print("="*70)
    
    service = get_classification_service()
    
    ambiguous_cases = [
        ("Room fan not working", "Should not be Critical"),
        ("Internet down during exams", "Time-sensitive, maybe High"),
        ("Bathroom is very dirty", "Hygiene, maybe Medium"),
        ("Street light near hostel is off", "Safety-ish, maybe Medium/High"),
    ]
    
    print("Testing ambiguous cases (lower confidence expected):")
    
    for text, note in ambiguous_cases:
        result = service.classify_complaint(text)
        
        # Check confidence is reasonable (not too high for ambiguous)
        conf = result["urgency_confidence"]
        reasonable_conf = 0.1 <= conf <= 0.6  # Shouldn't be too confident
        
        details = f"Urgency: {result['urgency']}, Confidence: {conf:.2f} ({'✅ Reasonable' if reasonable_conf else '❌ Too confident'}) - {note}"
        
        print_test_result(f"'{text}'", reasonable_conf, details)
    
    # Overall test passes if no Critical for non-safety
    non_safety_results = [service.classify_complaint(t[0]) for t in ambiguous_cases[:3]]
    critical_count = sum(1 for r in non_safety_results if r["urgency"] == "Critical")
    
    safety_appropriate = critical_count == 0
    print(f"\n📊 Safety appropriateness: {'✅ No false Criticals' if safety_appropriate else f'❌ {critical_count} false Critical(s)'}")
    
    return safety_appropriate

def test_confidence_sanity():
    """
    Test 4: Confidence sanity checks
    """
    print("\n" + "="*70)
    print("📈 TEST 4: CONFIDENCE SANITY CHECKS")
    print("="*70)
    
    service = get_classification_service()
    
    test_cases = [
        ("fire in kitchen", "Critical - should have high confidence"),
        ("tap leaking slightly", "Low - moderate confidence"),
        ("no water since morning", "High - moderate confidence"),
        ("something is wrong", "Vague - lower confidence"),
    ]
    
    confidences = []
    
    for text, note in test_cases:
        result = service.classify_complaint(text, detailed=True)
        conf = result["urgency_confidence"]
        confidences.append(conf)
        
        # Check confidence in reasonable range
        in_range = 0 <= conf <= 1
        
        details = f"Confidence: {conf:.3f} ({'✅ In range' if in_range else '❌ Out of range'}) - {note}"
        
        print_test_result(f"'{text}'", in_range, details)
    
    # Check distribution
    avg_conf = sum(confidences) / len(confidences)
    max_conf = max(confidences)
    min_conf = min(confidences)
    
    print(f"\n📊 Confidence Statistics:")
    print(f"   Average: {avg_conf:.3f}")
    print(f"   Range: {min_conf:.3f} - {max_conf:.3f}")
    print(f"   Spread: {max_conf - min_conf:.3f}")
    
    # Sanity checks
    not_all_same = max_conf - min_conf > 0.1
    reasonable_avg = 0.2 <= avg_conf <= 0.8
    critical_higher = False
    
    # Check if Critical has higher confidence than Low (optional)
    if len(confidences) >= 2:
        critical_higher = confidences[0] > confidences[1]  # fire > tap leak
    
    print(f"\n📊 Sanity Checks:")
    print(f"   Not all same: {'✅' if not_all_same else '❌'}")
    print(f"   Reasonable average: {'✅' if reasonable_avg else '❌'}")
    if critical_higher:
        print(f"   Critical > Low confidence: ✅")
    
    return not_all_same and reasonable_avg

def test_edge_cases_hardening():
    """
    Test 5: Edge case hardening
    """
    print("\n" + "="*70)
    print("🛡️ TEST 5: EDGE CASE HARDENING")
    print("="*70)
    
    service = get_classification_service()
    
    edge_cases = [
        ("", "Empty string - should handle gracefully"),
        ("   ", "Whitespace only - should handle gracefully"),
        ("a", "Single character - edge case"),
        ("fire", "Single word - should be Critical"),
        ("urgent help needed now immediately emergency", "Many urgency words"),
    ]
    
    all_passed = True
    
    for text, note in edge_cases:
        try:
            result = service.classify_complaint(text)
            
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

def main():
    """Run all Day 4.4 validation tests"""
    print("🧪 DAY 4.4: COMPREHENSIVE VALIDATION & EDGE CASE HARDENING")
    print("="*70)
    
    tests = [
        ("Cross-language Consistency", test_cross_language_consistency),
        ("Category-Urgency Independence", test_category_urgency_independence),
        ("Boundary Ambiguity", test_boundary_ambiguity),
        ("Confidence Sanity", test_confidence_sanity),
        ("Edge Case Hardening", test_edge_cases_hardening),
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
    print("📊 DAY 4.4 VALIDATION SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n✨ DAY 4.4 VALIDATION COMPLETE - ALL TESTS PASSED!")
        print("   System is stable, sane, multilingual, and safe.")
    else:
        print(f"\n⚠️  {total - passed} test(s) need attention.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
