"""
Prometheus metrics configuration.
"""
import os
from tracardi.service.utils.environment import get_env_as_bool, get_env_as_int


class PrometheusConfig:
    """Configuration for Prometheus metrics"""
    
    def __init__(self):
        # Enable/disable Prometheus metrics
        self.enabled = get_env_as_bool('PROMETHEUS_ENABLED', 'no')
        
        # Metrics endpoint path
        self.metrics_path = os.environ.get('PROMETHEUS_METRICS_PATH', '/metrics')
        
        # Enable specific metric types
        self.track_http_requests = get_env_as_bool('PROMETHEUS_TRACK_HTTP', 'yes')
        self.track_database_queries = get_env_as_bool('PROMETHEUS_TRACK_DATABASE', 'yes')
        self.track_health_checks = get_env_as_bool('PROMETHEUS_TRACK_HEALTH', 'yes')
        self.track_events = get_env_as_bool('PROMETHEUS_TRACK_EVENTS', 'yes')
        
        # Histogram buckets for latency (in seconds)
        self.latency_buckets = [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
        
        # Custom labels
        self.service_name = os.environ.get('PROMETHEUS_SERVICE_NAME', 'tracardi')
        self.environment = os.environ.get('PROMETHEUS_ENVIRONMENT', 'production')
        self.instance = os.environ.get('PROMETHEUS_INSTANCE', os.environ.get('HOSTNAME', 'unknown'))


# Global instance
prometheus_config = PrometheusConfig()
