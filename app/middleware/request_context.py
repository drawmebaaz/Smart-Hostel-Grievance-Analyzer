#!/usr/bin/env python3
"""
Request Context Middleware
Day 7B.3 - Request ID propagation
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time

from app.observability.context import (
    generate_request_id,
    set_request_id,
    clear_context
)
from app.observability.logger import get_logger
from app.observability.metrics import get_metrics

logger = get_logger(__name__)
metrics = get_metrics()


class RequestContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware that:
    1. Generates/accepts request_id
    2. Sets up request context
    3. Logs request/response
    4. Tracks request latency
    """
    
    async def dispatch(self, request: Request, call_next):
        # Generate or extract request ID
        request_id = request.headers.get("X-Request-ID") or generate_request_id()
        set_request_id(request_id)
        
        # Track request
        start_time = time.perf_counter()
        metrics.counter("http_requests_total").inc()
        
        # Log request
        logger.info(
            "http_request_received",
            method=request.method,
            path=request.url.path,
            client=request.client.host if request.client else None
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate latency
            latency_ms = (time.perf_counter() - start_time) * 1000
            metrics.histogram("http_request_latency_ms").observe(latency_ms)
            
            # Log response
            logger.info(
                "http_request_completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                latency_ms=round(latency_ms, 2)
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            # Track errors
            metrics.counter("http_errors_total").inc()
            
            # Log error
            logger.error(
                "http_request_failed",
                method=request.method,
                path=request.url.path,
                error=str(e)
            )
            
            raise
        
        finally:
            # Clear context
            clear_context()