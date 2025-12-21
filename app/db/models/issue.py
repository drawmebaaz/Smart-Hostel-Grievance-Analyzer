#!/usr/bin/env python3
"""
Issue Database Model
Day 6.1 - Persistent issue storage
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Enum as SQLEnum
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
    """
    __tablename__ = "issues"
    
    # Primary key
    id = Column(String, primary_key=True, index=True)  # ISSUE-bh_3-water-abc123
    
    # Core attributes
    hostel = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False, index=True)
    status = Column(SQLEnum(IssueStatus), nullable=False, default=IssueStatus.OPEN, index=True)
    
    # Urgency tracking
    urgency_max = Column(String, nullable=False, default="Low")
    urgency_avg = Column(Float, nullable=False, default=1.0)
    
    # Statistics
    complaint_count = Column(Integer, nullable=False, default=0)
    unique_complaint_count = Column(Integer, nullable=False, default=0)
    duplicate_count = Column(Integer, nullable=False, default=0)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_updated = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    
    # Relationships
    complaints = relationship("ComplaintModel", back_populates="issue", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Issue {self.id} ({self.hostel}/{self.category}) - {self.status}>"
    
    def to_dict(self, include_complaints=False, summary=False):
        """Convert to dictionary representation"""
        if summary:
            return {
                "issue_id": self.id,
                "category": self.category,
                "hostel": self.hostel,
                "status": self.status.value,
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
            "status": self.status.value,
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