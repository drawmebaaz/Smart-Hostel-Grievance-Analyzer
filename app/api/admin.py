#!/usr/bin/env python3
"""
Admin API Endpoints
Day 6.4 - Issue lifecycle management
"""

from fastapi import APIRouter, HTTPException, status
from typing import Optional
from pydantic import BaseModel

from app.services.issue_service_day6 import get_issue_service_day6
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/admin", tags=["Admin"])


# ==================== REQUEST SCHEMAS ====================

class IssueStatusUpdate(BaseModel):
    """Schema for issue status update"""
    status: str  # OPEN, IN_PROGRESS, RESOLVED, REOPENED
    
    class Config:
        schema_extra = {
            "example": {
                "status": "IN_PROGRESS"
            }
        }


# ==================== ENDPOINTS ====================

@router.put(
    "/issues/{issue_id}/status",
    summary="Update issue status",
    description="Update the lifecycle status of an issue (admin action)"
)
async def update_issue_status(
    issue_id: str,
    update: IssueStatusUpdate
):
    """
    Update issue status.
    
    Available statuses:
    - OPEN: Newly created, no action yet
    - IN_PROGRESS: Acknowledged, being handled
    - RESOLVED: Fixed
    - REOPENED: New complaints after resolution
    """
    try:
        service = get_issue_service_day6()
        
        result = service.update_issue_status(issue_id, update.status)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Issue '{issue_id}' not found"
            )
        
        logger.info(f"Issue status updated: {issue_id} → {update.status}")
        
        return {
            "success": True,
            "issue_id": issue_id,
            "new_status": update.status,
            "issue": result
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to update issue status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update issue status: {str(e)}"
        )


@router.get(
    "/issues/by-status/{status}",
    summary="Get issues by status",
    description="Retrieve all issues with a specific status"
)
async def get_issues_by_status(
    status: str,
    limit: int = 50
):
    """
    Get issues filtered by status.
    
    Status values: OPEN, IN_PROGRESS, RESOLVED, REOPENED
    """
    try:
        service = get_issue_service_day6()
        
        result = service.get_issues(status=status, limit=limit)
        
        return {
            "status": status,
            "count": result["count"],
            "issues": result["issues"]
        }
        
    except Exception as e:
        logger.error(f"Failed to get issues by status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve issues: {str(e)}"
        )


@router.get(
    "/metrics",
    summary="Get system metrics",
    description="Get comprehensive system metrics and statistics"
)
async def get_system_metrics():
    """
    Get system-wide metrics including:
    - Complaint statistics
    - Session statistics
    - Heuristic triggers
    - Performance metrics
    - Error counts
    """
    try:
        from app.metrics.system_metrics import get_metrics
        
        metrics = get_metrics()
        snapshot = metrics.get_snapshot()
        
        return {
            "success": True,
            "metrics": snapshot
        }
        
    except Exception as e:
        logger.error(f"Failed to get metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve metrics: {str(e)}"
        )


@router.post(
    "/metrics/reset",
    summary="Reset metrics (dev only)",
    description="⚠️ DEVELOPMENT ONLY: Reset all system metrics"
)
async def reset_metrics():
    """
    Reset all system metrics.
    
    ⚠️ WARNING: Development only - do not use in production!
    """
    try:
        from app.metrics.system_metrics import get_metrics
        
        metrics = get_metrics()
        metrics.reset()
        
        logger.warning("System metrics reset via admin API")
        
        return {
            "success": True,
            "message": "System metrics reset",
            "warning": "All metrics have been cleared"
        }
        
    except Exception as e:
        logger.error(f"Failed to reset metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset metrics: {str(e)}"
        )