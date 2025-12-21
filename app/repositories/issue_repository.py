#!/usr/bin/env python3
"""
Enhanced Issue Repository
Day 7A.3 - Row-level locking for concurrency safety
"""

from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from app.db.models.issue import IssueModel, IssueStatus
from app.utils.logger import get_logger

logger = get_logger(__name__)


class IssueRepository:
    """
    Repository for issue database operations
    
    Day 7A.3 Enhancements:
    - Row-level locking (for_update)
    - Integrity error handling
    - Query optimization with eager loading
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, issue_data: dict) -> IssueModel:
        """
        Create new issue with integrity error handling
        
        Day 7A.3: Handles race conditions where two threads
        try to create same (hostel, category) issue
        """
        try:
            issue = IssueModel(**issue_data)
            self.db.add(issue)
            self.db.flush()
            logger.info(f"Issue created: {issue.id}")
            return issue
        except IntegrityError as e:
            self.db.rollback()
            logger.warning(f"Issue creation failed (likely duplicate): {str(e)}")
            # Re-fetch existing issue
            existing = self.get_by_hostel_category(
                issue_data["hostel"],
                issue_data["category"],
                for_update=False
            )
            if existing:
                logger.info(f"Returning existing issue: {existing.id}")
                return existing
            raise
    
    def get_by_id(self, issue_id: str, for_update: bool = False) -> Optional[IssueModel]:
        """
        Get issue by ID
        
        Args:
            issue_id: Issue ID
            for_update: If True, locks row for update (Day 7A.3)
        """
        query = self.db.query(IssueModel).filter(IssueModel.id == issue_id)
        
        if for_update:
            query = query.with_for_update()
        
        return query.first()
    
    def get_by_hostel_category(
        self, 
        hostel: str, 
        category: str,
        for_update: bool = False
    ) -> Optional[IssueModel]:
        """
        Get issue by hostel and category
        
        Args:
            hostel: Hostel name
            category: Category name
            for_update: If True, locks row for update (Day 7A.3)
        """
        query = self.db.query(IssueModel).filter(
            IssueModel.hostel == hostel,
            IssueModel.category == category
        )
        
        if for_update:
            # Day 7A.3: Row-level lock prevents concurrent counter updates
            query = query.with_for_update()
        
        return query.first()
    
    def get_all(
        self,
        status: Optional[IssueStatus] = None,
        hostel: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 100,
        eager_load_complaints: bool = False
    ) -> List[IssueModel]:
        """
        Get issues with optional filters
        
        Day 7A.2: Query optimization with indexes
        """
        query = self.db.query(IssueModel)
        
        # Day 7A.2: Uses ix_issue_status index
        if status:
            query = query.filter(IssueModel.status == status.value)
        
        # Day 7A.2: Uses ix_issue_hostel_category index
        if hostel:
            query = query.filter(IssueModel.hostel == hostel)
        if category:
            query = query.filter(IssueModel.category == category)
        
        # Day 7A.2: Uses ix_issue_last_updated index
        query = query.order_by(IssueModel.last_updated.desc())
        
        # Day 7A.2: Eager load to avoid N+1 queries
        if eager_load_complaints:
            query = query.options(joinedload(IssueModel.complaints))
        
        return query.limit(limit).all()
    
    def update(self, issue: IssueModel) -> IssueModel:
        """Update issue (timestamp auto-updated)"""
        issue.last_updated = datetime.utcnow()
        self.db.flush()
        logger.debug(f"Issue updated: {issue.id}")
        return issue
    
    def update_status(
        self, 
        issue_id: str, 
        status: IssueStatus
    ) -> Optional[IssueModel]:
        """
        Update issue status (admin action)
        
        Day 7A.3: Uses row locking to prevent race conditions
        """
        # Lock the row during status update
        issue = self.get_by_id(issue_id, for_update=True)
        if not issue:
            return None
        
        issue.status = status.value
        issue.last_updated = datetime.utcnow()
        
        if status == IssueStatus.RESOLVED:
            issue.resolved_at = datetime.utcnow()
        elif status == IssueStatus.REOPENED:
            issue.resolved_at = None
        
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
        """
        Increment issue complaint counts
        
        Day 7A.3: Should be called within transaction with row lock
        """
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
        """
        Get overall issue statistics
        
        Day 7A.2: Optimized with status index
        """
        total_issues = self.db.query(IssueModel).count()
        
        status_counts = {}
        for status in IssueStatus:
            # Day 7A.2: Uses ix_issue_status index
            count = self.db.query(IssueModel).filter(
                IssueModel.status == status.value
            ).count()
            status_counts[status.value] = count
        
        return {
            "total_issues": total_issues,
            "status_distribution": status_counts
        }