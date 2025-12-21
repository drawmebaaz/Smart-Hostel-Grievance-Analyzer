#!/usr/bin/env python3
"""
System Constants - Day 6.5
Centralized configuration for tunable parameters
"""

# ==================== DUPLICATE DETECTION ====================

# Similarity threshold for duplicate detection
DUPLICATE_SIMILARITY_THRESHOLD = 0.88

# ==================== SESSION MANAGEMENT ====================

# Session time-to-live (seconds)
SESSION_TTL_SECONDS = 30 * 60  # 30 minutes

# Maximum complaints per session
MAX_SESSION_COMPLAINTS = 10

# Session cleanup interval (seconds)
SESSION_CLEANUP_INTERVAL = 5 * 60  # 5 minutes

# Maximum session entries to keep (memory management)
MAX_SESSION_ENTRIES = 20

# ==================== HEURISTICS ====================

# Minimum complaints before noise detection
MIN_COMPLAINTS_FOR_NOISE = 4

# Maximum average time between complaints for noise (seconds)
MAX_AVG_TIME_DELTA_SEC = 30

# Minimum average similarity for noise detection
MIN_AVG_SIMILARITY = 0.85

# Enable/disable heuristic evaluation
ENABLE_HEURISTICS = True

# Heuristic time window for analysis (minutes)
HEURISTIC_TIME_WINDOW_MIN = 30

# ==================== ISSUE MANAGEMENT ====================

# Default issue batch limit
DEFAULT_ISSUE_LIMIT = 50

# Maximum issues to return in single request
MAX_ISSUE_LIMIT = 200

# ==================== LANGUAGE SCOPE ====================

# Language enforcement
ENFORCE_ENGLISH_ONLY = True

# Hinglish normalization (disabled for English scope)
ENABLE_HINGLISH_NORMALIZATION = False

# ==================== URGENCY MAPPING ====================

URGENCY_SCORES = {
    "Low": 1,
    "Medium": 2,
    "High": 3,
    "Critical": 4
}

URGENCY_LABELS = {
    1: "Low",
    2: "Medium",
    3: "High",
    4: "Critical"
}

# ==================== DATABASE ====================

# Default database URL
DEFAULT_DATABASE_URL = "sqlite:///data/hostel_grievance.db"

# ==================== LOGGING ====================

# Log level for production
LOG_LEVEL = "INFO"

# Structured logging enabled
STRUCTURED_LOGGING = True