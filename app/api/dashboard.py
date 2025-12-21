#!/usr/bin/env python3
"""
Dashboard API Endpoints
Day 8.4 - Admin dashboard data contract
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime, timedelta

from app.services.admin_queue import AdminQueueService
from app.db.session import get_db_context
from app.repositories.issue_repository import IssueRepository
from app.repositories.complaint_repository import ComplaintRepository
from app.intelligence.issue_health import IssueHealthScorer
from app.intelligence.severity import IssueSeverityEngine
from app.intelligence.sla import SLARiskEngine
from app.observability.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/admin/dashboard", tags=["Dashboard"])


@router.get(
    "/priority-issues",
    summary="Get priority issue queue",
    description="Returns issues sorted by priority with intelligence signals"
)
async def get_priority_issues(
    limit: int = Query(50, ge=1, le=200),
    status: Optional[str] = Query(None, description="Filter by status")
):
    """
    Main priority queue endpoint.
    
    Returns issues enriched with:
    - Priority score & label
    - Severity assessment
    - Health status
    - SLA risk
    - Complaint statistics
    """
    try:
        logger.info(
            "priority_queue_requested",
            limit=limit,
            status_filter=status
        )
        
        with get_db_context() as db:
            issue_repo = IssueRepository(db)
            
            # Get issues
            status_enum = None
            if status:
                from app.db.models.issue import IssueStatus
                try:
                    status_enum = IssueStatus[status.upper()]
                except KeyError:
                    pass
            
            issues = issue_repo.get_all(
                status=status_enum,
                limit=limit,
                eager_load_complaints=False
            )
            
            # Build priority queue
            enriched = AdminQueueService.build(issues)
            
            # Convert to API format
            formatted = AdminQueueService.to_api_format(enriched)
            
            logger.info(
                "priority_queue_returned",
                count=len(formatted)
            )
            
            return {
                "generated_at": datetime.utcnow().isoformat(),
                "count": len(formatted),
                "issues": formatted
            }
    
    except Exception as e:
        logger.error(
            "priority_queue_failed",
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate priority queue: {str(e)}"
        )


@router.get(
    "/health-summary",
    summary="Get system health overview",
    description="Returns aggregated health statistics"
)
async def get_health_summary():
    """
    System health overview.
    
    Returns distributions of:
    - Health labels
    - Severity levels
    - SLA risk status
    """
    try:
        logger.info("health_summary_requested")
        
        with get_db_context() as db:
            issue_repo = IssueRepository(db)
            issues = issue_repo.get_all(limit=1000)
            
            # Filter to only OPEN, IN_PROGRESS, and REOPENED issues (exclude RESOLVED)
            from app.db.models.issue import IssueStatus
            active_issues = [
                issue for issue in issues 
                if issue.status in (IssueStatus.OPEN, IssueStatus.IN_PROGRESS, IssueStatus.REOPENED)
            ]
            
            # Initialize counters
            health_dist = {"HEALTHY": 0, "MONITOR": 0, "WARNING": 0, "CRITICAL": 0, "EMERGENCY": 0}
            severity_dist = {"SEV-1": 0, "SEV-2": 0, "SEV-3": 0, "SEV-4": 0}
            sla_dist = {"OK": 0, "WARNING": 0, "BREACHING": 0}
            
            # Compute distributions using only active issues
            for issue in active_issues:
                health = IssueHealthScorer.compute(issue)
                severity = IssueSeverityEngine.compute(issue)
                sla = SLARiskEngine.evaluate(issue, severity["numeric"])
                
                health_dist[health["label"]] += 1
                severity_dist[severity["severity"]] += 1
                sla_dist[sla["risk"]] += 1
            
            logger.info(
                "health_summary_returned",
                total_issues=len(issues),
                active_issues=len(active_issues)
            )
            
            return {
                "total_issues": len(active_issues),
                "health_distribution": health_dist,
                "severity_distribution": severity_dist,
                "sla_risk_distribution": sla_dist
            }
    
    except Exception as e:
        logger.error(
            "health_summary_failed",
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate health summary: {str(e)}"
        )


@router.get(
    "/sla-timers",
    summary="Get SLA countdown timers",
    description="Returns issues breaching or at risk of breaching SLA"
)
async def get_sla_timers():
    """
    SLA timer feed.
    
    Returns:
    - Issues currently breaching SLA
    - Issues in warning state
    """
    try:
        logger.info("sla_timers_requested")
        
        with get_db_context() as db:
            issue_repo = IssueRepository(db)
            issues = issue_repo.get_all(limit=500)
            
            breaching = []
            warning = []
            
            for issue in issues:
                if issue.status == "RESOLVED":
                    continue
                
                severity = IssueSeverityEngine.compute(issue)
                sla = SLARiskEngine.evaluate(issue, severity["numeric"])
                
                record = {
                    "issue_id": issue.id,
                    "hostel": issue.hostel,
                    "category": issue.category,
                    "severity": severity["severity"]
                }
                
                if sla["risk"] == "BREACHING":
                    record["minutes_overdue"] = sla.get("breach_minutes", 0)
                    breaching.append(record)
                elif sla["risk"] == "WARNING":
                    record["minutes_remaining"] = sla["time_remaining_minutes"]
                    warning.append(record)
            
            # Sort by time
            breaching.sort(key=lambda x: x["minutes_overdue"], reverse=True)
            warning.sort(key=lambda x: x["minutes_remaining"])
            
            logger.info(
                "sla_timers_returned",
                breaching_count=len(breaching),
                warning_count=len(warning)
            )
            
            return {
                "breaching": breaching,
                "warning": warning
            }
    
    except Exception as e:
        logger.error(
            "sla_timers_failed",
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate SLA timers: {str(e)}"
        )


@router.get(
    "/trends",
    summary="Get trend snapshot",
    description="Returns complaint and issue trends over time window"
)
async def get_trends(
    window: str = Query("24h", description="Time window: 1h, 6h, 24h, 7d")
):
    """
    Trend analysis over time window.
    
    Returns:
    - New complaints
    - New issues
    - Resolved issues
    - Percentage changes
    """
    try:
        logger.info(
            "trends_requested",
            window=window
        )
        
        # Parse window
        hours_map = {
            "1h": 1,
            "6h": 6,
            "24h": 24,
            "7d": 168
        }
        hours = hours_map.get(window, 24)
        
        with get_db_context() as db:
            issue_repo = IssueRepository(db)
            complaint_repo = ComplaintRepository(db)
            
            now = datetime.utcnow()
            window_start = now - timedelta(hours=hours)
            prev_window_start = window_start - timedelta(hours=hours)
            
            # Current window
            current_complaints = len([
                c for c in complaint_repo.get_recent(hours=hours)
            ])
            
            current_issues = len([
                i for i in issue_repo.get_all(limit=1000)
                if i.created_at >= window_start
            ])
            
            current_resolved = len([
                i for i in issue_repo.get_all(limit=1000)
                if i.resolved_at and i.resolved_at >= window_start
            ])
            
            # Previous window (for comparison)
            prev_complaints = len([
                c for c in complaint_repo.get_recent(hours=hours*2)
                if c.created_at < window_start and c.created_at >= prev_window_start
            ])
            
            prev_issues = len([
                i for i in issue_repo.get_all(limit=1000)
                if i.created_at < window_start and i.created_at >= prev_window_start
            ])
            
            prev_resolved = len([
                i for i in issue_repo.get_all(limit=1000)
                if i.resolved_at and i.resolved_at < window_start and i.resolved_at >= prev_window_start
            ])
            
            # Calculate changes
            def pct_change(current, previous):
                if previous == 0:
                    return 0.0
                return round(((current - previous) / previous) * 100, 1)
            
            logger.info(
                "trends_returned",
                window=window,
                current_complaints=current_complaints
            )
            
            return {
                "window": window,
                "complaints": {
                    "total": current_complaints,
                    "change_pct": pct_change(current_complaints, prev_complaints)
                },
                "new_issues": {
                    "count": current_issues,
                    "change_pct": pct_change(current_issues, prev_issues)
                },
                "resolved_issues": {
                    "count": current_resolved,
                    "change_pct": pct_change(current_resolved, prev_resolved)
                }
            }
    
    except Exception as e:
        logger.error(
            "trends_failed",
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate trends: {str(e)}"
        )