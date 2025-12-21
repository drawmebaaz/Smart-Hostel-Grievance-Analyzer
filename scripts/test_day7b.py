#!/usr/bin/env python3
"""
Day 7B Testing Script
Tests observability features
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.observability.context import (
    generate_request_id,
    set_request_id,
    get_request_id
)
from app.observability.logger import get_logger
from app.observability.metrics import get_metrics
from app.observability.trace import get_trace

logger = get_logger(__name__)


def test_request_context():
    """Test request context propagation"""
    print("\n" + "=" * 60)
    print("TEST 1: Request Context")
    print("=" * 60)
    
    # Generate and set request ID
    request_id = generate_request_id()
    set_request_id(request_id)
    
    # Verify it's retrievable
    retrieved_id = get_request_id()
    assert retrieved_id == request_id
    
    print(f"✓ Request ID set: {request_id}")
    print(f"✓ Request ID retrieved: {retrieved_id}")
    print("✅ Request context: PASSED")


def test_structured_logging():
    """Test structured logging"""
    print("\n" + "=" * 60)
    print("TEST 2: Structured Logging")
    print("=" * 60)
    
    # Set request context
    set_request_id("TEST-REQ-123")
    
    # Log various events
    logger.info("test_event", action="create", entity="issue")
    logger.warning("test_warning", reason="duplicate")
    logger.error("test_error", error_code="DB_001")
    
    print("✓ Logged INFO event")
    print("✓ Logged WARNING event")
    print("✓ Logged ERROR event")
    print("✅ Structured logging: PASSED")


def test_metrics():
    """Test metrics registry"""
    print("\n" + "=" * 60)
    print("TEST 3: Metrics Registry")
    print("=" * 60)
    
    metrics = get_metrics()
    
    # Test counter
    metrics.counter("test_counter").inc()
    metrics.counter("test_counter").inc(5)
    assert metrics.counter("test_counter").value == 6
    print("✓ Counter: 6")
    
    # Test gauge
    metrics.gauge("test_gauge").set(100)
    metrics.gauge("test_gauge").inc(50)
    assert metrics.gauge("test_gauge").value == 150
    print("✓ Gauge: 150")
    
    # Test histogram
    for val in [10, 20, 30, 40, 50]:
        metrics.histogram("test_latency").observe(val)
    
    stats = metrics.histogram("test_latency").get_stats()
    assert stats["count"] == 5
    assert stats["avg"] == 30
    print(f"✓ Histogram: count={stats['count']}, avg={stats['avg']}")
    
    print("✅ Metrics: PASSED")


def test_trace():
    """Test tracing"""
    print("\n" + "=" * 60)
    print("TEST 4: Request Tracing")
    print("=" * 60)
    
    trace = get_trace()
    trace.reset()
    
    trace.mark("operation_start")
    trace.mark("db_query")
    trace.mark("operation_end")
    
    timeline = trace.get_timeline()
    assert len(timeline) == 3
    
    print(f"✓ Trace events: {len(timeline)}")
    for event in timeline:
        print(f"  {event['event']}: {event['elapsed_ms']}ms")
    
    print("✅ Tracing: PASSED")


def test_metrics_snapshot():
    """Test metrics snapshot"""
    print("\n" + "=" * 60)
    print("TEST 5: Metrics Snapshot")
    print("=" * 60)
    
    metrics = get_metrics()
    snapshot = metrics.get_snapshot()
    
    assert "counters" in snapshot
    assert "gauges" in snapshot
    assert "histograms" in snapshot
    assert "meta" in snapshot
    
    print(f"✓ Counters: {len(snapshot['counters'])}")
    print(f"✓ Gauges: {len(snapshot['gauges'])}")
    print(f"✓ Histograms: {len(snapshot['histograms'])}")
    print(f"✓ Uptime: {snapshot['meta']['uptime_seconds']:.2f}s")
    
    print("✅ Metrics snapshot: PASSED")


def main():
    """Run all tests"""
    try:
        print("=" * 60)
        print("DAY 7B OBSERVABILITY TESTING")
        print("=" * 60)
        
        test_request_context()
        test_structured_logging()
        test_metrics()
        test_trace()
        test_metrics_snapshot()
        
        print("\n" + "=" * 60)
        print("✅ ALL DAY 7B TESTS PASSED")
        print("=" * 60)
        print("\nDay 7B Features Verified:")
        print("  ✅ Request context propagation")
        print("  ✅ Structured JSON logging")
        print("  ✅ Metrics registry (counters, gauges, histograms)")
        print("  ✅ Request tracing")
        print("  ✅ Metrics snapshot API")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ TEST ERROR: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()