#!/usr/bin/env python3
"""
Metrics Registry
Day 7B.2 - System behavior quantification
"""

from collections import defaultdict
from typing import Dict, List, Optional
import time
import threading
from datetime import datetime


class Counter:
    """Thread-safe counter metric"""
    
    def __init__(self):
        self._value = 0
        self._lock = threading.Lock()
    
    def inc(self, amount: int = 1):
        """Increment counter"""
        with self._lock:
            self._value += amount
    
    @property
    def value(self) -> int:
        """Get current value"""
        with self._lock:
            return self._value
    
    def reset(self):
        """Reset counter (testing only)"""
        with self._lock:
            self._value = 0


class Gauge:
    """Thread-safe gauge metric"""
    
    def __init__(self):
        self._value = 0.0
        self._lock = threading.Lock()
    
    def set(self, value: float):
        """Set gauge value"""
        with self._lock:
            self._value = value
    
    def inc(self, amount: float = 1.0):
        """Increment gauge"""
        with self._lock:
            self._value += amount
    
    def dec(self, amount: float = 1.0):
        """Decrement gauge"""
        with self._lock:
            self._value -= amount
    
    @property
    def value(self) -> float:
        """Get current value"""
        with self._lock:
            return self._value


class Histogram:
    """Thread-safe histogram for latency tracking"""
    
    def __init__(self):
        self._values: List[float] = []
        self._lock = threading.Lock()
    
    def observe(self, value: float):
        """Record observation"""
        with self._lock:
            self._values.append(value)
    
    def get_stats(self) -> Dict[str, float]:
        """Calculate statistics"""
        with self._lock:
            if not self._values:
                return {
                    "count": 0,
                    "sum": 0.0,
                    "avg": 0.0,
                    "min": 0.0,
                    "max": 0.0,
                    "p50": 0.0,
                    "p95": 0.0,
                    "p99": 0.0
                }
            
            values = sorted(self._values)
            count = len(values)
            
            return {
                "count": count,
                "sum": sum(values),
                "avg": sum(values) / count,
                "min": values[0],
                "max": values[-1],
                "p50": self._percentile(values, 50),
                "p95": self._percentile(values, 95),
                "p99": self._percentile(values, 99)
            }
    
    def _percentile(self, sorted_values: List[float], p: int) -> float:
        """Calculate percentile"""
        if not sorted_values:
            return 0.0
        k = (len(sorted_values) - 1) * p / 100
        f = int(k)
        c = f + 1
        if c >= len(sorted_values):
            return sorted_values[-1]
        return sorted_values[f] + (k - f) * (sorted_values[c] - sorted_values[f])
    
    def reset(self):
        """Reset histogram (testing only)"""
        with self._lock:
            self._values = []


class MetricsRegistry:
    """
    Central metrics registry.
    
    Design:
    - Low cardinality labels
    - Thread-safe operations
    - Minimal memory footprint
    """
    
    def __init__(self):
        self._counters: Dict[str, Counter] = defaultdict(Counter)
        self._gauges: Dict[str, Gauge] = defaultdict(Gauge)
        self._histograms: Dict[str, Histogram] = defaultdict(Histogram)
        self._lock = threading.Lock()
        self._created_at = datetime.utcnow()
    
    def counter(self, name: str) -> Counter:
        """Get or create counter"""
        with self._lock:
            return self._counters[name]
    
    def gauge(self, name: str) -> Gauge:
        """Get or create gauge"""
        with self._lock:
            return self._gauges[name]
    
    def histogram(self, name: str) -> Histogram:
        """Get or create histogram"""
        with self._lock:
            return self._histograms[name]
    
    def get_snapshot(self) -> Dict:
        """Get all metrics snapshot"""
        with self._lock:
            return {
                "counters": {
                    name: counter.value
                    for name, counter in self._counters.items()
                },
                "gauges": {
                    name: gauge.value
                    for name, gauge in self._gauges.items()
                },
                "histograms": {
                    name: histogram.get_stats()
                    for name, histogram in self._histograms.items()
                },
                "meta": {
                    "created_at": self._created_at.isoformat(),
                    "uptime_seconds": (datetime.utcnow() - self._created_at).total_seconds()
                }
            }
    
    def reset_all(self):
        """Reset all metrics (testing only)"""
        with self._lock:
            for counter in self._counters.values():
                counter.reset()
            for histogram in self._histograms.values():
                histogram.reset()
            self._created_at = datetime.utcnow()


# Singleton instance
_metrics: Optional[MetricsRegistry] = None


def get_metrics() -> MetricsRegistry:
    """Get singleton metrics registry"""
    global _metrics
    if _metrics is None:
        _metrics = MetricsRegistry()
    return _metrics