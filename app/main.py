#!/usr/bin/env python3
"""
FastAPI server for Smart Hostel Grievance Analyzer.
Day 4.3/4.4: Complete API with category + urgency integration.
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
from datetime import datetime
import uvicorn

from app.config import SERVICE_NAME, SERVICE_VERSION, API_PORT
from app.services.embedding_service import get_embedding_service
from app.services.classification_service import get_classification_service
from app.classification.urgency_anchors import (
    URGENCY_LEVELS, 
    URGENCY_DESCRIPTIONS,
    URGENCY_RESPONSE_TIMES,
    URGENCY_ANCHORS
)
from app.utils.logger import get_logger

# Initialize services
embedding_service = get_embedding_service()
classification_service = get_classification_service()

logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title=SERVICE_NAME,
    version=SERVICE_VERSION,
    description="AI Service for Multilingual Hostel Complaint Processing",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "Health",
            "description": "Service health and information endpoints"
        },
        {
            "name": "Embeddings",
            "description": "Text embedding and vectorization"
        },
        {
            "name": "Classification",
            "description": "Category classification (Day 3)"
        },
        {
            "name": "Urgency",
            "description": "Urgency detection and analysis (Day 4)"
        },
        {
            "name": "Analysis",
            "description": "Complete complaint analysis (Day 4.3 integrated)"
        }
    ]
)

# ==================== HEALTH & INFO ENDPOINTS ====================

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint with service info"""
    return {
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "status": "operational",
        "description": "Smart Hostel Grievance Analyzer AI Service",
        "features": [
            "Multilingual text processing (English/Hindi/Hinglish)",
            "Semantic embedding generation",
            "Category classification (10 hostel categories)",
            "Urgency detection (4 levels: Low/Medium/High/Critical)",
            "Complete complaint analysis",
            "Batch processing support"
        ],
        "days_completed": [1, 2, 3, 4],
        "endpoints": {
            "health": "/health",
            "info": "/info",
            "embedding": ["/embed", "/embed/batch"],
            "classification": ["/classify", "/classify/batch", "/classify/explain"],
            "urgency": ["/urgency", "/urgency/levels"],
            "analysis": ["/analyze"],
            "categories": "/categories",
            "stats": "/classify/stats"
        }
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    try:
        # Test service health
        embedding_test = embedding_service.generate_embedding("test", normalize_hinglish=False)
        classification_test = classification_service.classify_complaint("test")
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "embedding_service": "operational",
                "classification_service": "operational",
                "urgency_service": "operational"
            },
            "checks": {
                "embedding_dimension": len(embedding_test),
                "classification_working": "category" in classification_test,
                "day_4_integrated": True
            }
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "degraded",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "services": {
                "embedding_service": "check_failed",
                "classification_service": "check_failed"
            }
        }

@app.get("/info", tags=["Health"])
async def service_info():
    """Get service information and capabilities"""
    try:
        embedding_info = embedding_service.get_embedding_info()
        classification_stats = classification_service.get_classification_stats()
        
        return {
            "service": SERVICE_NAME,
            "version": SERVICE_VERSION,
            "embedding": embedding_info,
            "classification": classification_stats,
            "preprocessing": {
                "hinglish_normalization": True,
                "whitespace_cleaning": True,
                "lowercasing": True,
                "multilingual_support": True
            },
            "architecture": "FastAPI + Sentence Transformers + sklearn",
            "days_implemented": {
                "day_1_2": "Text processing & embedding pipeline",
                "day_3": "Category classification system",
                "day_4": "Urgency detection & integration"
            },
            "api_version": "1.0.0"
        }
        
    except Exception as e:
        logger.error(f"Service info error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Service info failed: {str(e)}")

# ==================== EMBEDDING ENDPOINTS (Day 1-2) ====================

@app.post("/embed", tags=["Embeddings"])
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
            "model": embedding_service.embedder.model_name,
            "normalized": normalize_hinglish
        }
        
    except Exception as e:
        logger.error(f"Embedding error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Embedding failed: {str(e)}")

@app.post("/embed/batch", tags=["Embeddings"])
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
            "all_valid": all(validations),
            "batch_size": batch_size,
            "normalized": normalize_hinglish
        }
        
    except Exception as e:
        logger.error(f"Batch embedding error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch embedding failed: {str(e)}")

