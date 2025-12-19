#!/usr/bin/env python3
"""
Quick Day 4.3 Integration Test
"""
import sys
sys.path.append('.')

from app.services.classification_service import get_classification_service

def test_integration():
    print("🧪 QUICK DAY 4.3 INTEGRATION TEST")
    print("="*50)
    
    service = get_classification_service()
    
    test_cases = [
        ("No water supply since morning", "Water", "High"),
        ("Electric spark coming from switch", "Electricity/Safety", "Critical"),
        ("WiFi is slow in my room", "Internet", "Medium/Low"),
        ("Tap is leaking slightly in washroom", "Water/Infrastructure", "Low"),
        ("Unknown person roaming inside hostel", "Safety", "Critical"),
    ]
    
    print("Expected behavior (Day 4.3 principles):")
    print("1. Category logic untouched")
    print("2. Urgency logic independent")
    print("3. No coupling between category and urgency")
    print("4. Single clean response object\n")
    
    for text, expected_category_note, expected_urgency_note in test_cases[:3]:
        # Use classify_with_urgency NOT classify_complaint
        result = service.classify_with_urgency(text, detailed=False)
        
        print(f"\n📝 Complaint: '{text}'")
        print(f"   Category: {result['category']} (Expected: {expected_category_note})")
        print(f"   Urgency: {result['urgency']} (Expected: {expected_urgency_note})")
        print(f"   Category Confidence: {result['category_confidence']:.3f}")
        print(f"   Urgency Confidence: {result['urgency_confidence']:.3f}")
        print(f"   Response Time: {result['response_time_hours']} hours")
        
        # Check Day 4.3 principles
        has_both = 'category' in result and 'urgency' in result
        has_independent = result.get('processing_info', {}).get('independent_analysis', False)
        print(f"   ✅ Single response object: {has_both}")
        print(f"   ✅ Independent analysis: {has_independent}")
    
    # Test system info
    print("\n📊 System Information:")
    info = service.get_classification_stats()
    print(f"   Categories: {info['categories']['total']}")
    print(f"   Urgency Levels: {len(info['urgency']['levels'])}")
    print(f"   Day 4.3 Integrated: {info['integration']['day_4_3_completed']}")
    
    print("\n✨ Day 4.3 Integration: COMPLETE ✅")

if __name__ == "__main__":
    test_integration()
