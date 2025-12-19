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
    Uses Sentence Transformers for cross-lingual semantic understanding[citation:1][citation:6].
    """
    
    def __init__(self, model_name: str = None):
        """
        Initialize the embedding model.
        
        Args:
            model_name: Override default model name. Recommended models[citation:3]:
                - "distiluse-base-multilingual-cased-v2": 512-dim, 50+ languages
                - "paraphrase-multilingual-MiniLM-L12-v2": 384-dim, faster
                - "l3cube-pune/hindi-sentence-similarity-sbert": Hindi-focused[citation:2]
        """
        self.model_name = model_name or EMBEDDING_MODEL_NAME
        self.model = None
        self.dimension = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Lazy loading of model to save memory"""
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            
            # Load the multilingual sentence transformer model[citation:6]
            self.model = SentenceTransformer(self.model_name)
            
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
            # The model handles multiple languages automatically[citation:1]
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
            # Batch processing for efficiency[citation:6]
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
        return self.dimension or 512  # Default for distiluse model[citation:5]

# Singleton instance for reuse
_embedder_instance = None

def get_embedder() -> Embedder:
    """Get singleton embedder instance"""
    global _embedder_instance
    if _embedder_instance is None:
        _embedder_instance = Embedder()
    return _embedder_instance