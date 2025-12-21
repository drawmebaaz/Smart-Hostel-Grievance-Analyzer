#!/usr/bin/env python3
"""
Session-aware heuristics engine
Day 6.3 - Follow-ups, escalations, noise detection
"""

from typing import Dict, Any, Optional, List
from datetime import datetime

from app.utils.logger import get_logger

logger = get_logger(__name__)

# -------------------------------
# Configurable heuristic constants
# -------------------------------

MIN_COMPLAINTS_FOR_NOISE = 4
MAX_AVG_TIME_DELTA_SEC = 30
MIN_AVG_SIMILARITY = 0.85


# -------------------------------
# Urgency ordering (authoritative)
# -------------------------------

URGENCY_ORDER = {
    "Low": 1,
    "Medium": 2,
    "High": 3,
    "Critical": 4,
}


class HeuristicEngine:
    """
    Stateless heuristic evaluator.
    Reads session + issue facts and emits descriptive signals.
    """

    @staticmethod
    def evaluate(
        *,
        session: Any,
        current_issue_id: str,
        current_urgency: str,
        is_duplicate: bool,
        similarity_score: Optional[float],
        timestamp: datetime,
    ) -> Dict[str, Any]:
        """
        Evaluate session-aware heuristics.

        Returns a dictionary of boolean flags + optional details.
        """

        result = {
            "is_follow_up": False,
            "is_escalation": False,
            "possible_noise": False,
            "details": {},
        }

        # Defensive: empty session
        if not session or not session.entries:
            return result

        previous_entries = session.entries[:-1] if len(session.entries) > 1 else []

        # ----------------------------------
        # 1️⃣ Follow-up detection
        # ----------------------------------

        if len(previous_entries) >= 1 and not is_duplicate:
            # Check if any previous entry has same issue_id
            for entry in previous_entries:
                if entry.issue_id == current_issue_id:
                    result["is_follow_up"] = True
                    logger.debug(f"Follow-up detected for issue {current_issue_id}")
                    break

        # ----------------------------------
        # 2️⃣ Escalation detection
        # ----------------------------------

        # Get previous urgencies for same issue
        previous_urgencies = [
            URGENCY_ORDER.get(e.urgency)
            for e in previous_entries
            if e.issue_id == current_issue_id and e.urgency in URGENCY_ORDER
        ]

        if previous_urgencies:
            prev_max = max(previous_urgencies)
            current_level = URGENCY_ORDER.get(current_urgency)

            if current_level and current_level > prev_max:
                result["is_escalation"] = True
                result["details"]["previous_urgency"] = _urgency_from_value(prev_max)
                result["details"]["current_urgency"] = current_urgency
                logger.info(f"Escalation detected: {_urgency_from_value(prev_max)} → {current_urgency}")

        # ----------------------------------
        # 3️⃣ Possible noise detection
        # ----------------------------------

        total_entries = len(session.entries)
        if total_entries >= MIN_COMPLAINTS_FOR_NOISE:
            # Calculate time deltas
            time_deltas = _time_deltas(session.entries, timestamp)
            avg_time_delta = _average(time_deltas)

            # Calculate similarity scores
            similarities = [
                e.similarity_score
                for e in session.entries
                if e.similarity_score is not None
            ]
            avg_similarity = _average(similarities)

            if (
                avg_time_delta is not None
                and avg_similarity is not None
                and avg_time_delta <= MAX_AVG_TIME_DELTA_SEC
                and avg_similarity >= MIN_AVG_SIMILARITY
            ):
                result["possible_noise"] = True
                result["details"]["avg_time_between_complaints_sec"] = round(avg_time_delta, 2)
                result["details"]["avg_similarity"] = round(avg_similarity, 3)
                logger.warning(f"Possible noise detected in session {session.session_id}")

        return result


# -------------------------------
# Helper functions (pure)
# -------------------------------

def _average(values):
    """Calculate average of list"""
    if not values:
        return None
    return sum(values) / len(values)


def _time_deltas(entries, current_time):
    """Calculate time deltas between entries"""
    deltas = []
    timestamps = [e.timestamp for e in entries if hasattr(e, 'timestamp')]
    
    if not timestamps:
        return []
    
    # Add current time
    current_ts = current_time.timestamp()
    all_timestamps = timestamps + [current_ts]
    
    # Calculate deltas between consecutive timestamps
    for i in range(1, len(all_timestamps)):
        delta = all_timestamps[i] - all_timestamps[i-1]
        if delta >= 0:
            deltas.append(delta)
    
    return deltas


def _urgency_from_value(value: int) -> Optional[str]:
    """Convert urgency score to label"""
    for k, v in URGENCY_ORDER.items():
        if v == value:
            return k
    return None