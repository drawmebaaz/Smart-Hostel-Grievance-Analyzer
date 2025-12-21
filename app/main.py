#!/usr/bin/env python3
"""
FastAPI server for Smart Hostel Grievance Analyzer.
Day 5: Complete API with category + urgency + issue aggregation.
ENGLISH-ONLY SCOPE: Optimized for English complaint processing.
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
from datetime import datetime
import uvicorn
from app.services.issue_service_day7a import get_issue_service_day7a
from app.middleware.request_context import RequestContextMiddleware
from app.api.observability import router as observability_router


from app.config import SERVICE_NAME, SERVICE_VERSION, API_PORT
from app.services.embedding_service import get_embedding_service
from app.services.classification_service import get_classification_service
from app.services.issue_service import get_issue_service
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
issue_service = get_issue_service()

logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title=SERVICE_NAME,
    version=SERVICE_VERSION,
    description="AI Service for Hostel Complaint Processing with Issue Aggregation (English Scope)",
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
        },
        {
            "name": "Complaints",
            "description": "Submit and process complaints (Day 5)"
        },
        {
            "name": "Issues",
            "description": "View and manage aggregated issues (Day 5)"
        },
        {
            "name": "Debug",
            "description": "Debug endpoints for testing"
        }
    ]
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestContextMiddleware)
app.include_router(observability_router)

# ==================== HEALTH & INFO ENDPOINTS ====================

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint with service info - ENGLISH ONLY SCOPE"""
    return {
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "status": "operational",
        "scope": "English-only complaint processing",
        "description": "Smart Hostel Grievance Analyzer AI Service (English Scope)",
        "features": [
            "English text processing (optimized for accuracy)",
            "Semantic embedding generation",
            "Category classification (10 hostel categories)",
            "Urgency detection (4 levels: Low/Medium/High/Critical)",
            "Issue aggregation & duplicate detection",
            "Complete complaint analysis",
            "Batch processing support"
        ],
        "language_support": {
            "current": "English-only (for precise duplicate detection)",
            "future_roadmap": ["Multilingual/Hinglish support", "Auto-translation"],
            "note": "English scope ensures high-precision issue aggregation"
        },
        "days_completed": [1, 2, 3, 4, 5],
        "endpoints": {
            "health": "/health",
            "info": "/info",
            "day5_status": "/day5/status",
            "scope": "/scope",
            "complaints": "/complaints",
            "issues": "/issues",
            "embedding": ["/embed", "/embed/batch"],
            "classification": ["/classify", "/classify/batch", "/classify/explain"],
            "urgency": ["/urgency", "/urgency/levels"],
            "analysis": ["/analyze", "/analyze/batch"]
        }
    }

@app.get("/scope", tags=["Health"])
async def get_scope():
    """Get system scope and language limitations"""
    return {
        "language_scope": "english_only",
        "reasoning": "English-only input ensures high-precision duplicate detection and issue aggregation",
        "validation_rules": [
            "Rejects Hindi script characters (Devanagari)",
            "Warns about heavy Hinglish patterns",
            "Allows hostel names and technical terms",
            "Focuses on semantic accuracy over language coverage"
        ],
        "benefits": [
            "Reliable duplicate detection (similarity > 0.75)",
            "Consistent category classification",
            "No silent translation errors",
            "Predictable system behavior"
        ],
        "future_enhancements": [
            "Multilingual support with explicit translation",
            "Hinglish normalization layer",
            "Language detection and routing"
        ],
        "recommended_usage": "Submit complaints in English for best results",
        "api_example": {
            "valid": {
                "text": "No water supply in BH-3 since morning",
                "hostel": "BH-3"
            },
            "invalid": {
                "text": "Paani nahi aa raha BH-3 me",
                "hostel": "BH-3",
                "reason": "Contains Hinglish terms"
            }
        }
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    try:
        # Test service health
        embedding_test = embedding_service.generate_embedding("test", normalize_hinglish=False)
        classification_test = classification_service.classify_complaint("test")
        issue_stats = issue_service.get_system_stats()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "embedding_service": "operational",
                "classification_service": "operational",
                "urgency_service": "operational",
                "issue_service": "operational"
            },
            "checks": {
                "embedding_dimension": len(embedding_test),
                "classification_working": "category" in classification_test,
                "issue_aggregation_working": "issue_system" in issue_stats,
                "day_4_integrated": True,
                "day_5_complete": True
            },
            "language_scope": "english_only"
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "degraded",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "services": {
                "embedding_service": "check_failed",
                "classification_service": "check_failed",
                "issue_service": "check_failed"
            }
        }

