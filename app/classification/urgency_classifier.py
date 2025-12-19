#!/usr/bin/env python3
"""
Similarity-based urgency classifier using urgency anchors.
Uses cosine similarity between complaint embeddings and urgency anchors.
"""
import numpy as np
from typing import Dict, List, Tuple, Optional
from sklearn.metrics.pairwise import cosine_similarity

from app.classification.urgency_anchors import URGENCY_ANCHORS, URGENCY_LEVELS
from app.services.embedding_service import get_embedding_service
from app.utils.logger import get_logger

logger = get_logger(__name__)

class UrgencyClassifier:
    """
    Classify complaint urgency by comparing embeddings with urgency anchors.
    
    Design Principles:
    - No training required
    - Multilingual by design
    - Explainable decisions (similarity scores visible)
    - Confidence based on score gaps
    - Independent of category classification
    """
    
    def __init__(self):
        """Initialize urgency classifier with anchors"""
        self.embedding_service = get_embedding_service()
        self.urgency_levels = URGENCY_LEVELS
        self.anchor_embeddings: Dict[str, np.ndarray] = {}
        
        # Load and embed anchors
        self._initialize_anchors()
        logger.info(f"UrgencyClassifier initialized with {len(self.urgency_levels)} urgency levels")
    
    def _initialize_anchors(self):
        """Embed all urgency anchors once at initialization"""
        try:
            for level, anchors in URGENCY_ANCHORS.items():
                # Generate embeddings for all anchors in this urgency level
                anchor_embeddings = []
                
                for anchor in anchors:
                    embedding = self.embedding_service.generate_embedding(anchor)
                    anchor_embeddings.append(embedding)
                
                # Store as numpy array for efficient computation
                self.anchor_embeddings[level] = np.array(anchor_embeddings)
                
                logger.debug(f"Embedded {len(anchors)} anchors for urgency level: {level}")
            
            logger.info(f"Successfully embedded anchors for {len(self.urgency_levels)} urgency levels")
            
        except Exception as e:
            logger.error(f"Failed to initialize urgency anchors: {str(e)}")
            raise
    
    def _compute_similarities(self, text_embedding: np.ndarray) -> Dict[str, float]:
        """
        Compute similarity scores between text and all urgency anchors.
        
        Strategy: Use mean similarity per urgency level
        (more stable than max for urgency detection)
        """
        scores = {}
        
        for level, anchor_embeddings in self.anchor_embeddings.items():
            # Compute cosine similarity with all anchors in this urgency level
            similarities = cosine_similarity(
                text_embedding.reshape(1, -1), 
                anchor_embeddings
            )[0]
            
            # Use mean similarity (more robust for urgency)
            mean_similarity = float(np.mean(similarities))
            scores[level] = mean_similarity
        
        return scores
    
    def _compute_confidence(self, scores: Dict[str, float], top_level: str) -> float:
        """
        Compute confidence based on gap between top score and others.
        
        Confidence = (top_score - second_score) / top_score
        Normalized to 0-1 range
        """
        if len(scores) < 2:
            return 0.5  # Default moderate confidence
        
        # Get sorted scores
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        top_score = sorted_scores[0][1]
        second_score = sorted_scores[1][1]
        
        # Avoid division by zero
        if top_score == 0:
            return 0.0
        
        # Gap-based confidence normalized by top score
        confidence = (top_score - second_score) / top_score
        
        # Ensure confidence is between 0 and 1
        return max(0.0, min(1.0, confidence))
    
    def _get_top_urgencies(self, scores: Dict[str, float], top_k: int = 3) -> List[Dict]:
        """Get top k urgency levels with their scores"""
        sorted_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        top_urgencies = []
        for level, score in sorted_items[:top_k]:
            top_urgencies.append({
                "level": level,
                "score": round(score, 4),
                "is_primary": (level == sorted_items[0][0])
            })
        
        return top_urgencies
    
    def classify(self, text: str, return_scores: bool = False) -> Dict:
        """
        Classify urgency level of a complaint text.
        
        Args:
            text: Complaint text to classify
            return_scores: If True, return all similarity scores
            
        Returns:
            Dictionary with urgency classification results
        """
        if not text or not isinstance(text, str):
            return {
                "urgency": "Medium",  # Default when unclear
                "confidence": 0.0,
                "error": "Empty or invalid text"
            }
        
        try:
            # Step 1: Generate embedding for the complaint
            text_embedding = np.array(
                self.embedding_service.generate_embedding(text)
            )
            
            # Step 2: Compute similarities with all urgency anchors
            scores = self._compute_similarities(text_embedding)
            
            # Step 3: Determine primary urgency level
            primary_level = max(scores.items(), key=lambda x: x[1])[0]
            primary_score = scores[primary_level]
            
            # Step 4: Compute confidence
            confidence = self._compute_confidence(scores, primary_level)
            
            # Step 5: Build response
            result = {
                "text": text,
                "urgency": primary_level,
                "confidence": round(confidence, 4),
                "similarity_score": round(primary_score, 4),
                "top_urgencies": self._get_top_urgencies(scores, top_k=3),
                "processing_info": {
                    "urgency_levels_considered": len(self.urgency_levels),
                    "strategy": "mean_similarity_per_level",
                    "independent_of_category": True
                }
            }
            
            # Include all scores if requested
            if return_scores:
                result["all_scores"] = {
                    level: round(score, 4) 
                    for level, score in scores.items()
                }
            
            logger.debug(f"Urgency classified: '{text[:50]}...' → {primary_level} (conf: {confidence:.3f})")
            
            return result
            
        except Exception as e:
            logger.error(f"Urgency classification failed: {str(e)}")
            return {
                "urgency": "Medium",
                "confidence": 0.0,
                "error": f"Urgency classification failed: {str(e)}"
            }
    
    def classify_batch(self, texts: List[str]) -> List[Dict]:
        """
        Classify multiple texts efficiently.
        
        Args:
            texts: List of complaint texts
            
        Returns:
            List of urgency classification results
        """
        results = []
        
        for text in texts:
            result = self.classify(text)
            results.append(result)
        
        return results
    
    def explain_urgency(self, text: str, urgency_level: str) -> Dict:
        """
        Provide explanation for why a text got a specific urgency level.
        
        Returns:
            Explanation including matching anchors
        """
        try:
            # Get embedding for the text
            text_embedding = np.array(
                self.embedding_service.generate_embedding(text)
            )
            
            # Get anchors for the urgency level
            anchors = URGENCY_ANCHORS.get(urgency_level, [])
            anchor_embeddings = self.anchor_embeddings.get(urgency_level, np.array([]))
            
            if len(anchor_embeddings) == 0:
                return {"error": f"No anchors found for urgency level: {urgency_level}"}
            
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
                "urgency_level": urgency_level,
                "explanation": f"Text urgency matches '{urgency_level}' severity patterns",
                "top_matching_anchors": top_anchors,
                "average_similarity": round(float(np.mean(similarities)), 4)
            }
            
        except Exception as e:
            logger.error(f"Urgency explanation failed: {str(e)}")
            return {"error": f"Urgency explanation failed: {str(e)}"}

# Singleton instance
_classifier_instance = None

def get_urgency_classifier() -> UrgencyClassifier:
    """Get singleton urgency classifier instance"""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = UrgencyClassifier()
    return _classifier_instance

if __name__ == "__main__":
    # Quick test
    classifier = get_urgency_classifier()
    
    test_cases = [
        "Tap is leaking slightly in washroom",
        "WiFi not working properly since yesterday",
        "No water supply since morning",
        "Electric spark coming from switch",
        "Unknown person roaming inside hostel",
        "Fan makes small noise but works"
    ]
    
    print("Testing Urgency Classifier")
    print("=" * 70)
    
    for test in test_cases:
        result = classifier.classify(test, return_scores=False)
        print(f"\nInput: '{test}'")
        print(f"Urgency: {result['urgency']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Score: {result['similarity_score']}")
        print(f"Top 3: {[u['level'] for u in result['top_urgencies']]}")