#!/usr/bin/env python3
"""
Issue API endpoints
Day 5.5
"""

from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional

from app.api.schemas import IssueSummary, IssueDetails, SystemStats
from app.services.issue_service import get_issue_service
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/issues", tags=["Issues"])


@router.get(
    "/",
    response_model=List[IssueSummary],
    summary="List all issues",
    description="Get a summary of all active issues, sorted by last update time."
)
async def list_issues(
    include_complaints: bool = Query(
        False, 
        description="Include full complaint details in response (can be large)"
    ),
    limit: int = Query(
        50, 
        ge=1, 
        le=200, 
        description="Maximum number of issues to return"
    ),
    category: Optional[str] = Query(
        None, 
        description="Filter issues by category"
    ),
    hostel: Optional[str] = Query(
        None, 
        description="Filter issues by hostel"
    )
):
    """
    List all issues with optional filtering.
    
    By default returns a summary view. Set include_complaints=True
    to get full complaint details (warning: can be large).
    """
    try:
        service = get_issue_service()
        
        if include_complaints:
            # Get full details
            result = service.get_issues(include_complaints=True)
            issues = result["issues"]
        else:
            # Get summary only
            result = service.get_issues(include_complaints=False)
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
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve issues"
        )


@router.get(
    "/{issue_id}",
    response_model=IssueDetails,
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
        service = get_issue_service()
        
        issue_details = service.get_issue_details(issue_id)
        
        if not issue_details:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Issue '{issue_id}' not found"
            )
        
        logger.info(f"Returning details for issue: {issue_id}")
        return issue_details
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get issue {issue_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve issue: {str(e)}"
        )


@router.get(
    "/stats/system",
    response_model=SystemStats,
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
        service = get_issue_service()
        stats = service.get_system_stats()
        
        logger.info("Returning system statistics")
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get system stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve system statistics"
        )


@router.delete(
    "/reset",
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
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset system: {str(e)}"
        )