#!/usr/bin/env python3
"""
Test script for Day 4.2 - Urgency Classification System
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.classification.urgency_classifier import get_urgency_classifier
from app.services.classification_service import get_classification_service

def run_urgency_tests():
    """Run urgency classification tests"""
    urgency_classifier = get_urgency_classifier()
    classification_service = get_classification_service()
    
    print("🧪 DAY 4.2 - URGENCY CLASSIFICATION TEST")
    print("=" * 70)
    
    # Test cases covering different urgency levels
    test_cases = [
        ("Tap is leaking slightly in washroom", "Low"),
        ("Room light is dim", "Low"),
        ("WiFi not working properly since yesterday", "Medium"),
        ("Paani ka pressure kaafi kam hai", "Medium"),
        ("No water supply since morning", "High"),
        ("Toilet is blocked and unusable", "High"),
        ("Electric spark coming from switch", "Critical"),
        ("Unknown person roaming inside hostel", "Critical"),
        ("Fight happened near hostel", "Critical"),
        ("Power cut for many hours", "High"),
    ]
    
    results = []
    
    print("\n🔍 Urgency Classification Tests:")
    print("-" * 70)
    
    for text, expected_urgency in test_cases:
        result = urgency_classifier.classify(text)
        predicted = result["urgency"]
        confidence = result["confidence"]
        score = result["similarity_score"]
        
        is_correct = predicted == expected_urgency
        status = "✅" if is_correct else "❌"
        
        results.append({
            "text": text,
            "expected": expected_urgency,
            "predicted": predicted,
            "correct": is_correct,
            "confidence": confidence,
            "score": score
        })
        
        print(f"{status} '{text[:40]}...'")
        print(f"   Expected: {expected_urgency:10} | Predicted: {predicted:10}")
        print(f"   Confidence: {confidence:.3f} | Score: {score:.3f}")
    
    # Calculate accuracy
    correct = sum(1 for r in results if r["correct"])
    total = len(results)
    accuracy = correct / total if total > 0 else 0
    
    print(f"\n📊 Urgency Classification Summary:")
    print(f"   Total tests: {total}")
    print(f"   Correct: {correct}")
    print(f"   Accuracy: {accuracy:.1%}")
    
    # Test combined classification
    print(f"\n🔗 Combined Classification Test (Category + Urgency):")
    print("-" * 70)
    
    combined_result = classification_service.classify_with_urgency(
        "Electric spark coming from switch in room 101"
    )
    
    print(f"Text: {combined_result['text']}")
    print(f"Category: {combined_result['category']}")
    print(f"Urgency: {combined_result['urgency_analysis']['urgency']}")
    print(f"Priority Tier: {combined_result['combined_priority']['priority_tier']}")
    print(f"Priority Score: {combined_result['combined_priority']['priority_score']:.3f}")
    
    # Test batch classification
    print(f"\n📦 Batch Urgency Classification Test:")
    print("-" * 70)
    
    batch_texts = [
        "Tap leaking slightly",
        "No water since morning",
        "Electric spark from socket"
    ]
    
    batch_results = urgency_classifier.classify_batch(batch_texts)
    
    for i, (text, result) in enumerate(zip(batch_texts, batch_results), 1):
        print(f"{i}. '{text}' → {result['urgency']} (conf: {result['confidence']:.2f})")
    
    # System info
    print(f"\n📊 Urgency System Info:")
    print("-" * 70)
    print(f"Urgency Levels: {urgency_classifier.urgency_levels}")
    print(f"Total anchors: {sum(len(anchors) for anchors in urgency_classifier.anchor_embeddings)}")
    
    return results

def test_urgency_explanation():
    """Test urgency explanation feature"""
    print(f"\n💡 Urgency Explanation Test:")
    print("-" * 70)
    
    urgency_classifier = get_urgency_classifier()
    
    test_text = "Electric spark coming from switch near bed"
    result = urgency_classifier.classify(test_text)
    urgency_level = result["urgency"]
    
    explanation = urgency_classifier.explain_urgency(test_text, urgency_level)
    
    print(f"Text: {test_text}")
    print(f"Urgency Level: {urgency_level}")
    
    if "error" not in explanation:
        print(f"Explanation: {explanation['explanation']}")
        print(f"Average Similarity: {explanation['average_similarity']}")
        print("\nTop Matching Anchors:")
        for anchor_info in explanation["top_matching_anchors"]:
            print(f"  - '{anchor_info['anchor']}' (similarity: {anchor_info['similarity']})")
    else:
        print(f"Error: {explanation['error']}")

if __name__ == "__main__":
    # Run all tests
    run_urgency_tests()
    test_urgency_explanation()
    
    print("\n" + "=" * 70)
    print("✅ DAY 4.2 COMPLETE: Urgency classification system implemented")
    print("=" * 70)