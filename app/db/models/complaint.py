#!/usr/bin/env python3
"""
Complaint Database Model
Day 6.1 - Persistent complaint storage
"""

from sqlalchemy import Column, String, Text, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base


class ComplaintModel(Base):
    """
    Complaint = single user submission (immutable)
    """
    __tablename__ = "complaints"
    
    # Primary key
    id = Column(String, primary_key=True, index=True)  # COMP-abc123
    
    # Foreign key to issue
    issue_id = Column(String, ForeignKey("issues.id"), nullable=False, index=True)
    
    # Core content
    text = Column(Text, nullable=False)
    category = Column(String, nullable=False, index=True)
    urgency = Column(String, nullable=False, index=True)
    hostel = Column(String, nullable=False, index=True)
    
    # Duplicate detection
    similarity_score = Column(Float, nullable=True)
    is_duplicate = Column(Boolean, nullable=False, default=False, index=True)
    duplicate_of = Column(String, nullable=True)
    
    # Session tracking (Day 6.2)
    session_id = Column(String, nullable=True, index=True)
    
    # Additional metadata (renamed to avoid SQLAlchemy conflict)
    extra_metadata = Column(JSON, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Relationships
    issue = relationship("IssueModel", back_populates="complaints")
    
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