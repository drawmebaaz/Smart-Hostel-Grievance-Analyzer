#!/usr/bin/env python3
"""
Issue Priority Engine
Day 8.3 - Computes priority score for issue ranking
"""

from datetime import datetime
from typing import Dict


class IssuePriorityEngine:
    """
    Computes priority score (0-100) based on:
    1. Severity (0-40 points)
    2. SLA risk (0-25 points)
    3. Health (0-20 points)
    4. Volume (0-10 points)
    5. Recency (0-5 points)
    
    Higher score = higher priority
    """

    SEVERITY_WEIGHT = {
        1: 40,  # SEV-1
        2: 30,  # SEV-2
        3: 20,  # SEV-3
        4: 10   # SEV-4
    }

    SLA_WEIGHT = {
        "BREACHING": 25,
        "WARNING": 15,
        "OK": 0
    }

    @classmethod
    def compute(cls, issue, severity_numeric: int, health_score: float, sla_risk: str) -> Dict:
        """
        Compute priority score for an issue.
        
        Args:
            issue: IssueModel instance
            severity_numeric: Numeric severity (1-4)
            health_score: Health score (0-100)
            sla_risk: SLA risk level (OK/WARNING/BREACHING)
            
        Returns:
            Dict with priority score and component breakdown
        """
        score = 0
        breakdown = {}

        # 1. Severity weight (0-40)
        sev_weight = cls.SEVERITY_WEIGHT.get(severity_numeric, 10)
        breakdown["severity"] = sev_weight
        score += sev_weight

        # 2. SLA weight (0-25)
        sla_weight = cls.SLA_WEIGHT.get(sla_risk, 0)
        breakdown["sla"] = sla_weight
        score += sla_weight

        # 3. Health weight (0-20)
        # Inverted: worse health = higher priority
        health_weight = round((100 - health_score) * 0.2, 2)
        breakdown["health"] = health_weight
        score += health_weight

        # 4. Volume weight (0-10)
        volume_weight = min(issue.unique_complaint_count * 2, 10)
        breakdown["volume"] = volume_weight
        score += volume_weight

        # 5. Recency weight (0-5)
        age_hours = (datetime.utcnow() - issue.created_at).total_seconds() / 3600
        if age_hours < 1:
            recency = 5
        elif age_hours < 6:
            recency = 3
        elif age_hours < 24:
            recency = 1
        else:
            recency = 0

        breakdown["recency"] = recency
        score += recency

        # Priority label based on score
        priority_label = cls._label(score)

        return {
            "priority_score": round(score, 2),
            "priority_label": priority_label,
            "breakdown": breakdown
        }
    
    @staticmethod
    def _label(score: float) -> str:
        """Convert priority score to label"""
        if score >= 75:
            return "CRITICAL"
        elif score >= 50:
            return "HIGH"
        elif score >= 25:
            return "MEDIUM"
        return "LOW"