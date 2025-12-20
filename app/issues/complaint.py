#!/usr/bin/env python3
"""
Complaint Domain Model
Day 5.1 - Immutable atomic complaint
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class Complaint:
    """
    Complaint record.
    One object = one student submission.
    """
    id: str
    text: str
    category: str          # From Day 3 classifier
    urgency: str           # From Day 4 urgency system
    hostel: str
    timestamp: datetime
    embedding: List[float]  # For duplicate detection
    metadata: Dict = field(default_factory=dict)
    
    # Duplicate tracking
    is_duplicate: bool = False
    duplicate_of: Optional[str] = None
    similarity_score: Optional[float] = None

    def to_dict(self) -> Dict:
        """Serialize complaint safely"""
        return {
            "id": self.id,
            "text": self.text[:100] + "..." if len(self.text) > 100 else self.text,
            "category": self.category,
            "urgency": self.urgency,
            "hostel": self.hostel,
            "timestamp": self.timestamp.isoformat(),
            "is_duplicate": self.is_duplicate,
            "duplicate_of": self.duplicate_of,
            "similarity_score": round(self.similarity_score, 4) if self.similarity_score else None,
            "embedding_length": len(self.embedding) if self.embedding else 0,
            "metadata": self.metadata
        }