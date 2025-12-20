#!/usr/bin/env python3
"""
Issue ID Utilities
Day 5.2
"""

import hashlib
import re
from typing import Tuple

def normalize_text(text: str) -> str:
    """Normalize text for consistent hashing"""
    # Remove special chars, lowercase, replace spaces
    text = re.sub(r'[^a-zA-Z0-9]', ' ', text.lower())
    text = re.sub(r'\s+', '_', text.strip())
    return text

def generate_issue_key(category: str, hostel: str) -> str:
    """
    Stable key used internally for grouping
    Format: {hostel}::{category}
    """
    normalized_hostel = normalize_text(hostel)
    normalized_category = normalize_text(category)
    return f"{normalized_hostel}::{normalized_category}"

def generate_issue_id(category: str, hostel: str, sequence: int = None) -> str:
    """
    Public-facing issue ID
    Format: ISSUE-{HOSTEL}-{CATEGORY}-{HASH}
    """
    base = f"{hostel}-{category}"
    digest = hashlib.sha1(base.encode()).hexdigest()[:6]
    
    return f"ISSUE-{normalize_text(hostel)}-{normalize_text(category)}-{digest}"

def parse_issue_id(issue_id: str) -> Tuple[str, str, str]:
    """Parse issue ID into components"""
    parts = issue_id.split('-')
    if len(parts) >= 4 and parts[0] == "ISSUE":
        hostel = parts[1]
        category = parts[2]
        hash_part = parts[3]
        return hostel, category, hash_part
    return "", "", ""