@app.get("/info", tags=["Health"])
async def service_info():
    """Get service information and capabilities"""
    try:
        embedding_info = embedding_service.get_embedding_info()
        classification_stats = classification_service.get_classification_stats()
        issue_stats = issue_service.get_system_stats()
        
        return {
            "service": SERVICE_NAME,
            "version": SERVICE_VERSION,
            "language_scope": "english_only",
            "embedding": embedding_info,
            "classification": classification_stats,
            "issue_aggregation": issue_stats["issue_system"],
            "preprocessing": {
                "hinglish_normalization": False,  # Disabled for English scope
                "whitespace_cleaning": True,
                "lowercasing": True,
                "multilingual_support": False
            },
            "architecture": "FastAPI + Sentence Transformers + sklearn",
            "days_implemented": {
                "day_1_2": "Text processing & embedding pipeline",
                "day_3": "Category classification system",
                "day_4": "Urgency detection & integration",
                "day_5": "Issue aggregation & duplicate detection"
            },
            "api_version": "2.0.0",
            "language_note": "System optimized for English input only. Non-English text may produce unreliable results."
        }
        
    except Exception as e:
        logger.error(f"Service info error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Service info failed: {str(e)}")

@app.get("/day5/status", tags=["Health"])
async def day5_status():
    """Day 5 specific status check"""
    try:
        from app.issues.issue_manager import get_issue_manager
        
        manager = get_issue_manager()
        stats = manager.get_statistics()
        
        return {
            "day": 5,
            "status": "complete",
            "timestamp": datetime.now().isoformat(),
            "issue_system": {
                "total_issues": stats["total_issues"],
                "total_complaints": stats["total_complaints"],
                "unique_complaints": stats["unique_complaints"],
                "duplicate_rate": stats["duplicate_rate"],
                "categories_tracked": len(stats["categories"]),
                "hostels_tracked": len(stats["hostels"])
            },
            "features": [
                "Issue aggregation by category + hostel",
                "Semantic duplicate detection (threshold: 0.82)",
                "Urgency aggregation across complaints",
                "REST API for complaint submission",
                "Issue management endpoints",
                "System statistics"
            ],
            "language_optimization": "English-only for reliable duplicate detection"
        }
        
    except Exception as e:
        logger.error(f"Day 5 status check failed: {str(e)}")
        return {
            "day": 5,
            "status": "failed",
            "error": str(e)
        }

# ==================== DAY 5: COMPLAINTS ENDPOINTS ====================

from app.api.schemas import ComplaintRequest, ComplaintResponse, BatchComplaintRequest
from app.api.schemas import IssueSummary, IssueDetails, SystemStats

@app.post(
    "/complaints/",
    response_model=ComplaintResponse,
    status_code=201,
    tags=["Complaints"],
    summary="Submit a new complaint (English only)",
    description="Process a complaint through the complete pipeline: classification, urgency detection, embedding, and issue aggregation. English text required for reliable results."
)
async def submit_complaint(payload: ComplaintRequest):
    """
    Submit a new complaint.
    
    This endpoint:
    1. Classifies the complaint category (Day 3)
    2. Determines urgency level (Day 4)
    3. Generates embedding (Day 2)
    4. Groups with similar complaints into issues (Day 5)
    5. Returns comprehensive result
    
    IMPORTANT: English text required for reliable duplicate detection.
    """
    try:
        # Use Day 7A service instead of Day 6
        service = get_issue_service_day7a()
        
        result = service.process_complaint(
            text=payload.text,
            hostel=payload.hostel,  
            complaint_id=payload.complaint_id,
            metadata=payload.metadata
        )
        
        if not result.get("success", False):
            raise HTTPException(
                status_code=422,
                detail=result.get("error", "Complaint processing failed")
            )
        
        logger.info(f"Complaint submitted successfully: {result['complaint_id']}")
        return result
        
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in submit_complaint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while processing complaint"
        )

@app.post(
    "/complaints/batch",
    response_model=List[ComplaintResponse],
    tags=["Complaints"],
    summary="Submit multiple complaints (English only)",
    description="Process multiple complaints in batch. Each complaint is processed independently but more efficiently. English text required."
)
async def submit_batch_complaints(payload: BatchComplaintRequest):
    """
    Submit multiple complaints in batch.
    
    This is more efficient for processing large numbers of complaints.
    Returns individual results for each complaint.
    
    NOTE: All complaints should be in English for best results.
    """
    try:
        if len(payload.complaints) > 100:
            raise HTTPException(
                status_code=400,
                detail="Batch size cannot exceed 100 complaints"
            )
        
        results = issue_service.batch_process_complaints(payload.complaints)
        
        # Check for any failures
        failures = [r for r in results if not r.get("success", False)]
        if failures:
            logger.warning(f"Batch processing had {len(failures)} failures")
        
        logger.info(f"Batch processed {len(results)} complaints")
        return results
        
    except Exception as e:
        logger.error(f"Batch processing failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Batch processing failed: {str(e)}"
        )

# ==================== DAY 5: ISSUES ENDPOINTS ====================

