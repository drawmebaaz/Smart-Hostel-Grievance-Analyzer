#!/usr/bin/env python3
"""
Urgency Rules - Single source of truth
Day 5.2
"""

URGENCY_SCORES = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4,
}

def get_urgency_score(level: str) -> int:
    """Convert urgency label to numeric score"""
    return URGENCY_SCORES.get(level.upper(), 1)

def get_urgency_label(score: int) -> str:
    """Convert numeric score to label"""
    reverse = {v: k for k, v in URGENCY_SCORES.items()}
    return reverse.get(score, "LOW")

def get_max_urgency(levels: list) -> str:
    """Return highest urgency from list"""
    if not levels:
        return "LOW"
    
    scores = [get_urgency_score(level) for level in levels]
    max_score = max(scores)
    return get_urgency_label(max_score)