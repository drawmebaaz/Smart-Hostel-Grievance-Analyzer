#!/usr/bin/env python3
"""
Domain Validators
Day 5.2
"""

from typing import List
import numpy as np

def validate_category(category: str, allowed_categories: List[str] = None) -> None:
    """Validate category"""
    if not category or not isinstance(category, str):
        raise ValueError("Invalid category: must be non-empty string")
    
    if allowed_categories and category not in allowed_categories:
        raise ValueError(f"Category '{category}' not in allowed list")

def validate_hostel(hostel: str) -> None:
    """Validate hostel"""
    if not hostel or not isinstance(hostel, str):
        raise ValueError("Invalid hostel: must be non-empty string")
    
    if len(hostel.strip()) < 2:
        raise ValueError("Hostel name too short")

def validate_complaint_id(cid: str) -> None:
    """Validate complaint ID"""
    if not cid or not isinstance(cid, str):
        raise ValueError("Invalid complaint ID: must be non-empty string")
    
    if len(cid) < 3:
        raise ValueError("Complaint ID too short")

def validate_embedding(embedding: List[float]) -> None:
    """Validate embedding vector"""
    if not embedding:
        raise ValueError("Embedding cannot be empty")
    
    if not isinstance(embedding, list):
        raise ValueError("Embedding must be a list")
    
    if not all(isinstance(x, (int, float)) for x in embedding):
        raise ValueError("Embedding must contain only numbers")
    
    # Check for zero vector
    if np.allclose(embedding, 0):
        raise ValueError("Embedding appears to be a zero vector")