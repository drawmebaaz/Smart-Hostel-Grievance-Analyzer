#!/usr/bin/env python3
"""
Fixed Embedder - Day 7A
Handles PyTorch meta tensor issues
"""

import logging
from typing import List, Union
import numpy as np
from sentence_transformers import SentenceTransformer
from app.config import EMBEDDING_MODEL_NAME
from app.utils.logger import get_logger


logger = get_logger(__name__)


class Embedder:
    """
    Multilingual sentence embedding generator.
    Uses Sentence Transformers for cross-lingual semantic understanding.
    
    Day 7A: Fixed PyTorch meta tensor loading issue
    """
  
    def __init__(self, model_name: str = None):
        """
        Initialize the embedding model.
      
        Args:
            model_name: Override default model name.
        """
        self.model_name = model_name or EMBEDDING_MODEL_NAME
        self.model = None
        self.dimension = None
        self._initialize_model()
  
    def _initialize_model(self):
        """Lazy loading of model with PyTorch fix"""
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            
            # Day 7A Fix: Use device_map="cpu" to avoid meta tensor issues
            import torch
            
            # Force CPU and avoid meta tensors
            self.model = SentenceTransformer(
                self.model_name,
                device="cpu"
            )
            
            # Ensure model is on CPU
            self.model = self.model.to("cpu")
            
            # Get embedding dimension
            test_embedding = self.model.encode(["test"])
            self.dimension = len(test_embedding[0])
            
            logger.info(f"Model loaded successfully. Dimension: {self.dimension}")
          
        except Exception as e:
            logger.error(f"Failed to load model {self.model_name}: {str(e)}")
            raise
  
    def embed(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
      
        Args:
            text: Input text (any language)
          
        Returns:
            List of floats representing the semantic vector
        """
        if not text:
            return [0.0] * self.dimension if self.dimension else []
      
        try:
            # The model handles multiple languages automatically
            vector = self.model.encode(text, convert_to_numpy=True)
            return vector.tolist()
        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}")
            # Return zero vector on failure
            return [0.0] * self.dimension if self.dimension else []
  
    def embed_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Generate embeddings for multiple texts efficiently.
      
        Args:
            texts: List of input texts
            batch_size: Batch size for processing
          
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
      
        try:
            # Batch processing for efficiency
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                convert_to_numpy=True,
                show_progress_bar=False
            )
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Batch embedding failed: {str(e)}")
            return []
  
    def get_dimension(self) -> int:
        """Get embedding dimension"""
        return self.dimension or 512  # Default for distiluse model


# Singleton instance for reuse
_embedder_instance = None


def get_embedder() -> Embedder:
    """Get singleton embedder instance"""
    global _embedder_instance
    if _embedder_instance is None:
        _embedder_instance = Embedder()
    return _embedder_instance