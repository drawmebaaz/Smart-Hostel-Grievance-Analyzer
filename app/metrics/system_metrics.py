#!/usr/bin/env python3
"""
System Metrics Collector
Day 6.5 - Observability and monitoring
"""

from dataclasses import dataclass, field
from typing import Dict
from datetime import datetime
import threading

from app.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class SystemMetrics:
    """System-wide metrics collector"""
    
    # Complaint metrics
    complaints_total: int = 0
    complaints_success: int = 0
    complaints_rejected: int = 0
    complaints_failed: int = 0
    
    # Duplicate detection
    duplicates_detected: int = 0
    unique_complaints: int = 0
    
    # Session metrics
    sessions_created: int = 0
    sessions_expired: int = 0
    
    # Heuristic triggers
    follow_ups_detected: int = 0
    escalations_detected: int = 0
    noise_flagged: int = 0
    
    # Issue metrics
    issues_created: int = 0
    issues_updated: int = 0
    
    # Performance
    avg_processing_time_ms: float = 0.0
    total_requests: int = 0
    
    # Errors
    classification_errors: int = 0
    embedding_errors: int = 0
    db_errors: int = 0
    
    # Timestamps
    started_at: datetime = field(default_factory=datetime.utcnow)
    last_reset: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        self._lock = threading.Lock()
    
    # ==================== COMPLAINT METRICS ====================
    
    def record_complaint_success(self):
        """Record successful complaint processing"""
        with self._lock:
            self.complaints_total += 1
            self.complaints_success += 1
    
    def record_complaint_rejection(self):
        """Record complaint rejection (validation)"""
        with self._lock:
            self.complaints_total += 1
            self.complaints_rejected += 1
    
    def record_complaint_failure(self):
        """Record complaint processing failure"""
        with self._lock:
            self.complaints_total += 1
            self.complaints_failed += 1
    
    def record_duplicate(self):
        """Record duplicate detection"""
        with self._lock:
            self.duplicates_detected += 1
    
    def record_unique_complaint(self):
        """Record unique complaint"""
        with self._lock:
            self.unique_complaints += 1
    
    # ==================== SESSION METRICS ====================
    
    def record_session_created(self):
        """Record session creation"""
        with self._lock:
            self.sessions_created += 1
    
    def record_session_expired(self):
        """Record session expiration"""
        with self._lock:
            self.sessions_expired += 1
    
    # ==================== HEURISTIC METRICS ====================
    
    def record_follow_up(self):
        """Record follow-up detection"""
        with self._lock:
            self.follow_ups_detected += 1
    
    def record_escalation(self):
        """Record escalation detection"""
        with self._lock:
            self.escalations_detected += 1
    
    def record_noise_flag(self):
        """Record noise flagging"""
        with self._lock:
            self.noise_flagged += 1
    
    # ==================== ISSUE METRICS ====================
    
    def record_issue_created(self):
        """Record issue creation"""
        with self._lock:
            self.issues_created += 1
    
    def record_issue_updated(self):
        """Record issue update"""
        with self._lock:
            self.issues_updated += 1
    
    # ==================== PERFORMANCE METRICS ====================
    
    def record_processing_time(self, time_ms: float):
        """Record processing time"""
        with self._lock:
            self.total_requests += 1
            # Running average
            n = self.total_requests
            self.avg_processing_time_ms = (
                (self.avg_processing_time_ms * (n - 1) + time_ms) / n
            )
    
    # ==================== ERROR METRICS ====================
    
    def record_classification_error(self):
        """Record classification error"""
        with self._lock:
            self.classification_errors += 1
    
    def record_embedding_error(self):
        """Record embedding error"""
        with self._lock:
            self.embedding_errors += 1
    
    def record_db_error(self):
        """Record database error"""
        with self._lock:
            self.db_errors += 1
    
    # ==================== REPORTING ====================
    
    def get_snapshot(self) -> Dict:
        """Get current metrics snapshot"""
        with self._lock:
            uptime_seconds = (datetime.utcnow() - self.started_at).total_seconds()
            
            return {
                "complaints": {
                    "total": self.complaints_total,
                    "success": self.complaints_success,
                    "rejected": self.complaints_rejected,
                    "failed": self.complaints_failed,
                    "success_rate": round(
                        self.complaints_success / max(1, self.complaints_total), 4
                    )
                },
                "duplicates": {
                    "detected": self.duplicates_detected,
                    "unique": self.unique_complaints,
                    "duplicate_rate": round(
                        self.duplicates_detected / max(1, self.complaints_total), 4
                    )
                },
                "sessions": {
                    "created": self.sessions_created,
                    "expired": self.sessions_expired
                },
                "heuristics": {
                    "follow_ups": self.follow_ups_detected,
                    "escalations": self.escalations_detected,
                    "noise_flags": self.noise_flagged
                },
                "issues": {
                    "created": self.issues_created,
                    "updated": self.issues_updated
                },
                "performance": {
                    "avg_processing_time_ms": round(self.avg_processing_time_ms, 2),
                    "total_requests": self.total_requests
                },
                "errors": {
                    "classification": self.classification_errors,
                    "embedding": self.embedding_errors,
                    "database": self.db_errors,
                    "total": (
                        self.classification_errors +
                        self.embedding_errors +
                        self.db_errors
                    )
                },
                "system": {
                    "started_at": self.started_at.isoformat(),
                    "uptime_seconds": round(uptime_seconds, 2),
                    "uptime_hours": round(uptime_seconds / 3600, 2)
                }
            }
    
    def reset(self):
        """Reset all metrics (for testing)"""
        with self._lock:
            self.__init__()
            logger.warning("System metrics reset")


# ==================== SINGLETON ====================

_metrics: SystemMetrics = None


def get_metrics() -> SystemMetrics:
    """Get singleton metrics instance"""
    global _metrics
    if _metrics is None:
        _metrics = SystemMetrics()
        logger.info("System metrics initialized")
    return _metrics