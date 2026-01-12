"""
Prometheus metrics integration for Tracardi.

Optional metrics collection and exposition for monitoring with Prometheus.
Enable with PROMETHEUS_ENABLED=yes environment variable.

Usage:
    from tracardi.service.metrics import metrics_manager, track_request
    
    # Track HTTP request
    with track_request("/api/track", "POST"):
        # ... handle request ...
        pass
    
    # Custom metrics
    metrics_manager.increment_counter("custom_events_total", {"type": "page_view"})
"""

from .config import prometheus_config
from .metrics_manager import metrics_manager, track_request, track_database_query

__all__ = [
    'prometheus_config',
    'metrics_manager',
    'track_request',
    'track_database_query'
]
