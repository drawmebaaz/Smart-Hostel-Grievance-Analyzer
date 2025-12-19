#!/usr/bin/env python3
"""
Test script for Day 3 - Classification System
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.classification_service import get_classification_service

def run_tests():
    """Run classification tests"""
    service = get_classification_service()
    
    print("🧪 DAY 3 - CLASSIFICATION SYSTEM TEST")
    print("=" * 70)
    
    # Test cases covering different categories and languages
    test_cases = [
        ("paani nahi aa raha hostel me", "Water"),
        ("No water supply in hostel", "Water"),
        ("wifi ka issue hai room me", "Internet"),
        ("WiFi is very slow in my room", "Internet"),
        ("warden sunta hi nahi hai", "Administration"),
        ("warden is not responding to complaints", "Administration"),
        ("mess food is very bad quality", "Mess"),
        ("khana kharab hai mess me", "Mess"),
        ("light nahi hai room me", "Electricity"),
        ("bijli chali gayi hai", "Electricity"),
        ("washroom saaf nahi hai", "Hygiene"),
        ("bathroom is not cleaned", "Hygiene"),
        ("fan not working in room", "Infrastructure"),
        ("room ka fan kharab hai", "Infrastructure"),
        ("raat ko bahut shor hota hai", "Noise"),
        ("too much noise at night", "Noise"),
        ("unknown person near hostel gate", "Safety"),
        ("security guard not present", "Safety"),
        ("general inconvenience", "Others"),
        ("hostel facilities need improvement", "Others")
    ]
    
    results = []
    
    print("\n🔍 Classification Tests:")
    print("-" * 70)
    
    for text, expected_category in test_cases:
        result = service.classify_complaint(text)
        predicted = result["category"]
        confidence = result["confidence"]
        score = result["similarity_score"]
        
        is_correct = predicted == expected_category
        status = "✅" if is_correct else "❌"
        
        results.append({
            "text": text,
            "expected": expected_category,
            "predicted": predicted,
            "correct": is_correct,
            "confidence": confidence,
            "score": score
        })
        
        print(f"{status} '{text[:40]}...'")
        print(f"   Expected: {expected_category:15} | Predicted: {predicted:15}")
        print(f"   Confidence: {confidence:.3f} | Score: {score:.3f}")
    
    # Calculate accuracy
    correct = sum(1 for r in results if r["correct"])
    total = len(results)
    accuracy = correct / total if total > 0 else 0
    
    print(f"\n📊 Summary:")
    print(f"   Total tests: {total}")
    print(f"   Correct: {correct}")
    print(f"   Accuracy: {accuracy:.1%}")
    
    # Show confidence distribution
    print(f"\n📈 Confidence Distribution:")
    high_conf = sum(1 for r in results if r["confidence"] > 0.2)
    medium_conf = sum(1 for r in results if 0.1 <= r["confidence"] <= 0.2)
    low_conf = sum(1 for r in results if r["confidence"] < 0.1)
    
    print(f"   High (>0.2): {high_conf}/{total}")
    print(f"   Medium (0.1-0.2): {medium_conf}/{total}")
    print(f"   Low (<0.1): {low_conf}/{total}")
    
    # Test detailed classification
    print(f"\n🔎 Detailed Classification Test:")
    print("-" * 70)
    
    detailed_result = service.classify_complaint("paani nahi aa raha", detailed=True)
    print(f"Text: {detailed_result['text']}")
    print(f"Category: {detailed_result['category']}")
    print(f"Top 3 categories:")
    for cat in detailed_result["top_categories"]:
        print(f"  {cat['category']}: {cat['score']:.3f}")
    
    # Get system stats
    print(f"\n📊 System Statistics:")
    print("-" * 70)
    
    stats = service.get_classification_stats()
    print(f"Categories: {stats['categories']['total']}")
    print(f"Total anchors: {stats['anchors']['total']}")
    
    print(f"\nAnchors per category:")
    for category, count in stats['anchors']['per_category'].items():
        print(f"  {category}: {count} anchors")
    
    return results

if __name__ == "__main__":
    run_tests()