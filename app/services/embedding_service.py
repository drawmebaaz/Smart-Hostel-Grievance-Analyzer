import logging
from typing import List, Dict, Any, Optional
from app.preprocessing.text_cleaner import preprocess_text, batch_preprocess
from app.embeddings.embedder import get_embedder
from app.utils.logger import get_logger

logger = get_logger(__name__)

class EmbeddingService:
    """
    Orchestration layer for text preprocessing and embedding generation.
    This is your AI SDK for the grievance system.
    """
    
    def __init__(self, embedder=None):
        """
        Initialize the embedding service.
        
        Args:
            embedder: Optional custom embedder instance
        """
        self.embedder = embedder or get_embedder()
        self.embedding_dim = self.embedder.get_dimension()
        logger.info(f"Embedding service initialized with dimension: {self.embedding_dim}")
    
    def generate_embedding(self, raw_text: str, 
                          normalize_hinglish: bool = True) -> List[float]:
        """
        Complete pipeline: Preprocess → Embed
        
        Args:
            raw_text: Raw complaint text
            normalize_hinglish: Apply Hinglish normalization
            
        Returns:
            Embedding vector (list of floats)
        """
        # Step 1: Preprocess
        cleaned_text = preprocess_text(raw_text, normalize_hinglish)
        
        # Step 2: Generate embedding
        embedding = self.embedder.embed(cleaned_text)
        
        logger.debug(f"Generated embedding for text (length: {len(raw_text)})")
        return embedding
    
    def generate_embeddings_batch(self, raw_texts: List[str],
                                 normalize_hinglish: bool = True,
                                 batch_size: int = 32) -> List[List[float]]:
        """
        Batch processing for efficiency.
        
        Args:
            raw_texts: List of raw texts
            normalize_hinglish: Apply Hinglish normalization
            batch_size: Processing batch size
            
        Returns:
            List of embedding vectors
        """
        if not raw_texts:
            return []
        
        # Step 1: Batch preprocessing
        cleaned_texts = batch_preprocess(raw_texts, normalize_hinglish)
        
        # Step 2: Batch embedding
        embeddings = self.embedder.embed_batch(cleaned_texts, batch_size)
        
        logger.info(f"Generated {len(embeddings)} embeddings in batch")
        return embeddings
    
    def get_embedding_info(self) -> Dict[str, Any]:
        """Get service metadata"""
        return {
            "model": self.embedder.model_name,
            "dimension": self.embedding_dim,
            "languages_supported": "Multilingual (50+ languages)",
            "hinglish_support": True
        }
    
    def validate_embedding(self, embedding: List[float]) -> bool:
        """Validate if embedding is valid"""
        if not embedding:
            return False
        
        # Check dimension
        if len(embedding) != self.embedding_dim:
            logger.warning(f"Embedding dimension mismatch: {len(embedding)} != {self.embedding_dim}")
            return False
        
        # Check for zero vectors (might indicate failure)
        if all(abs(x) < 1e-10 for x in embedding):
            logger.warning("Embedding appears to be a zero vector")
            return False
        
        return True

# Global service instance
_service_instance = None

def get_embedding_service() -> EmbeddingService:
    """Get singleton embedding service instance"""
    global _service_instance
    if _service_instance is None:
        _service_instance = EmbeddingService()
    return _service_instance