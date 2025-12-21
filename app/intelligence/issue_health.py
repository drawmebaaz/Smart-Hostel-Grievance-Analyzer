#!/usr/bin/env python3
"""
Issue Health Scorer
Day 8.1 - Computes health score (0-100) for issues
"""

from datetime import datetime
from typing import Dict


class IssueHealthScorer:
    """
    Computes health score for an issue based on:
    1. Urgency (0-40 points)
    2. Volume (0-25 points)
    3. Time decay (0-20 points)
    4. Noise penalty (-15 to 0 points)
    
    Final score: 0-100 (higher = worse health)
    """

    URGENCY_MAP = {
        "Low": 10,
        "Medium": 20,
        "High": 30,
        "Critical": 40
    }

    @classmethod
    def compute(cls, issue) -> Dict:
        """
        Compute health score for an issue.
        
        Args:
            issue: IssueModel instance
            
        Returns:
            Dict with score, label, and component breakdown
        """
        now = datetime.utcnow()

        # 1. Urgency score (0-40)
        urgency_score = cls.URGENCY_MAP.get(issue.urgency_max, 10)

        # 2. Volume score (0-25)
        # More complaints = worse health
        volume_score = min(25, issue.unique_complaint_count * 5)

        # 3. Time score (0-20)
        # Older unresolved issues = worse health
        if issue.status == "RESOLVED":
            time_score = 0
        else:
            hours_open = (now - issue.created_at).total_seconds() / 3600

            if hours_open < 6:
                time_score = 5
            elif hours_open < 24:
                time_score = 10
            elif hours_open < 72:
                time_score = 15
            else:
                time_score = 20

        # 4. Noise penalty (-15 to 0)
        # High duplicate ratio = less severe (spam detection)
        if issue.complaint_count == 0:
            noise_penalty = 0
        else:
            duplicate_ratio = issue.duplicate_count / issue.complaint_count

            if duplicate_ratio > 0.6:
                noise_penalty = -15
            elif duplicate_ratio > 0.4:
                noise_penalty = -10
            elif duplicate_ratio > 0.2:
                noise_penalty = -5
            else:
                noise_penalty = 0

        # Final score (0-100)
        raw_score = (
            urgency_score
            + volume_score
            + time_score
            + noise_penalty
        )

        score = max(0, min(100, raw_score))

        return {
            "score": score,
            "label": cls._label(score),
            "components": {
                "urgency": urgency_score,
                "volume": volume_score,
                "time": time_score,
                "noise_penalty": noise_penalty
            }
        }

    @staticmethod
    def _label(score: int) -> str:
        """Convert numeric score to health label"""
        if score <= 20:
            return "HEALTHY"
        elif score <= 40:
            return "MONITOR"
        elif score <= 60:
            return "WARNING"
        elif score <= 80:
            return "CRITICAL"
        return "EMERGENCY"