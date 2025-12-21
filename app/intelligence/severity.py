#!/usr/bin/env python3
"""
Issue Severity Engine
Day 8.2 - Determines issue severity (SEV-1 to SEV-4)
"""

from typing import Dict


class IssueSeverityEngine:
    """
    Computes issue severity based on:
    1. Base urgency mapping
    2. Volume escalation
    3. Category minimums
    
    SEV-1: Critical (most severe)
    SEV-2: Major
    SEV-3: Moderate
    SEV-4: Minor
    """

    # Base severity from urgency
    URGENCY_BASE = {
        "Low": 4,
        "Medium": 3,
        "High": 2,
        "Critical": 1
    }

    # Category minimum severity (some issues are never minor)
    CATEGORY_MIN = {
        "Electricity": 2,
        "Water": 2,
        "Internet": 3,
        "Safety": 1,
        "Hygiene": 3
    }

    @classmethod
    def compute(cls, issue) -> Dict:
        """
        Compute severity for an issue.
        
        Args:
            issue: IssueModel instance
            
        Returns:
            Dict with severity label and numeric value
        """
        # Start with base severity from urgency
        severity = cls.URGENCY_BASE.get(issue.urgency_max, 4)

        # Volume escalation (more complaints = more severe)
        if issue.unique_complaint_count >= 8:
            severity -= 2  # Escalate by 2 levels
        elif issue.unique_complaint_count >= 4:
            severity -= 1  # Escalate by 1 level

        # Apply category minimum (some categories are always severe)
        min_sev = cls.CATEGORY_MIN.get(issue.category)
        if min_sev:
            severity = min(severity, min_sev)

        # Clamp between SEV-1 and SEV-4
        severity = max(1, min(4, severity))

        return {
            "severity": f"SEV-{severity}",
            "numeric": severity,
            "description": cls._description(severity)
        }
    
    @staticmethod
    def _description(severity: int) -> str:
        """Get severity description"""
        descriptions = {
            1: "Critical - Immediate action required",
            2: "Major - Significant impact",
            3: "Moderate - Noticeable disruption",
            4: "Minor - Low impact"
        }
        return descriptions.get(severity, "Unknown")