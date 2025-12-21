#!/usr/bin/env python3
"""
Admin Queue Service
Day 8.3 - Builds prioritized issue queue for admins
"""

from typing import List, Dict
from datetime import datetime

from app.intelligence.issue_health import IssueHealthScorer
from app.intelligence.severity import IssueSeverityEngine
from app.intelligence.sla import SLARiskEngine
from app.intelligence.priority import IssuePriorityEngine
from app.observability.logger import get_logger

logger = get_logger(__name__)


class AdminQueueService:
    """
    Builds and sorts the admin priority queue.
    
    Enriches issues with:
    - Health score
    - Severity
    - SLA risk
    - Priority score
    """

    @classmethod
    def build(cls, issues: List) -> List[Dict]:
        """
        Build priority queue from issues.
        
        Args:
            issues: List of IssueModel instances
            
        Returns:
            List of enriched issues sorted by priority (descending)
        """
        enriched = []

        for issue in issues:
            # Compute intelligence signals
            health = IssueHealthScorer.compute(issue)
            severity = IssueSeverityEngine.compute(issue)
            sla = SLARiskEngine.evaluate(issue, severity["numeric"])
            priority = IssuePriorityEngine.compute(
                issue,
                severity_numeric=severity["numeric"],
                health_score=health["score"],
                sla_risk=sla["risk"]
            )

            # Build enriched record
            enriched.append({
                "issue": issue,
                "health": health,
                "severity": severity,
                "sla": sla,
                "priority": priority
            })

        # Sort by priority score (descending)
        sorted_queue = sorted(
            enriched,
            key=lambda x: x["priority"]["priority_score"],
            reverse=True
        )

        logger.info(
            "admin_queue_built",
            total_issues=len(sorted_queue),
            top_priority_score=sorted_queue[0]["priority"]["priority_score"] if sorted_queue else 0
        )

        return sorted_queue
    
    @classmethod
    def to_api_format(cls, enriched_issues: List[Dict]) -> List[Dict]:
        """
        Convert enriched issues to API-friendly format.
        
        Args:
            enriched_issues: List of enriched issue records
            
        Returns:
            List of API-formatted issue records
        """
        formatted = []

        for record in enriched_issues:
            issue = record["issue"]
            health = record["health"]
            severity = record["severity"]
            sla = record["sla"]
            priority = record["priority"]

            formatted.append({
                "issue_id": issue.id,
                "hostel": issue.hostel,
                "category": issue.category,
                "status": issue.status,
                
                "priority": {
                    "score": priority["priority_score"],
                    "label": priority["priority_label"]
                },
                
                "severity": {
                    "label": severity["severity"],
                    "numeric": severity["numeric"],
                    "description": severity.get("description", "")
                },
                
                "health": {
                    "score": health["score"],
                    "label": health["label"]
                },
                
                "sla": {
                    "risk": sla["risk"],
                    "time_remaining_minutes": sla["time_remaining_minutes"],
                    "is_breached": sla.get("is_breached", False)
                },
                
                "complaints": {
                    "total": issue.complaint_count,
                    "unique": issue.unique_complaint_count,
                    "duplicates": issue.duplicate_count
                },
                
                "timestamps": {
                    "created_at": issue.created_at.isoformat(),
                    "last_updated": issue.last_updated.isoformat()
                }
            })

        return formatted