#!/usr/bin/env python3
"""
Structured Logger
Day 7B.1 - Machine-readable, correlatable logs
"""

import logging
import json
from datetime import datetime
from typing import Any, Optional
from app.observability.context import get_request_id


class StructuredLogger:
    """
    Structured logger that emits JSON logs with request context.
    
    Design:
    - Every log is a JSON object
    - Includes request_id automatically
    - Event-oriented naming
    - Low-cardinality fields
    """
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.name = name
    
    def _log(self, level: str, event: str, **fields):
        """Internal log method with structured format"""
        request_id = get_request_id()
        
        payload = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": level,
            "event": event,
            "source": self.name,
            **fields
        }
        
        # Add request_id if available
        if request_id:
            payload["request_id"] = request_id
        
        # Use standard logging with JSON payload
        log_level = getattr(logging, level)
        self.logger.log(log_level, json.dumps(payload))
    
    def info(self, event: str, **fields):
        """Log INFO level event"""
        self._log("INFO", event, **fields)
    
    def warning(self, event: str, **fields):
        """Log WARNING level event"""
        self._log("WARNING", event, **fields)
    
    def error(self, event: str, **fields):
        """Log ERROR level event"""
        self._log("ERROR", event, **fields)
    
    def critical(self, event: str, **fields):
        """Log CRITICAL level event"""
        self._log("CRITICAL", event, **fields)


def get_structured_logger(name: str) -> StructuredLogger:
    """Get structured logger instance"""
    return StructuredLogger(name)


# Convenience function for backward compatibility
def get_logger(name: str) -> StructuredLogger:
    """Get structured logger (replaces old logger)"""
    return get_structured_logger(name)