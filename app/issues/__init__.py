"""
Issue Management Module
Day 5 - Issue Aggregation System
"""

from app.issues.complaint import Complaint
from app.issues.issue import Issue
from app.issues.issue_manager import IssueManager, get_issue_manager

__all__ = [
    "Complaint",
    "Issue", 
    "IssueManager",
    "get_issue_manager"
]