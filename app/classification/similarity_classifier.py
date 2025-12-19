#!/usr/bin/env python3
"""
Similarity-based classifier using category anchors.
Uses cosine similarity between complaint embeddings and category anchors.
"""
import numpy as np
from typing import Dict, List, Tuple, Optional
from sklearn.metrics.pairwise import cosine_similarity

from app.classification.category_anchors import CATEGORY_ANCHORS
from app.services.embedding_service import get_embedding_service
from app.utils.logger import get_logger

logger = get_logger(__name__)

class SimilarityClassifier:
    """
    Classify complaints by comparing their embeddings with category anchors.
    
    Design Philosophy:
    - No training required
    - Multilingual by design
    - Explainable decisions (similarity scores visible)
    - Confidence based on score gaps
    """
    
    def __init__(self, similarity_threshold: float = 0.0):
        """
        Initialize classifier with category anchors.
        
        Args:
            similarity_threshold: Minimum similarity to consider (0-1)
        """
        self.embedding_service = get_embedding_service()
        self.similarity_threshold = similarity_threshold
        self.category_embeddings: Dict[str, np.ndarray] = {}
        self.category_names: List[str] = []
        
        # Load and embed anchors
        self._initialize_anchors()
        logger.info(f"SimilarityClassifier initialized with {len(self.category_names)} categories")
    
    def _initialize_anchors(self):
        """Embed all category anchors once at initialization"""
        try:
            self.category_names = list(CATEGORY_ANCHORS.keys())
            
            for category, anchors in CATEGORY_ANCHORS.items():
                # Generate embeddings for all anchors in this category
                anchor_embeddings = []
                
                for anchor in anchors:
                    embedding = self.embedding_service.generate_embedding(anchor)
                    anchor_embeddings.append(embedding)
                
                # Store as numpy array for efficient computation
                self.category_embeddings[category] = np.array(anchor_embeddings)
                
                logger.debug(f"Embedded {len(anchors)} anchors for category: {category}")
            
            logger.info(f"Successfully embedded anchors for {len(self.category_names)} categories")
            
        except Exception as e:
            logger.error(f"Failed to initialize anchors: {str(e)}")
            raise
    
    def _compute_similarities(self, text_embedding: np.ndarray) -> Dict[str, float]:
        """
        Compute similarity scores between text and all category anchors.
        
        Strategy: Use maximum similarity per category (best matching anchor)
        """
        scores = {}
        
        for category, anchor_embeddings in self.category_embeddings.items():
            # Compute cosine similarity with all anchors in this category
            similarities = cosine_similarity(
                text_embedding.reshape(1, -1), 
                anchor_embeddings
            )[0]
            
            # Use maximum similarity (best matching anchor)
            max_similarity = float(np.max(similarities))
            scores[category] = max_similarity
        
        return scores
    
    def _compute_confidence(self, sorted_scores: List[Tuple[str, float]]) -> float:
        """
        Compute confidence based on gap between top two scores.
        
        Confidence = top_score - second_score
        Range: 0 to 1 (higher = more confident)
        """
        if len(sorted_scores) < 2:
            return 0.0
        
        top_score = sorted_scores[0][1]
        second_score = sorted_scores[1][1]
        
        # Gap-based confidence
        confidence = top_score - second_score
        
        # Ensure confidence is between 0 and 1
        return max(0.0, min(1.0, confidence))
    
    def _get_top_categories(self, scores: Dict[str, float], top_k: int = 3) -> List[Dict]:
        """Get top k categories with their scores"""
        sorted_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        top_categories = []
        for category, score in sorted_items[:top_k]:
            top_categories.append({
                "category": category,
                "score": round(score, 4),
                "is_primary": (category == sorted_items[0][0])
            })
        
        return top_categories
    
    def classify(self, text: str, return_scores: bool = False) -> Dict:
        """
        Classify a complaint text into a category.
        
        Args:
            text: Complaint text to classify
            return_scores: If True, return all similarity scores
            
        Returns:
            Dictionary with classification results
        """
        if not text or not isinstance(text, str):
            return {
                "category": "Others",
                "confidence": 0.0,
                "error": "Empty or invalid text"
            }
        
        try:
            # Step 1: Generate embedding for the complaint
            text_embedding = np.array(
                self.embedding_service.generate_embedding(text)
            )
            
            # Step 2: Compute similarities with all category anchors
            scores = self._compute_similarities(text_embedding)
            
            # Step 3: Sort categories by similarity score
            sorted_scores = sorted(
                scores.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            # Step 4: Determine primary category
            primary_category, primary_score = sorted_scores[0]
            
            # Step 5: Compute confidence
            confidence = self._compute_confidence(sorted_scores)
            
            # Step 6: Check if score meets threshold
            meets_threshold = primary_score >= self.similarity_threshold
            
            # Step 7: Build response
            result = {
                "text": text,
                "category": primary_category,
                "confidence": round(confidence, 4),
                "similarity_score": round(primary_score, 4),
                "meets_threshold": meets_threshold,
                "top_categories": self._get_top_categories(scores, top_k=3),
                "processing_info": {
                    "categories_considered": len(self.category_names),
                    "threshold": self.similarity_threshold,
                    "strategy": "max_similarity_per_category"
                }
            }
            
            # Include all scores if requested
            if return_scores:
                result["all_scores"] = {
                    category: round(score, 4) 
                    for category, score in scores.items()
                }
            
            logger.debug(f"Classified: '{text[:50]}...' → {primary_category} (conf: {confidence:.3f})")
            
            return result
            
        except Exception as e:
            logger.error(f"Classification failed for text: {str(e)}")
            return {
                "category": "Others",
                "confidence": 0.0,
                "error": f"Classification failed: {str(e)}"
            }
    
    def classify_batch(self, texts: List[str]) -> List[Dict]:
        """
        Classify multiple texts efficiently.
        
        Args:
            texts: List of complaint texts
            
        Returns:
            List of classification results
        """
        results = []
        
        for text in texts:
            result = self.classify(text)
            results.append(result)
        
        return results
    
    def explain_classification(self, text: str, category: str) -> Dict:
        """
        Provide explanation for why a text was classified into a category.
        
        Returns:
            Explanation including top matching anchors
        """
        try:
            # Get embedding for the text
            text_embedding = np.array(
                self.embedding_service.generate_embedding(text)
            )
            
            # Get anchors for the category
            anchors = CATEGORY_ANCHORS.get(category, [])
            anchor_embeddings = self.category_embeddings.get(category, np.array([]))
            
            if len(anchor_embeddings) == 0:
                return {"error": "No anchors found for category"}
            
            # Compute similarities with each anchor
            similarities = cosine_similarity(
                text_embedding.reshape(1, -1), 
                anchor_embeddings
            )[0]
            
            # Get top matching anchors
            anchor_scores = list(zip(anchors, similarities))
            anchor_scores.sort(key=lambda x: x[1], reverse=True)
            
            top_anchors = [
                {"anchor": anchor, "similarity": round(score, 4)}
                for anchor, score in anchor_scores[:3]  # Top 3 anchors
            ]
            
            return {
                "text": text,
                "category": category,
                "explanation": f"Text is most similar to '{category}' anchors",
                "top_matching_anchors": top_anchors,
                "max_similarity": round(float(np.max(similarities)), 4)
            }
            
        except Exception as e:
            logger.error(f"Explanation failed: {str(e)}")
            return {"error": f"Explanation failed: {str(e)}"}

# Singleton instance
_classifier_instance = None

def get_classifier() -> SimilarityClassifier:
    """Get singleton classifier instance"""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = SimilarityClassifier()
    return _classifier_instance

if __name__ == "__main__":
    # Quick test
    classifier = get_classifier()
    
    test_cases = [
        "paani nahi aa raha hostel me",
        "wifi ka issue hai room me",
        "warden sunta hi nahi hai",
        "mess food is very bad quality",
        "light nahi hai room me"
    ]
    
    print("Testing Similarity Classifier")
    print("=" * 60)
    
    for test in test_cases:
        result = classifier.classify(test, return_scores=False)
        print(f"\nInput: '{test}'")
        print(f"Category: {result['category']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Score: {result['similarity_score']}")
        print(f"Top 3: {[c['category'] for c in result['top_categories']]}")