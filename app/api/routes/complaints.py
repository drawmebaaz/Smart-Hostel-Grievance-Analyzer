#!/usr/bin/env python3
"""
Complaint API endpoints
Day 5.5
"""

from fastapi import APIRouter, HTTPException, status
from typing import List

from app.api.schemas import (
    ComplaintRequest, 
    ComplaintResponse,
    BatchComplaintRequest
)
from app.services.issue_service import get_issue_service
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/complaints", tags=["Complaints"])


@router.post(
    "/",
    response_model=ComplaintResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a new complaint",
    description="Process a complaint through the complete pipeline: classification, urgency detection, embedding, and issue aggregation."
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
    """
    try:
        service = get_issue_service()
        
        result = service.process_complaint(
            text=payload.text,
            hostel=payload.hostel,
            complaint_id=payload.complaint_id,
            metadata=payload.metadata
        )
        
        if not result.get("success", False):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=result.get("error", "Complaint processing failed")
            )
        
        logger.info(f"Complaint submitted successfully: {result['complaint_id']}")
        return result
        
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in submit_complaint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while processing complaint"
        )


@router.post(
    "/batch",
    response_model=List[ComplaintResponse],
    summary="Submit multiple complaints",
    description="Process multiple complaints in batch. Each complaint is processed independently but more efficiently."
)
async def submit_batch_complaints(payload: BatchComplaintRequest):
    """
    Submit multiple complaints in batch.
    
    This is more efficient for processing large numbers of complaints.
    Returns individual results for each complaint.
    """
    try:
        if len(payload.complaints) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Batch size cannot exceed 100 complaints"
            )
        
        service = get_issue_service()
        
        results = service.batch_process_complaints(payload.complaints)
        
        # Check for any failures
        failures = [r for r in results if not r.get("success", False)]
        if failures:
            logger.warning(f"Batch processing had {len(failures)} failures")
        
        logger.info(f"Batch processed {len(results)} complaints")
        return results
        
    except Exception as e:
        logger.error(f"Batch processing failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch processing failed: {str(e)}"
        )