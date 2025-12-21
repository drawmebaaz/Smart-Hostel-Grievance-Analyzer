#!/usr/bin/env python3
"""
SLA Risk Engine
Day 8.2 - Evaluates SLA compliance risk
"""

from datetime import datetime
from typing import Dict


class SLARiskEngine:
    """
    Evaluates SLA risk based on:
    1. Severity-based SLA targets
    2. Time elapsed
    3. Current status
    
    Risk levels: OK, WARNING, BREACHING
    """

    # SLA targets in hours by severity
    SLA_HOURS = {
        1: 1,    # SEV-1: 1 hour
        2: 6,    # SEV-2: 6 hours
        3: 24,   # SEV-3: 24 hours
        4: 72    # SEV-4: 72 hours
    }

    @classmethod
    def evaluate(cls, issue, severity_numeric: int) -> Dict:
        """
        Evaluate SLA risk for an issue.
        
        Args:
            issue: IssueModel instance
            severity_numeric: Numeric severity (1-4)
            
        Returns:
            Dict with risk level, time info, and breach status
        """
        # Resolved issues have no SLA risk
        if issue.status == "RESOLVED":
            return {
                "risk": "OK",
                "elapsed_hours": 0,
                "sla_hours": cls.SLA_HOURS[severity_numeric],
                "time_remaining_minutes": 0,
                "is_breached": False
            }

        # Calculate elapsed time
        now = datetime.utcnow()
        elapsed = (now - issue.created_at).total_seconds() / 3600
        sla = cls.SLA_HOURS[severity_numeric]

        # Calculate ratio and time remaining
        ratio = elapsed / sla
        time_remaining_hours = max(0, sla - elapsed)
        time_remaining_minutes = int(time_remaining_hours * 60)

        # Determine risk level
        if ratio >= 1.0:
            risk = "BREACHING"
            is_breached = True
        elif ratio >= 0.5:
            risk = "WARNING"
            is_breached = False
        else:
            risk = "OK"
            is_breached = False

        return {
            "risk": risk,
            "elapsed_hours": round(elapsed, 2),
            "sla_hours": sla,
            "time_remaining_minutes": time_remaining_minutes,
            "is_breached": is_breached,
            "breach_minutes": int((elapsed - sla) * 60) if is_breached else 0
        }