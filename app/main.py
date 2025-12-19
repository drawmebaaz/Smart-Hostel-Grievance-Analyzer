from app.services.classification_service import get_classification_service
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
from datetime import datetime
import uvicorn

from app.config import SERVICE_NAME, SERVICE_VERSION, API_PORT
from app.services.embedding_service import get_embedding_service
from app.utils.logger import get_logger

classification_service = get_classification_service()

logger = get_logger(__name__)
app = FastAPI(
    title=SERVICE_NAME,
    version=SERVICE_VERSION,
    description="AI Service for Multilingual Hostel Complaint Processing",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Initialize services
embedding_service = get_embedding_service()

@app.get("/")
async def root():
    """Root endpoint with service info"""
    return {
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "embed": "/embed",
            "batch_embed": "/embed/batch",
            "info": "/info"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "embedding_service": "operational"
    }

@app.get("/info")
async def service_info():
    """Get service information and capabilities"""
    info = embedding_service.get_embedding_info()
    return {
        **info,
        "preprocessing": {
            "hinglish_normalization": True,
            "whitespace_cleaning": True,
            "lowercasing": True
        },
        "architecture": "FastAPI + Sentence Transformers"
    }

@app.get("/categories")
async def get_categories():
    """Get all available complaint categories"""
    stats = classification_service.get_classification_stats()
    return {
        "categories": stats["categories"]["list"],
        "total_categories": stats["categories"]["total"],
        "multilingual_support": True
    }

@app.get("/classify/stats")
async def get_classification_stats():
    """Get classification system statistics"""
    stats = classification_service.get_classification_stats()
    return stats

@app.post("/classify")
async def classify_complaint(request: Dict[str, Any]):
    """
    Classify a complaint text.
    
    Request body:
    {
        "text": "complaint text here",
        "detailed": false
    }
    """
    try:
        text = request.get("text", "")
        detailed = request.get("detailed", False)
        
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        result = classification_service.classify_complaint(text, detailed)
        
        return result
        
    except Exception as e:
        logger.error(f"Classification error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")

@app.post("/classify/batch")
async def classify_complaints_batch(request: Dict[str, Any]):
    """
    Classify multiple complaints in batch.
    
    Request body:
    {
        "texts": ["text1", "text2", ...]
    }
    """
    try:
        texts = request.get("texts", [])
        
        if not texts:
            raise HTTPException(status_code=400, detail="Texts list is required")
        
        results = classification_service.classify_complaints_batch(texts)
        
        return {
            "count": len(results),
            "results": results,
            "summary": {
                "categories_predicted": len(set(r["category"] for r in results)),
                "average_confidence": sum(r.get("confidence", 0) for r in results) / len(results) if results else 0
            }
        }
        
    except Exception as e:
        logger.error(f"Batch classification error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch classification failed: {str(e)}")

@app.post("/classify/explain")
async def explain_classification(request: Dict[str, Any]):
    """
    Get explanation for a classification.
    
    Request body:
    {
        "text": "complaint text here"
    }
    """
    try:
        text = request.get("text", "")
        
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        explanation = classification_service.explain_classification(text)
        
        return explanation
        
    except Exception as e:
        logger.error(f"Explanation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Explanation failed: {str(e)}"

)

@app.post("/embed")
async def embed_text(request: Dict[str, Any]):
    """
    Embed a single text.
    
    Request body:
    {
        "text": "complaint text here",
        "normalize_hinglish": true
    }
    """
    try:
        text = request.get("text", "")
        normalize_hinglish = request.get("normalize_hinglish", True)
        
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        embedding = embedding_service.generate_embedding(
            text, 
            normalize_hinglish=normalize_hinglish
        )
        
        # Validate embedding
        is_valid = embedding_service.validate_embedding(embedding)
        
        return {
            "text": text,
            "embedding": embedding,
            "dimension": len(embedding),
            "valid": is_valid,
            "model": embedding_service.embedder.model_name
        }
        
    except Exception as e:
        logger.error(f"Embedding error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Embedding failed: {str(e)}")

@app.post("/embed/batch")
async def embed_batch(request: Dict[str, Any]):
    """
    Embed multiple texts in batch.
    
    Request body:
    {
        "texts": ["text1", "text2", ...],
        "normalize_hinglish": true,
        "batch_size": 32
    }
    """
    try:
        texts = request.get("texts", [])
        normalize_hinglish = request.get("normalize_hinglish", True)
        batch_size = request.get("batch_size", 32)
        
        if not texts:
            raise HTTPException(status_code=400, detail="Texts list is required")
        
        embeddings = embedding_service.generate_embeddings_batch(
            texts,
            normalize_hinglish=normalize_hinglish,
            batch_size=batch_size
        )
        
        # Validate each embedding
        validations = [
            embedding_service.validate_embedding(emb) for emb in embeddings
        ]
        
        return {
            "count": len(embeddings),
            "embeddings": embeddings,
            "dimension": len(embeddings[0]) if embeddings else 0,
            "validations": validations,
            "all_valid": all(validations)
        }
        
    except Exception as e:
        logger.error(f"Batch embedding error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch embedding failed: {str(e)}")

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )

def start():
    """Start the FastAPI server"""
    logger.info(f"Starting {SERVICE_NAME} v{SERVICE_VERSION}")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=API_PORT,
        reload=True,  # Auto-reload in development
        log_level="info"
    )

if __name__ == "__main__":
    start()