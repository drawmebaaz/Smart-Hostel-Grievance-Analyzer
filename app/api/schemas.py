#!/usr/bin/env python3
"""
Pydantic schemas for API - Updated for English-only scope
Day 5.5
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
import re


class ComplaintRequest(BaseModel):
    """Schema for submitting a complaint - ENGLISH ONLY"""
    text: str = Field(..., min_length=5, max_length=1000, description="Complaint text (English only)")
    hostel: str = Field(..., min_length=2, max_length=50, description="Hostel name/identifier")
    complaint_id: Optional[str] = Field(None, description="Optional custom complaint ID")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    
    @validator('text')
    def validate_english_text(cls, v):
        """
        Simple English validation.
        Rejects text with heavy Hinglish or non-English patterns.
        """
        # Check for Devanagari characters (Hindi script)
        if re.search(r'[\u0900-\u097F]', v):
            raise ValueError('Text contains Hindi script characters. Please submit complaints in English.')
        
        # Check for common Hinglish patterns that indicate non-English
        hinglish_patterns = [
            r'\bpaani\b', r'\bnahi\b', r'\braha\b', r'\brahi\b', r'\bkyu\b',
            r'\bkya\b', r'\bthik\b', r'\bsab\b', r'\bme\b', r'\btu\b', r'\btum\b',
            r'\bbijli\b', r'\bgaya\b', r'\bgayi\b', r'\bkaam\b', r'\bbahut\b',
            r'\bsubah\b', r'\braat\b', r'\bhostel\s*me\b', r'\broom\s*me\b'
        ]
        
        # If multiple Hinglish patterns found, warn/reject
        hinglish_count = sum(1 for pattern in hinglish_patterns if re.search(pattern, v.lower()))
        if hinglish_count >= 3:
            raise ValueError(
                'Text appears to contain Hinglish/Hindi terms. '
                'For best results, please submit complaints in English. '
                f'Found {hinglish_count} non-English patterns.'
            )
        
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "text": "No water supply in BH-3 since morning",
                "hostel": "BH-3",
                "complaint_id": "optional-custom-id",
                "metadata": {"floor": "2", "room": "201"}
            }
        }


class ComplaintResponse(BaseModel):
    """Schema for complaint response"""
    success: bool
    processing_time_seconds: float
    complaint_id: str
    text_preview: str
    classification: Dict[str, Any]
    issue_aggregation: Dict[str, Any]
    metadata: Dict[str, Any]
    error: Optional[str] = None


class IssueSummary(BaseModel):
    """Schema for issue summary"""
    issue_id: str
    category: str
    hostel: str
    complaint_count: int
    unique_complaint_count: int
    urgency_max: str
    urgency_avg: float
    created_at: str
    last_updated: str
    duplicate_count: int


class IssueDetails(BaseModel):
    """Schema for detailed issue"""
    issue_id: str
    category: str
    hostel: str
    complaint_count: int
    unique_complaint_count: int
    urgency_max: str
    urgency_avg: float
    created_at: str
    last_updated: str
    duplicate_pairs: List[Dict[str, Any]]
    complaints: List[Dict[str, Any]]


class SystemStats(BaseModel):
    """Schema for system statistics"""
    issue_system: Dict[str, Any]
    classification_system: Dict[str, Any]
    embedding_system: Dict[str, Any]
    day_5_complete: bool
    timestamp: str


class BatchComplaintRequest(BaseModel):
    """Schema for batch complaint processing"""
    complaints: List[Dict[str, Any]] = Field(..., min_items=1, max_items=100)
    
    class Config:
        schema_extra = {
            "example": {
                "complaints": [
                    {
                        "text": "No water supply in BH-3 since morning",
                        "hostel": "BH-3",
                        "metadata": {"floor": "2"}
                    },
                    {
                        "text": "Toilet flush not working in room 305",
                        "hostel": "GH-1",
                        "complaint_id": "custom-id-123"
                    }
                ]
            }
        }