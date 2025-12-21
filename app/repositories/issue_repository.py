#!/usr/bin/env python3
"""
Issue Repository
Day 6.2 - Database operations for issues
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.models.issue import IssueModel, IssueStatus
from app.utils.logger import get_logger

logger = get_logger(__name__)


class IssueRepository:
    """Repository for issue database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, issue_data: dict) -> IssueModel:
        """Create new issue"""
        issue = IssueModel(**issue_data)
        self.db.add(issue)
        self.db.flush()
        logger.info(f"Issue created: {issue.id}")
        return issue
    
    def get_by_id(self, issue_id: str) -> Optional[IssueModel]:
        """Get issue by ID"""
        return self.db.query(IssueModel).filter(IssueModel.id == issue_id).first()
    
    def get_by_hostel_category(self, hostel: str, category: str) -> Optional[IssueModel]:
        """Get issue by hostel and category"""
        return self.db.query(IssueModel).filter(
            IssueModel.hostel == hostel,
            IssueModel.category == category
        ).first()
    
    def get_all(
        self,
        status: Optional[IssueStatus] = None,
        hostel: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 100
    ) -> List[IssueModel]:
        """Get issues with optional filters"""
        query = self.db.query(IssueModel)
        
        if status:
            query = query.filter(IssueModel.status == status)
        if hostel:
            query = query.filter(IssueModel.hostel == hostel)
        if category:
            query = query.filter(IssueModel.category == category)
        
        return query.order_by(IssueModel.last_updated.desc()).limit(limit).all()
    
    def update(self, issue: IssueModel) -> IssueModel:
        """Update issue"""
        issue.last_updated = datetime.utcnow()
        self.db.flush()
        logger.debug(f"Issue updated: {issue.id}")
        return issue
    
    def update_status(self, issue_id: str, status: IssueStatus) -> Optional[IssueModel]:
        """Update issue status"""
        issue = self.get_by_id(issue_id)
        if not issue:
            return None
        
        issue.status = status
        issue.last_updated = datetime.utcnow()
        
        if status == IssueStatus.RESOLVED:
            issue.resolved_at = datetime.utcnow()
        
        self.db.flush()
        logger.info(f"Issue {issue_id} status changed to {status.value}")
        return issue
    
    def increment_counts(
        self,
        issue: IssueModel,
        is_duplicate: bool,
        urgency: str,
        urgency_avg: float
    ):
        """Increment issue complaint counts"""
        issue.complaint_count += 1
        
        if not is_duplicate:
            issue.unique_complaint_count += 1
        else:
            issue.duplicate_count += 1
        
        issue.urgency_max = urgency
        issue.urgency_avg = urgency_avg
        issue.last_updated = datetime.utcnow()
        
        self.db.flush()
    
    def get_statistics(self) -> dict:
        """Get overall issue statistics"""
        total_issues = self.db.query(IssueModel).count()
        
        status_counts = {}
        for status in IssueStatus:
            count = self.db.query(IssueModel).filter(IssueModel.status == status).count()
            status_counts[status.value] = count
        
        return {
            "total_issues": total_issues,
            "status_distribution": status_counts
        }