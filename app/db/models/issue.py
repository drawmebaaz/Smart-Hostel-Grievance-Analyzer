#!/usr/bin/env python3
"""
Enhanced Issue Database Model
Day 7A.1 & 7A.2 - Integrity constraints + Indexing
"""

from sqlalchemy import (
    Column, String, Integer, Float, DateTime, 
    UniqueConstraint, CheckConstraint, Index
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.base import Base


class IssueStatus(str, enum.Enum):
    """Issue lifecycle states"""
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    REOPENED = "REOPENED"


class IssueModel(Base):
    """
    Issue = cluster of related complaints
    Boundary: category + hostel
    
    Day 7A Enhancements:
    - Unique constraint on (hostel, category)
    - Status validation via CHECK constraint
    - Counter sanity checks
    - Performance indexes
    """
    __tablename__ = "issues"
    
    # Primary key
    id = Column(String, primary_key=True, index=True)
    
    # Core attributes
    hostel = Column(String, nullable=False)
    category = Column(String, nullable=False)
    status = Column(String, nullable=False, default="OPEN")
    
    # Urgency tracking
    urgency_max = Column(String, nullable=False, default="Low")
    urgency_avg = Column(Float, nullable=False, default=1.0)
    
    # Statistics
    complaint_count = Column(Integer, nullable=False, default=0)
    unique_complaint_count = Column(Integer, nullable=False, default=0)
    duplicate_count = Column(Integer, nullable=False, default=0)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    last_updated = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    
    # Relationships
    complaints = relationship(
        "ComplaintModel", 
        back_populates="issue", 
        cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        # ==================== INTEGRITY CONSTRAINTS (Day 7A.1) ====================
        
        # 1️⃣ One issue per (hostel, category)
        UniqueConstraint(
            "hostel", "category",
            name="uq_issue_hostel_category"
        ),
        
        # 2️⃣ Valid status only
        CheckConstraint(
            "status IN ('OPEN', 'IN_PROGRESS', 'RESOLVED', 'REOPENED')",
            name="ck_issue_status_valid"
        ),
        
        # 3️⃣ Counts sanity
        CheckConstraint(
            "complaint_count >= unique_complaint_count",
            name="ck_issue_counts_valid"
        ),
        
        CheckConstraint(
            "complaint_count >= duplicate_count",
            name="ck_issue_duplicate_count_valid"
        ),
        
        CheckConstraint(
            "complaint_count = unique_complaint_count + duplicate_count",
            name="ck_issue_counts_sum"
        ),
        
        # ==================== PERFORMANCE INDEXES (Day 7A.2) ====================
        
        # Index for status filtering (admin dashboards)
        Index("ix_issue_status", "status"),
        
        # Index for recent activity sorting
        Index("ix_issue_last_updated", "last_updated"),
        
        # Composite index for hostel + category lookups
        Index("ix_issue_hostel_category", "hostel", "category"),
        
        # Index for resolved issues filtering
        Index("ix_issue_resolved_at", "resolved_at"),
    )
    
    def __repr__(self):
        return f"<Issue {self.id} ({self.hostel}/{self.category}) - {self.status}>"
    
    def to_dict(self, include_complaints=False, summary=False):
        """Convert to dictionary representation"""
        if summary:
            return {
                "issue_id": self.id,
                "category": self.category,
                "hostel": self.hostel,
                "status": self.status,
                "complaint_count": self.complaint_count,
                "unique_complaint_count": self.unique_complaint_count,
                "urgency_max": self.urgency_max,
                "urgency_avg": round(self.urgency_avg, 2),
                "created_at": self.created_at.isoformat(),
                "last_updated": self.last_updated.isoformat(),
                "duplicate_count": self.duplicate_count
            }
        
        data = {
            "issue_id": self.id,
            "category": self.category,
            "hostel": self.hostel,
            "status": self.status,
            "complaint_count": self.complaint_count,
            "unique_complaint_count": self.unique_complaint_count,
            "urgency_max": self.urgency_max,
            "urgency_avg": round(self.urgency_avg, 2),
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "duplicate_count": self.duplicate_count
        }
        
        if include_complaints:
            data["complaints"] = [c.to_dict() for c in self.complaints]
        
        return data