@app.get(
    "/issues/",
    response_model=List[IssueSummary],
    tags=["Issues"],
    summary="List all issues",
    description="Get a summary of all active issues, sorted by last update time."
)
async def list_issues(
    include_complaints: bool = False,
    limit: int = 50,
    category: str = None,
    hostel: str = None
):
    """
    List all issues with optional filtering.
    
    By default returns a summary view. Set include_complaints=True
    to get full complaint details (warning: can be large).
    """
    try:
        if include_complaints:
            # Get full details
            result = issue_service.get_issues(include_complaints=True)
            issues = result["issues"]
        else:
            # Get summary only
            result = issue_service.get_issues(include_complaints=False)
            issues = result["issues"]
        
        # Apply filters
        if category:
            issues = [i for i in issues if i.get("category", "").lower() == category.lower()]
        
        if hostel:
            issues = [i for i in issues if i.get("hostel", "").lower() == hostel.lower()]
        
        # Apply limit
        issues = issues[:limit]
        
        logger.info(f"Returning {len(issues)} issues")
        return issues
        
    except Exception as e:
        logger.error(f"Failed to list issues: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve issues"
        )

@app.get(
    "/issues/{issue_id}",
    response_model=IssueDetails,
    tags=["Issues"],
    summary="Get issue details",
    description="Get detailed information about a specific issue including all complaints."
)
async def get_issue(issue_id: str):
    """
    Get detailed information about a specific issue.
    
    Includes:
    - Issue metadata
    - All complaints (with duplicate relationships)
    - Urgency statistics
    - Timeline information
    """
    try:
        issue_details = issue_service.get_issue_details(issue_id)
        
        if not issue_details:
            raise HTTPException(
                status_code=404,
                detail=f"Issue '{issue_id}' not found"
            )
        
        logger.info(f"Returning details for issue: {issue_id}")
        return issue_details
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get issue {issue_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve issue: {str(e)}"
        )

@app.get(
    "/issues/stats/system",
    response_model=SystemStats,
    tags=["Issues"],
    summary="Get system statistics",
    description="Get comprehensive statistics about the entire system including issue aggregation, classification, and embedding systems."
)
async def get_system_statistics():
    """
    Get comprehensive system statistics.
    
    Includes:
    - Issue aggregation statistics (Day 5)
    - Classification system stats (Day 3)
    - Embedding system info (Day 2)
    - Overall system health
    """
    try:
        stats = issue_service.get_system_stats()
        
        logger.info("Returning system statistics")
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get system stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve system statistics"
        )

@app.delete(
    "/issues/reset",
    tags=["Issues"],
    summary="Reset issue system (development only)",
    description="⚠️ DEVELOPMENT ONLY: Reset all issues and clear memory. Use for testing."
)
async def reset_issue_system():
    """
    Reset the issue system (development/testing only).
    
    ⚠️ WARNING: This clears all issues from memory!
    Only use in development/testing environments.
    """
    try:
        from app.issues.issue_manager import get_issue_manager
        
        manager = get_issue_manager()
        manager.reset()
        
        logger.warning("Issue system reset requested and completed")
        
        return {
            "success": True,
            "message": "Issue system reset completed",
            "warning": "All issues have been cleared from memory"
        }
        
    except Exception as e:
        logger.error(f"Failed to reset issue system: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reset system: {str(e)}"
        )

# ==================== EMBEDDING ENDPOINTS (Day 1-2) ====================

