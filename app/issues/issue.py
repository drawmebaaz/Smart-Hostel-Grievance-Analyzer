#!/usr/bin/env python3
"""
Issue Aggregate
Day 5.1 - Groups related complaints
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import numpy as np

from app.issues.complaint import Complaint
from app.issues.similarity import cosine_similarity
from app.issues.urgency_rules import get_urgency_score, get_urgency_label


@dataclass
class Issue:
    """
    Issue = cluster of related complaints
    Boundary: category + hostel
    """
    issue_id: str
    category: str
    hostel: str
    
    complaints: List[Complaint] = field(default_factory=list)
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    # Derived fields
    complaint_count: int = 0
    unique_complaint_count: int = 0
    urgency_max: str = "LOW"
    urgency_avg: float = 1.0
    
    # Duplicate detection threshold
    duplicate_threshold: float = 0.88  # Changed from 0.82 to 0.75
    
    def __post_init__(self):
        """Initialize after dataclass creation"""
        self.complaint_count = len(self.complaints)
        self._recalculate_derived_fields()
    
    def add_complaint(self, complaint: Complaint) -> Tuple[bool, Optional[Complaint], float]:
        """
        Append complaint and update aggregates.
        Returns: (is_new_complaint, duplicate_of, similarity_score)
        """
        # Check for duplicates
        duplicate_of, similarity_score = self._find_duplicate(complaint)
        
        if duplicate_of:
            complaint.is_duplicate = True
            complaint.duplicate_of = duplicate_of.id
            complaint.similarity_score = similarity_score
            is_new = False
        else:
            complaint.is_duplicate = False
            complaint.duplicate_of = None
            complaint.similarity_score = similarity_score  # Store score even if not duplicate
            is_new = True
        
        # Add to list
        self.complaints.append(complaint)
        
        # Update timestamps
        self.last_updated = datetime.utcnow()
        if self.complaint_count == 0:
            self.created_at = complaint.timestamp
        
        # Recalculate derived fields
        self._recalculate_derived_fields()
        
        return is_new, duplicate_of, similarity_score
    
    def _find_duplicate(self, new_complaint: Complaint) -> Tuple[Optional[Complaint], float]:
        """Find if complaint is duplicate of existing one. Returns (best_match, similarity_score)"""
        if not self.complaints or not new_complaint.embedding:
            return None, 0.0
        
        # HARD RULE: Must be same hostel
        if new_complaint.hostel != self.hostel:
            return None, 0.0  # Different hostel → no duplicate possible
        
        # HARD RULE: Must be same category (already enforced by IssueManager grouping)
        if new_complaint.category != self.category:
            return None, 0.0  # Different category → no duplicate possible
        
        best_match = None
        best_score = 0.0
        
        for existing in self.complaints:
            if not existing.embedding:
                continue
            
            # Additional safety check (should already be same hostel/category)
            if existing.hostel != new_complaint.hostel or existing.category != new_complaint.category:
                continue  # Skip if somehow different hostel/category
            
            score = cosine_similarity(new_complaint.embedding, existing.embedding)
            
            if score > best_score:
                best_score = score
                best_match = existing
        
        if best_score >= self.duplicate_threshold:
            return best_match, best_score
        
        return None, best_score  # Return score even if not duplicate
        
    def _recalculate_derived_fields(self):
        """Update all derived fields"""
        self.complaint_count = len(self.complaints)
        self.unique_complaint_count = len([c for c in self.complaints if not c.is_duplicate])
        
        if not self.complaints:
            self.urgency_max = "LOW"
            self.urgency_avg = 1.0
            return
        
        # Calculate urgency statistics
        urgency_scores = [get_urgency_score(c.urgency) for c in self.complaints]
        max_score = max(urgency_scores)
        self.urgency_max = get_urgency_label(max_score)
        self.urgency_avg = sum(urgency_scores) / len(urgency_scores)
    
    def get_complaint_ids(self) -> List[str]:
        """Get all complaint IDs in this issue"""
        return [c.id for c in self.complaints]
    
    def get_unique_complaints(self) -> List[Complaint]:
        """Get only unique (non-duplicate) complaints"""
        return [c for c in self.complaints if not c.is_duplicate]
    
    def get_duplicate_pairs(self) -> List[Dict]:
        """Get all duplicate relationships"""
        pairs = []
        for complaint in self.complaints:
            if complaint.is_duplicate and complaint.duplicate_of and complaint.similarity_score:
                pairs.append({
                    "duplicate_id": complaint.id,
                    "original_id": complaint.duplicate_of,
                    "similarity": round(complaint.similarity_score, 4)
                })
        return pairs
    
    def get_similarity_statistics(self) -> Dict:
        """Get statistics about similarity scores"""
        scores = []
        for complaint in self.complaints:
            if complaint.similarity_score is not None:
                scores.append(complaint.similarity_score)
        
        if not scores:
            return {
                "average_similarity": 0.0,
                "min_similarity": 0.0,
                "max_similarity": 0.0,
                "total_scored": 0
            }
        
        return {
            "average_similarity": round(sum(scores) / len(scores), 4),
            "min_similarity": round(min(scores), 4),
            "max_similarity": round(max(scores), 4),
            "total_scored": len(scores)
        }
    
    def to_dict(self, include_complaints: bool = True, summary: bool = False) -> Dict:
        """
        Serialize issue.
        
        Args:
            include_complaints: Include full complaint details
            summary: Return summary only (for lists)
        """
        if summary:
            return {
                "issue_id": self.issue_id,
                "category": self.category,
                "hostel": self.hostel,
                "complaint_count": self.complaint_count,
                "unique_complaint_count": self.unique_complaint_count,
                "urgency_max": self.urgency_max,
                "urgency_avg": round(self.urgency_avg, 2),
                "created_at": self.created_at.isoformat(),
                "last_updated": self.last_updated.isoformat(),
                "duplicate_count": self.complaint_count - self.unique_complaint_count,
                "duplicate_threshold": self.duplicate_threshold
            }
        
        data = {
            "issue_id": self.issue_id,
            "category": self.category,
            "hostel": self.hostel,
            "complaint_count": self.complaint_count,
            "unique_complaint_count": self.unique_complaint_count,
            "urgency_max": self.urgency_max,
            "urgency_avg": round(self.urgency_avg, 2),
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "duplicate_pairs": self.get_duplicate_pairs(),
            "similarity_stats": self.get_similarity_statistics(),
            "duplicate_threshold": self.duplicate_threshold
        }
        
        if include_complaints:
            data["complaints"] = [c.to_dict() for c in self.complaints]
        
        return data