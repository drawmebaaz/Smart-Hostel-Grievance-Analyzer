#!/usr/bin/env python3
"""
Request Context Management
Day 7B.3 - Thread-safe request ID propagation
"""

import contextvars
import uuid
from typing import Optional

# Context variable for request ID (async-safe)
_request_id = contextvars.ContextVar("request_id", default=None)
_user_context = contextvars.ContextVar("user_context", default=None)


def generate_request_id() -> str:
    """Generate unique request ID"""
    return f"REQ-{uuid.uuid4().hex[:12]}"


def set_request_id(request_id: str):
    """Set request ID in context"""
    _request_id.set(request_id)


def get_request_id() -> Optional[str]:
    """Get current request ID from context"""
    return _request_id.get()


def set_user_context(context: dict):
    """Set user context (session_id, etc.)"""
    _user_context.set(context)


def get_user_context() -> Optional[dict]:
    """Get current user context"""
    return _user_context.get()


def clear_context():
    """Clear all context (useful for testing)"""
    _request_id.set(None)
    _user_context.set(None)