@app.post("/embed", tags=["Embeddings"])
async def embed_text(request: Dict[str, Any]):
    """
    Embed a single text.
    
    Request body:
    {
        "text": "complaint text here",
        "normalize_hinglish": false  # Disabled for English scope
    }
    """
    try:
        text = request.get("text", "")
        normalize_hinglish = request.get("normalize_hinglish", False)  # Default to False for English scope
        
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
            "normalized": normalize_hinglish,
            "language_note": "English text recommended for best embeddings"
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
        "normalize_hinglish": false,  # Disabled for English scope
        "batch_size": 32
    }
    """
    try:
        texts = request.get("texts", [])
        normalize_hinglish = request.get("normalize_hinglish", False)  # Default to False
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
            "normalized": normalize_hinglish,
            "language_scope": "english_recommended"
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
            "multilingual_support": False,  # Updated for English scope
            "language_scope": "english_only",
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
            },
            "language_optimization": "English-only training data"
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
    
    NOTE: English text recommended for accurate classification.
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
            "day_implemented": "Day 3",
            "language_note": "English text recommended"
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
    
    NOTE: English text recommended for all inputs.
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
            "batch_processing": True,
            "language_scope": "english_only"
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
    
    NOTE: Works best with English text.
    """
    try:
        text = request.get("text", "")
        
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        explanation = classification_service.explain_classification(text)
        
        return {
            **explanation,
            "explanation_type": "category_classification",
            "day_implemented": "Day 3",
            "language_note": "English text recommended"
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
            "validation_status": "Day 4.4 validated",
            "language_scope": "English anchor texts"
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
    
    NOTE: English text required for accurate urgency detection.
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
            "validation": "Day 4.4 edge case hardened",
            "language_note": "English text required for reliable results"
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
    
    IMPORTANT: English text required for reliable results.
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
            ],
            "language_scope": "english_only_for_reliability"
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
    
    NOTE: English text required for all inputs.
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
            "sorted_by_priority": True,
            "language_note": "English text required for reliable results"
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
    
    NOTE: Now primarily validates English text consistency.
    """
    try:
        english_text = request.get("english_text", "")
        hindi_text = request.get("hindi_text", "")
        
        if not english_text:
            raise HTTPException(status_code=400, detail="English text is required")
        
        # Note: Hindi text validation is deprecated in English scope
        warning = None
        if hindi_text:
            warning = "Hindi text validation is limited in English-only scope"
        
        # Validate English text consistency
        validation_result = classification_service.validate_cross_language_consistency(
            english_text, hindi_text if hindi_text else ""
        )
        
        return {
            **validation_result,
            "validation_type": "english_consistency_check",
            "day_implemented": "Day 4.4",
            "purpose": "Ensure semantic consistency for reliable urgency detection",
            "language_scope": "english_focused",
            "warning": warning
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
            "timestamp": datetime.now().isoformat(),
            "language_scope": "english_only"
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
            "support": "Check /health endpoint for service status",
            "language_note": "Service optimized for English input"
        }
    )

@app.get("/openapi.json", include_in_schema=False)
async def get_openapi():
    """Get OpenAPI schema"""
    return app.openapi()

# ==================== DEBUG ENDPOINTS ====================

@app.post("/debug/similarity", tags=["Debug"])
async def debug_similarity(request: Dict[str, Any]):
    """Debug endpoint to check similarity between texts"""
    try:
        from app.preprocessing.text_cleaner import preprocess_text
        from app.issues.similarity import cosine_similarity
        
        text1 = request.get("text1", "")
        text2 = request.get("text2", "")
        
        if not text1 or not text2:
            raise HTTPException(status_code=400, detail="Both texts required")
        
        # PREPROCESS both texts before embedding
        clean_text1 = preprocess_text(text1, normalize_hinglish=False)  # No Hinglish normalization
        clean_text2 = preprocess_text(text2, normalize_hinglish=False)  # No Hinglish normalization
        
        # Get embeddings (with normalize_hinglish=False)
        emb1 = embedding_service.generate_embedding(clean_text1, normalize_hinglish=False)
        emb2 = embedding_service.generate_embedding(clean_text2, normalize_hinglish=False)
        
        # Calculate similarity
        similarity = cosine_similarity(emb1, emb2)
        
        return {
            "original": {
                "text1": text1,
                "text2": text2
            },
            "preprocessed": {
                "text1": clean_text1,
                "text2": clean_text2
            },
            "similarity": round(similarity, 4),
            "embedding_length": len(emb1),
            "is_duplicate_088": similarity >= 0.88,  # New strict threshold
            "is_duplicate_082": similarity >= 0.82,
            "is_duplicate_075": similarity >= 0.75,
            "note": "No Hinglish normalization applied. English text recommended.",
            "language_scope": "english_optimized"
        }
        
    except Exception as e:
        logger.error(f"Debug similarity failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Debug failed: {str(e)}")

def start():
    """Start the FastAPI server"""
    logger.info(f"🚀 Starting {SERVICE_NAME} v{SERVICE_VERSION}")
    logger.info(f"📅 Days implemented: 1, 2, 3, 4, 5")
    logger.info(f"🌐 Language Scope: ENGLISH ONLY (optimized for reliability)")
    logger.info(f"📚 API Documentation: http://localhost:{API_PORT}/docs")
    logger.info(f"❤️  Health Check: http://localhost:{API_PORT}/health")
    logger.info(f"🔍 Scope Info: http://localhost:{API_PORT}/scope")
    logger.info(f"📊 Day 5 Status: http://localhost:{API_PORT}/day5/status")
    logger.info("\nDay 5 Features:")
    logger.info("  ✅ Issue aggregation (category + hostel)")
    logger.info("  ✅ Semantic duplicate detection (English optimized)")
    logger.info("  ✅ Complaint grouping into issues")
    logger.info("  ✅ REST API for complaint submission")
    logger.info("  ✅ Issue management endpoints")
    logger.info("\n⚠️  IMPORTANT:")
    logger.info("  - System optimized for English input only")
    logger.info("  - Non-English text may produce unreliable results")
    logger.info("  - High precision duplicate detection requires English")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=API_PORT,
        reload=True,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    start()