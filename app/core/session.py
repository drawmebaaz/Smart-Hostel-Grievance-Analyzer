#!/usr/bin/env python3
"""
Session management for complaint lifecycle tracking.

Day 6.2:
- Lightweight session tracking (no auth)
- In-memory store (replaceable later with Redis/DB)
- Complaint-level traceability
"""

import uuid
import time
from typing import Dict, Optional, List
from dataclasses import dataclass, field

from app.utils.logger import get_logger

logger = get_logger(__name__)

# -------------------------
# Session Configuration
# -------------------------

SESSION_TTL_SECONDS = 30 * 60        # 30 minutes
MAX_COMPLAINTS_PER_SESSION = 10
SESSION_CLEANUP_INTERVAL = 300       # 5 minutes


# -------------------------
# Session Entry Model
# -------------------------

@dataclass
class SessionEntry:
    """Single complaint entry in session history"""
    complaint_id: str
    issue_id: str
    category: str
    urgency: str
    similarity_score: Optional[float]
    is_duplicate: bool
    timestamp: float


# -------------------------
# Session Model
# -------------------------

@dataclass
class Session:
    session_id: str
    created_at: float
    last_active_at: float
    entries: List[SessionEntry] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)

    def touch(self):
        """Update last active timestamp"""
        self.last_active_at = time.time()

    def is_expired(self) -> bool:
        """Check if session has expired"""
        return (time.time() - self.last_active_at) > SESSION_TTL_SECONDS

    def can_submit_complaint(self) -> bool:
        """Check if session can accept more complaints"""
        return len(self.entries) < MAX_COMPLAINTS_PER_SESSION
    
    def add_entry(self, entry: SessionEntry) -> bool:
        """
        Add complaint entry to session.
        Enforces idempotency - won't add duplicate complaint_id.
        """
        # Check for duplicate complaint_id (idempotency)
        if any(e.complaint_id == entry.complaint_id for e in self.entries):
            logger.warning(f"Complaint {entry.complaint_id} already in session {self.session_id}")
            return False
        
        # Add entry
        self.entries.append(entry)
        self.touch()
        
        # Enforce max size
        if len(self.entries) > MAX_COMPLAINTS_PER_SESSION:
            self.entries.pop(0)  # Remove oldest
            
        return True
    
    def get_issue_history(self, issue_id: str) -> List[SessionEntry]:
        """Get all entries for a specific issue"""
        return [e for e in self.entries if e.issue_id == issue_id]
    
    def get_max_urgency_for_issue(self, issue_id: str) -> Optional[str]:
        """Get maximum urgency level for an issue in this session"""
        from app.issues.urgency_rules import get_urgency_score
        
        entries = self.get_issue_history(issue_id)
        if not entries:
            return None
        
        urgencies = [get_urgency_score(e.urgency) for e in entries]
        max_score = max(urgencies)
        
        # Convert back to label
        urgency_map = {1: "Low", 2: "Medium", 3: "High", 4: "Critical"}
        return urgency_map.get(max_score, "Low")


# -------------------------
# Session Manager
# -------------------------

class SessionManager:
    """
    Manages lifecycle of anonymous user sessions.
    """

    def __init__(self):
        self._sessions: Dict[str, Session] = {}
        self._last_cleanup = time.time()
        logger.info("SessionManager initialized")

    # -------- Core API --------

    def create_session(self, metadata: Optional[Dict] = None) -> Session:
        """Create a new session"""
        session_id = self._generate_session_id()
        now = time.time()

        session = Session(
            session_id=session_id,
            created_at=now,
            last_active_at=now,
            metadata=metadata or {}
        )

        self._sessions[session_id] = session
        logger.info(f"Session created: {session_id}")
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID, auto-cleanup if expired"""
        session = self._sessions.get(session_id)

        if not session:
            return None

        if session.is_expired():
            self._sessions.pop(session_id, None)
            logger.info(f"Session expired: {session_id}")
            return None

        session.touch()
        return session

    def register_complaint(
        self,
        session_id: str,
        complaint_id: str,
        issue_id: str,
        category: str,
        urgency: str,
        similarity_score: Optional[float],
        is_duplicate: bool
    ) -> bool:
        """Register a complaint in session"""
        session = self.get_session(session_id)

        if not session:
            logger.warning(f"Session not found: {session_id}")
            return False

        if not session.can_submit_complaint():
            logger.warning(f"Session {session_id} at complaint limit")
            return False

        entry = SessionEntry(
            complaint_id=complaint_id,
            issue_id=issue_id,
            category=category,
            urgency=urgency,
            similarity_score=similarity_score,
            is_duplicate=is_duplicate,
            timestamp=time.time()
        )

        success = session.add_entry(entry)
        if success:
            logger.debug(f"Complaint {complaint_id} registered in session {session_id}")
        
        return success

    # -------- Maintenance --------

    def cleanup_expired_sessions(self):
        """Remove expired sessions"""
        now = time.time()

        if (now - self._last_cleanup) < SESSION_CLEANUP_INTERVAL:
            return

        expired = [
            sid for sid, session in self._sessions.items()
            if session.is_expired()
        ]

        for sid in expired:
            self._sessions.pop(sid, None)

        if expired:
            logger.info(f"Cleaned up {len(expired)} expired sessions")

        self._last_cleanup = now

    # -------- Utilities --------

    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        return f"SES-{uuid.uuid4().hex[:12]}"

    def get_stats(self) -> Dict:
        """Get session manager statistics"""
        return {
            "active_sessions": len(self._sessions),
            "total_complaints_tracked": sum(
                len(s.entries) for s in self._sessions.values()
            )
        }


# -------------------------
# Singleton Accessor
# -------------------------

_session_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """Get singleton session manager instance"""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager