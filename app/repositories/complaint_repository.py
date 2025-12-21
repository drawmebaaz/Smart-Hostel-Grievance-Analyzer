#!/usr/bin/env python3
"""
Complaint Repository
Day 6.2 - Database operations for complaints
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.db.models.complaint import ComplaintModel
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ComplaintRepository:
    """Repository for complaint database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, complaint_data: dict) -> ComplaintModel:
        """Create new complaint"""
        complaint = ComplaintModel(**complaint_data)
        self.db.add(complaint)
        self.db.flush()
        logger.info(f"Complaint created: {complaint.id}")
        return complaint
    
    def get_by_id(self, complaint_id: str) -> Optional[ComplaintModel]:
        """Get complaint by ID"""
        return self.db.query(ComplaintModel).filter(
            ComplaintModel.id == complaint_id
        ).first()
    
    def get_by_issue(self, issue_id: str, limit: int = 100) -> List[ComplaintModel]:
        """Get all complaints for an issue"""
        return self.db.query(ComplaintModel).filter(
            ComplaintModel.issue_id == issue_id
        ).order_by(ComplaintModel.created_at.desc()).limit(limit).all()
    
    def get_by_session(self, session_id: str) -> List[ComplaintModel]:
        """Get all complaints for a session"""
        return self.db.query(ComplaintModel).filter(
            ComplaintModel.session_id == session_id
        ).order_by(ComplaintModel.created_at).all()
    
    def get_recent(self, hours: int = 24, limit: int = 100) -> List[ComplaintModel]:
        """Get recent complaints"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return self.db.query(ComplaintModel).filter(
            ComplaintModel.created_at >= cutoff
        ).order_by(ComplaintModel.created_at.desc()).limit(limit).all()
    
    def count_by_issue(self, issue_id: str) -> int:
        """Count complaints for an issue"""
        return self.db.query(ComplaintModel).filter(
            ComplaintModel.issue_id == issue_id
        ).count()
    
    def count_duplicates_by_issue(self, issue_id: str) -> int:
        """Count duplicate complaints for an issue"""
        return self.db.query(ComplaintModel).filter(
            ComplaintModel.issue_id == issue_id,
            ComplaintModel.is_duplicate == True
        ).count()
    
    def get_statistics(self) -> dict:
        """Get overall complaint statistics"""
        total_complaints = self.db.query(ComplaintModel).count()
        duplicates = self.db.query(ComplaintModel).filter(
            ComplaintModel.is_duplicate == True
        ).count()
        
        return {
            "total_complaints": total_complaints,
            "duplicate_complaints": duplicates,
            "unique_complaints": total_complaints - duplicates,
            "duplicate_rate": round(duplicates / total_complaints, 4) if total_complaints > 0 else 0
        }