# ==================== CATEGORY ENDPOINTS (Day 3) ====================

@app.get("/categories", tags=["Classification"])
async def get_categories():
    """Get all available complaint categories"""
    try:
        stats = classification_service.get_classification_stats()
        return {
            "categories": stats["categories"]["list"],
            "total_categories": stats["categories"]["total"],
            "multilingual_support": True,
            "day_implemented": "Day 3"
        }
    except Exception as e:
        logger.error(f"Categories error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Categories failed: {str(e)}")

@app.get("/classify/stats", tags=["Classification"])
async def get_classification_stats():
    """Get classification system statistics"""
    try:
        stats = classification_service.get_classification_stats()
        return {
            **stats,
            "api_endpoints": {
                "category_only": "/classify",
                "with_urgency": "/analyze",
                "batch": "/classify/batch",
                "explain": "/classify/explain"
            }
        }
    except Exception as e:
        logger.error(f"Classification stats error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Classification stats failed: {str(e)}")

@app.post("/classify", tags=["Classification"])
async def classify_complaint(request: Dict[str, Any]):
    """
    Classify a complaint text (Category only).
    
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
        
        return {
            **result,
            "analysis_type": "category_only",
            "day_implemented": "Day 3"
        }
        
    except Exception as e:
        logger.error(f"Classification error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")

@app.post("/classify/batch", tags=["Classification"])
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
                "average_confidence": sum(r.get("confidence", 0) for r in results) / len(results) if results else 0,
                "most_common_category": max(
                    set(r["category"] for r in results),
                    key=lambda x: sum(1 for r in results if r["category"] == x)
                ) if results else None
            },
            "batch_processing": True
        }
        
    except Exception as e:
        logger.error(f"Batch classification error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch classification failed: {str(e)}")

@app.post("/classify/explain", tags=["Classification"])
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
        
        return {
            **explanation,
            "explanation_type": "category_classification",
            "day_implemented": "Day 3"
        }
        
    except Exception as e:
        logger.error(f"Explanation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Explanation failed: {str(e)}")

# ==================== URGENCY ENDPOINTS (Day 4) ====================

@app.get("/urgency/levels", tags=["Urgency"])
async def get_urgency_levels():
    """
    Get all available urgency levels and descriptions.
    
    Day 4.4: Returns detailed urgency level information.
    """
    try:
        levels_info = []
        for level in URGENCY_LEVELS:
            levels_info.append({
                "level": level,
                "description": URGENCY_DESCRIPTIONS[level],
                "response_time_hours": URGENCY_RESPONSE_TIMES[level],
                "anchor_count": len(URGENCY_ANCHORS.get(level, [])),
                "example_anchor": URGENCY_ANCHORS.get(level, [""])[0] if URGENCY_ANCHORS.get(level) else ""
            })
        
        return {
            "total_levels": len(URGENCY_LEVELS),
            "levels": levels_info,
            "day_implemented": "Day 4",
            "validation_status": "Day 4.4 validated"
        }
        
    except Exception as e:
        logger.error(f"Urgency levels error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Urgency levels failed: {str(e)}")

@app.post("/urgency", tags=["Urgency"])
async def analyze_urgency(request: Dict[str, Any]):
    """
    Analyze urgency only.
    
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
        
        # Get urgency classifier
        from app.classification.urgency_classifier import get_urgency_classifier
        urgency_classifier = get_urgency_classifier()
        
        result = urgency_classifier.classify(text, return_scores=detailed)
        
        return {
            **result,
            "analysis_type": "urgency_only",
            "day_implemented": "Day 4",
            "validation": "Day 4.4 edge case hardened"
        }
        
    except Exception as e:
        logger.error(f"Urgency analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Urgency analysis failed: {str(e)}")

# ==================== COMPLETE ANALYSIS ENDPOINTS (Day 4.3) ====================

