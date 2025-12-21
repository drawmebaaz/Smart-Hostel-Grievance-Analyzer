#!/usr/bin/env python3
"""
Enhanced Complaint Database Model
Day 7A.1 & 7A.2 - Integrity constraints + Indexing
"""

from sqlalchemy import (
    Column, String, Text, Float, Boolean, DateTime, 
    ForeignKey, JSON, CheckConstraint, Index
)
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base


class ComplaintModel(Base):
    """
    Complaint = single user submission (immutable)
    
    Day 7A Enhancements:
    - Foreign key constraints with referential integrity
    - Duplicate consistency validation
    - Performance indexes for common queries
    """
    __tablename__ = "complaints"
    
    # Primary key
    id = Column(String, primary_key=True)
    
    # Foreign key to issue (with referential integrity)
    issue_id = Column(
        String,
        ForeignKey("issues.id", ondelete="RESTRICT"),
        nullable=False
    )
    
    # Core content
    text = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    urgency = Column(String, nullable=False)
    hostel = Column(String, nullable=False)
    
    # Duplicate detection
    similarity_score = Column(Float, nullable=True)
    is_duplicate = Column(Boolean, nullable=False, default=False)
    duplicate_of = Column(
        String,
        ForeignKey("complaints.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # Session tracking
    session_id = Column(String, nullable=True)
    
    # Additional metadata
    extra_metadata = Column(JSON, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    issue = relationship("IssueModel", back_populates="complaints")
    
    __table_args__ = (
        # ==================== INTEGRITY CONSTRAINTS (Day 7A.1) ====================
        
        # 1️⃣ Duplicate consistency: if is_duplicate=True, must have duplicate_of
        CheckConstraint(
            "(is_duplicate = 0 AND duplicate_of IS NULL) OR "
            "(is_duplicate = 1 AND duplicate_of IS NOT NULL)",
            name="ck_duplicate_consistency"
        ),
        
        # 2️⃣ Similarity score range validation
        CheckConstraint(
            "similarity_score IS NULL OR (similarity_score >= 0 AND similarity_score <= 1)",
            name="ck_similarity_score_range"
        ),
        
        # ==================== PERFORMANCE INDEXES (Day 7A.2) ====================
        
        # Index for getting all complaints of an issue
        Index("ix_complaint_issue_id", "issue_id"),
        
        # Index for session-based queries
        Index("ix_complaint_session_id", "session_id"),
        
        # Index for time-ordered queries
        Index("ix_complaint_created_at", "created_at"),
        
        # Index for duplicate filtering
        Index("ix_complaint_is_duplicate", "is_duplicate"),
        
        # Index for hostel filtering
        Index("ix_complaint_hostel", "hostel"),
        
        # Index for category filtering
        Index("ix_complaint_category", "category"),
        
        # Composite index for session + time (heuristics optimization)
        Index("ix_complaint_session_time", "session_id", "created_at"),
        
        # Composite index for issue + time
        Index("ix_complaint_issue_time", "issue_id", "created_at"),
    )
    
    def __repr__(self):
        return f"<Complaint {self.id} - {self.category}/{self.urgency}>"
    
    def to_dict(self):
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "issue_id": self.issue_id,
            "text": self.text[:100] + "..." if len(self.text) > 100 else self.text,
            "category": self.category,
            "urgency": self.urgency,
            "hostel": self.hostel,
            "is_duplicate": self.is_duplicate,
            "duplicate_of": self.duplicate_of,
            "similarity_score": round(self.similarity_score, 4) if self.similarity_score else None,
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "metadata": self.extra_metadata
        }