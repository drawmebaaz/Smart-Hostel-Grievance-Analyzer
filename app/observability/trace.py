#!/usr/bin/env python3
"""
Optional Request Tracing
Day 7B.3 - Timeline reconstruction for debugging
"""

import time
from typing import List, Tuple, Optional
from app.observability.context import get_request_id


class Trace:
    """
    Lightweight request trace for debugging.
    
    Usage:
        trace.mark("duplicate_check_start")
        trace.mark("duplicate_check_end")
    
    Only enabled in debug mode.
    """
    
    def __init__(self):
        self.events: List[Tuple[str, float]] = []
        self.start_time = time.perf_counter()
    
    def mark(self, event_name: str):
        """Mark event in trace"""
        elapsed = (time.perf_counter() - self.start_time) * 1000  # ms
        self.events.append((event_name, elapsed))
    
    def get_timeline(self) -> List[dict]:
        """Get formatted timeline"""
        return [
            {
                "event": name,
                "elapsed_ms": round(elapsed, 2)
            }
            for name, elapsed in self.events
        ]
    
    def reset(self):
        """Reset trace"""
        self.events = []
        self.start_time = time.perf_counter()


# Thread-local trace instance
import threading
_local = threading.local()


def get_trace() -> Trace:
    """Get thread-local trace instance"""
    if not hasattr(_local, 'trace'):
        _local.trace = Trace()
    return _local.trace


def reset_trace():
    """Reset current trace"""
    if hasattr(_local, 'trace'):
        _local.trace.reset()