@app.post("/analyze", tags=["Analysis"])
async def analyze_complaint(request: Dict[str, Any]):
    """
    Complete analysis: Category + Urgency (Day 4.3 integration).
    
    Request body:
    {
        "text": "complaint text here",
        "detailed": false
    }
    
    Day 4.3 Principles:
    1. Category logic untouched
    2. Urgency logic independent  
    3. No coupling between systems
    4. Single clean response object
    """
    try:
        text = request.get("text", "")
        detailed = request.get("detailed", False)
        
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        result = classification_service.classify_with_urgency(text, detailed)
        
        return {
            **result,
            "analysis_type": "complete_analysis",
            "day_implemented": "Day 4.3",
            "integration_principles": [
                "Category logic untouched",
                "Urgency logic independent",
                "No coupling between systems",
                "Single clean response object"
            ]
        }
        
    except Exception as e:
        logger.error(f"Complete analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/analyze/batch", tags=["Analysis"])
async def analyze_complaints_batch(request: Dict[str, Any]):
    """
    Complete analysis for multiple complaints.
    
    Request body:
    {
        "texts": ["text1", "text2", ...]
    }
    """
    try:
        texts = request.get("texts", [])
        
        if not texts:
            raise HTTPException(status_code=400, detail="Texts list is required")
        
        results = []
        for text in texts:
            result = classification_service.classify_with_urgency(text, detailed=False)
            results.append(result)
        
        # Sort by priority if available
        results_with_priority = [r for r in results if "combined_priority" in r]
        if results_with_priority:
            results_with_priority.sort(
                key=lambda x: x["combined_priority"]["priority_score"], 
                reverse=True
            )
        
        return {
            "count": len(results),
            "results": results_with_priority + [r for r in results if "combined_priority" not in r],
            "summary": {
                "total_analyzed": len(results),
                "urgency_distribution": {
                    level: sum(1 for r in results if r.get("urgency") == level)
                    for level in URGENCY_LEVELS
                },
                "priority_distribution": {
                    "critical": sum(1 for r in results if r.get("combined_priority", {}).get("priority_tier") == "TIER_1_CRITICAL"),
                    "high": sum(1 for r in results if r.get("combined_priority", {}).get("priority_tier") == "TIER_2_HIGH"),
                    "medium": sum(1 for r in results if r.get("combined_priority", {}).get("priority_tier") == "TIER_3_MEDIUM"),
                    "low": sum(1 for r in results if r.get("combined_priority", {}).get("priority_tier") == "TIER_4_LOW"),
                    "routine": sum(1 for r in results if r.get("combined_priority", {}).get("priority_tier") == "TIER_5_ROUTINE"),
                }
            },
            "batch_processing": True,
            "sorted_by_priority": True
        }
        
    except Exception as e:
        logger.error(f"Batch analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")

@app.post("/analyze/validate", tags=["Analysis"])
async def validate_analysis(request: Dict[str, Any]):
    """
    Day 4.4: Validate cross-language consistency.
    
    Request body:
    {
        "english_text": "English complaint here",
        "hindi_text": "Hindi complaint here"
    }
    """
    try:
        english_text = request.get("english_text", "")
        hindi_text = request.get("hindi_text", "")
        
        if not english_text or not hindi_text:
            raise HTTPException(status_code=400, detail="Both English and Hindi texts are required")
        
        # Validate cross-language consistency
        validation_result = classification_service.validate_cross_language_consistency(
            english_text, hindi_text
        )
        
        return {
            **validation_result,
            "validation_type": "cross_language_consistency",
            "day_implemented": "Day 4.4",
            "purpose": "Ensure same meaning → same urgency regardless of language"
        }
        
    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")

# ==================== ERROR HANDLING ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    logger.error(f"HTTP Exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_type": "http_exception",
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc),
            "error_type": "unhandled_exception",
            "timestamp": datetime.now().isoformat(),
            "support": "Check /health endpoint for service status"
        }
    )

@app.get("/openapi.json", include_in_schema=False)
async def get_openapi():
    """Get OpenAPI schema"""
    return app.openapi()

def start():
    """Start the FastAPI server"""
    logger.info(f"Starting {SERVICE_NAME} v{SERVICE_VERSION}")
    logger.info(f"Days implemented: 1, 2, 3, 4 (Complete through Day 4.4)")
    logger.info(f"API Documentation: http://localhost:{API_PORT}/docs")
    logger.info(f"Health Check: http://localhost:{API_PORT}/health")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=API_PORT,
        reload=True,  # Auto-reload in development
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    start()