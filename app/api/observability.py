#!/usr/bin/env python3
"""
Observability API Endpoints
Day 7B - Metrics exposure
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from app.observability.metrics import get_metrics
from app.observability.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/observability", tags=["Observability"])


@router.get(
    "/metrics",
    summary="Get system metrics",
    description="Returns all metrics (counters, gauges, histograms)"
)
async def get_system_metrics() -> Dict[str, Any]:
    """
    Get comprehensive system metrics.
    
    Returns:
        - counters: Total counts
        - gauges: Current values
        - histograms: Latency statistics
        - meta: System metadata
    """
    try:
        metrics = get_metrics()
        snapshot = metrics.get_snapshot()
        
        logger.info("metrics_snapshot_requested")
        
        return {
            "success": True,
            "metrics": snapshot
        }
        
    except Exception as e:
        logger.error("metrics_snapshot_failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve metrics: {str(e)}"
        )


@router.get(
    "/health",
    summary="Health check with metrics",
    description="Returns service health with key metrics"
)
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint with key metrics.
    
    Returns basic health status plus critical metrics.
    """
    try:
        metrics = get_metrics()
        snapshot = metrics.get_snapshot()
        
        # Extract key health indicators
        counters = snapshot["counters"]
        histograms = snapshot["histograms"]
        
        # Calculate error rate
        total_requests = counters.get("http_requests_total", 0)
        total_errors = counters.get("http_errors_total", 0)
        error_rate = (total_errors / max(1, total_requests)) * 100
        
        # Get average latency
        latency_stats = histograms.get("http_request_latency_ms", {})
        avg_latency = latency_stats.get("avg", 0)
        
        # Determine health status
        is_healthy = error_rate < 5.0 and avg_latency < 1000
        
        return {
            "status": "healthy" if is_healthy else "degraded",
            "error_rate_percent": round(error_rate, 2),
            "avg_latency_ms": round(avg_latency, 2),
            "total_requests": total_requests,
            "uptime_seconds": snapshot["meta"]["uptime_seconds"]
        }
        
    except Exception as e:
        logger.error("health_check_failed", error=str(e))
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@router.post(
    "/metrics/reset",
    summary="Reset metrics (dev only)",
    description="⚠️ DEVELOPMENT ONLY: Reset all metrics"
)
async def reset_metrics():
    """
    Reset all metrics (development/testing only).
    
    ⚠️ WARNING: This clears all metrics!
    """
    try:
        metrics = get_metrics()
        metrics.reset_all()
        
        logger.warning("metrics_reset_requested")
        
        return {
            "success": True,
            "message": "All metrics reset"
        }
        
    except Exception as e:
        logger.error("metrics_reset_failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reset metrics: {str(e)}"
        )