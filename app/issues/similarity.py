#!/usr/bin/env python3
"""
Vector similarity utilities
Day 5.3.1
"""

import numpy as np
from typing import List


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Compute cosine similarity between two vectors"""
    if not a or not b:
        return 0.0
    
    a_np = np.array(a)
    b_np = np.array(b)
    
    # Handle zero vectors
    norm_a = np.linalg.norm(a_np)
    norm_b = np.linalg.norm(b_np)
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
    
    similarity = np.dot(a_np, b_np) / (norm_a * norm_b)
    
    # Clamp to [-1, 1] due to floating point errors
    return float(max(-1.0, min(1.0, similarity)))