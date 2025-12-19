#!/usr/bin/env python3
"""
Classification service layer - provides clean API for classification.
Acts as an interface between the classifier and the application.
"""
from typing import Dict, List, Any, Optional

from app.classification.similarity_classifier import get_classifier
from app.classification.category_anchors import (
    CATEGORY_ANCHORS, 
    get_all_categories,
    get_category_description
)
from app.utils.logger import get_logger

logger = get_logger(__name__)

class ClassificationService:
    """
    Service layer for classification operations.
    Provides business logic and error handling.
    """
    
    def __init__(self):
        self.classifier = get_classifier()
        self.categories = get_all_categories()
        logger.info(f"ClassificationService initialized with {len(self.categories)} categories")
    
    def classify_complaint(self, text: str, detailed: bool = False) -> Dict[str, Any]:
        """
        Classify a single complaint.
        
        Args:
            text: Complaint text
            detailed: If True, return detailed scores
            
        Returns:
            Classification result with metadata
        """
        try:
            # Perform classification
            classification_result = self.classifier.classify(
                text, 
                return_scores=detailed
            )
            
            # Add service metadata
            result = {
                **classification_result,
                "service_info": {
                    "classifier_type": "similarity_based",
                    "categories_available": self.categories,
                    "anchors_per_category": {
                        cat: len(anchors) 
                        for cat, anchors in CATEGORY_ANCHORS.items()
                    }
                }
            }
            
            # Add category description
            result["category_description"] = get_category_description(
                result["category"]
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Classification service error: {str(e)}")
            return {
                "category": "Others",
                "confidence": 0.0,
                "error": str(e),
                "text": text
            }
    
    def classify_complaints_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Classify multiple complaints.
        
        Args:
            texts: List of complaint texts
            
        Returns:
            List of classification results
        """
        if not texts:
            return []
        
        results = []
        for text in texts:
            result = self.classify_complaint(text)
            results.append(result)
        
        return results
    
    def get_classification_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the classification system.
        
        Returns:
            System statistics and configuration
        """
        total_anchors = sum(
            len(anchors) for anchors in CATEGORY_ANCHORS.values()
        )
        
        return {
            "categories": {
                "total": len(self.categories),
                "list": self.categories
            },
            "anchors": {
                "total": total_anchors,
                "per_category": {
                    cat: len(anchors) 
                    for cat, anchors in CATEGORY_ANCHORS.items()
                }
            },
            "classifier": {
                "type": "SimilarityClassifier",
                "similarity_threshold": self.classifier.similarity_threshold,
                "strategy": "max_similarity_per_category"
            },
            "multilingual_support": True,
            "requires_training": False
        }
    
    def explain_classification(self, text: str) -> Dict[str, Any]:
        """
        Provide detailed explanation for a classification.
        
        Args:
            text: Complaint text
            
        Returns:
            Explanation with matching anchors
        """
        try:
            # First classify
            classification = self.classify_complaint(text)
            category = classification["category"]
            
            # Get explanation from classifier
            explanation = self.classifier.explain_classification(text, category)
            
            # Combine with classification result
            result = {
                **classification,
                "explanation": explanation
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Explanation service error: {str(e)}")
            return {
                "error": f"Failed to generate explanation: {str(e)}",
                "text": text
            }
    
    def validate_category(self, category: str) -> bool:
        """Check if a category exists in the system"""
        return category in self.categories
    
    def get_category_info(self, category: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific category"""
        if not self.validate_category(category):
            return None
        
        return {
            "name": category,
            "description": get_category_description(category),
            "anchor_count": len(CATEGORY_ANCHORS.get(category, [])),
            "anchors": CATEGORY_ANCHORS.get(category, []),
            "multilingual": any(
                any(char.isalpha() for char in anchor if ord(char) > 127)
                for anchor in CATEGORY_ANCHORS.get(category, [])
            )
        }

# Singleton instance
_service_instance = None

def get_classification_service() -> ClassificationService:
    """Get singleton classification service instance"""
    global _service_instance
    if _service_instance is None:
        _service_instance = ClassificationService()
    return _service_instance

if __name__ == "__main__":
    # Quick service test
    service = get_classification_service()
    
    print("Classification Service Test")
    print("=" * 60)
    
    # Test classification
    test_text = "paani nahi aa raha hai hostel me"
    result = service.classify_complaint(test_text, detailed=True)
    
    print(f"\nText: {test_text}")
    print(f"Category: {result['category']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Similarity Score: {result['similarity_score']}")
    
    # Print top 3 categories
    print("\nTop 3 Categories:")
    for cat in result['top_categories']:
        print(f"  {cat['category']}: {cat['score']}")
    
    # Print stats
    stats = service.get_classification_stats()
    print(f"\nSystem Stats:")
    print(f"  Categories: {stats['categories']['total']}")
    print(f"  Total anchors: {stats['anchors']['total']}")