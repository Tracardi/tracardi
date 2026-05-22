"""
Prometheus metrics manager for Tracardi.
"""
import time
from contextlib import contextmanager
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class MetricsManager:
    """
    Manager for Prometheus metrics collection.
    
    Provides a unified interface for tracking various metrics:
    - HTTP requests (latency, status codes, method)
    - Database queries (latency, operations)
    - Health checks (status, response time)
    - Events (counts, types)
    - Custom business metrics
    """
    
    def __init__(self):
        self._initialized = False
        self._registry = None
        
        # Metrics instances
        self.http_requests_total = None
        self.http_request_duration_seconds = None
        self.http_requests_in_progress = None
        
        self.db_queries_total = None
        self.db_query_duration_seconds = None
        self.db_connections_active = None
        
        self.health_check_status = None
        self.health_check_duration_seconds = None
        
        self.events_processed_total = None
        self.profiles_updated_total = None
        self.workflows_executed_total = None
    
    def initialize(self):
        """Initialize Prometheus metrics"""
        if self._initialized:
            return
        
        try:
            from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry
            from tracardi.service.metrics.config import prometheus_config
            
            if not prometheus_config.enabled:
                logger.info("Prometheus metrics disabled")
                return
            
            self._registry = CollectorRegistry()
            
            # Initialize advanced metrics with same registry
            try:
                from tracardi.service.metrics.advanced_metrics import advanced_metrics_manager
                advanced_metrics_manager.initialize(self._registry)
            except Exception as e:
                logger.warning(f"Failed to initialize advanced metrics: {e}")
            
            # Common labels
            common_labels = ['service', 'environment', 'instance']
            
            # HTTP Metrics
            if prometheus_config.track_http_requests:
                self.http_requests_total = Counter(
                    'tracardi_http_requests_total',
                    'Total HTTP requests',
                    ['method', 'endpoint', 'status'] + common_labels,
                    registry=self._registry
                )
                
                self.http_request_duration_seconds = Histogram(
                    'tracardi_http_request_duration_seconds',
                    'HTTP request latency',
                    ['method', 'endpoint'] + common_labels,
                    buckets=prometheus_config.latency_buckets,
                    registry=self._registry
                )
                
                self.http_requests_in_progress = Gauge(
                    'tracardi_http_requests_in_progress',
                    'HTTP requests currently being processed',
                    ['method', 'endpoint'] + common_labels,
                    registry=self._registry
                )
            
            # Database Metrics
            if prometheus_config.track_database_queries:
                self.db_queries_total = Counter(
                    'tracardi_db_queries_total',
                    'Total database queries',
                    ['database', 'operation'] + common_labels,
                    registry=self._registry
                )
                
                self.db_query_duration_seconds = Histogram(
                    'tracardi_db_query_duration_seconds',
                    'Database query latency',
                    ['database', 'operation'] + common_labels,
                    buckets=prometheus_config.latency_buckets,
                    registry=self._registry
                )
                
                self.db_connections_active = Gauge(
                    'tracardi_db_connections_active',
                    'Active database connections',
                    ['database'] + common_labels,
                    registry=self._registry
                )
            
            # Health Check Metrics
            if prometheus_config.track_health_checks:
                self.health_check_status = Gauge(
                    'tracardi_health_check_status',
                    'Health check status (1=healthy, 0=unhealthy)',
                    ['component'] + common_labels,
                    registry=self._registry
                )
                
                self.health_check_duration_seconds = Histogram(
                    'tracardi_health_check_duration_seconds',
                    'Health check duration',
                    ['component'] + common_labels,
                    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0],
                    registry=self._registry
                )
            
            # Event Processing Metrics
            if prometheus_config.track_events:
                self.events_processed_total = Counter(
                    'tracardi_events_processed_total',
                    'Total events processed',
                    ['event_type', 'source'] + common_labels,
                    registry=self._registry
                )
                
                self.profiles_updated_total = Counter(
                    'tracardi_profiles_updated_total',
                    'Total profiles updated',
                    common_labels,
                    registry=self._registry
                )
                
                self.workflows_executed_total = Counter(
                    'tracardi_workflows_executed_total',
                    'Total workflows executed',
                    ['workflow_id', 'status'] + common_labels,
                    registry=self._registry
                )
            
            self._initialized = True
            logger.info("✓ Prometheus metrics initialized")
            
        except ImportError:
            logger.warning("prometheus_client not installed, metrics disabled")
        except Exception as e:
            logger.error(f"Failed to initialize Prometheus metrics: {e}")
    
    def get_registry(self):
        """Get Prometheus registry for /metrics endpoint"""
        if not self._initialized:
            self.initialize()
        return self._registry
    
    def _get_common_labels(self) -> dict:
        """Get common labels for all metrics"""
        from tracardi.service.metrics.config import prometheus_config
        return {
            'service': prometheus_config.service_name,
            'environment': prometheus_config.environment,
            'instance': prometheus_config.instance
        }
    
    def track_http_request(self, method: str, endpoint: str, status: int, duration: float):
        """Track HTTP request"""
        if not self._initialized or not self.http_requests_total:
            return
        
        try:
            labels = {
                'method': method,
                'endpoint': endpoint,
                'status': str(status),
                **self._get_common_labels()
            }
            self.http_requests_total.labels(**labels).inc()
            
            duration_labels = {
                'method': method,
                'endpoint': endpoint,
                **self._get_common_labels()
            }
            self.http_request_duration_seconds.labels(**duration_labels).observe(duration)
        except Exception as e:
            logger.debug(f"Error tracking HTTP request: {e}")
    
    def track_db_query(self, database: str, operation: str, duration: float):
        """Track database query"""
        if not self._initialized or not self.db_queries_total:
            return
        
        try:
            labels = {
                'database': database,
                'operation': operation,
                **self._get_common_labels()
            }
            self.db_queries_total.labels(**labels).inc()
            self.db_query_duration_seconds.labels(**labels).observe(duration)
        except Exception as e:
            logger.debug(f"Error tracking DB query: {e}")
    
    def set_db_connections(self, database: str, count: int):
        """Set active database connections"""
        if not self._initialized or not self.db_connections_active:
            return
        
        try:
            labels = {
                'database': database,
                **self._get_common_labels()
            }
            self.db_connections_active.labels(**labels).set(count)
        except Exception as e:
            logger.debug(f"Error setting DB connections: {e}")
    
    def track_health_check(self, component: str, is_healthy: bool, duration: float):
        """Track health check"""
        if not self._initialized or not self.health_check_status:
            return
        
        try:
            labels = {
                'component': component,
                **self._get_common_labels()
            }
            self.health_check_status.labels(**labels).set(1 if is_healthy else 0)
            self.health_check_duration_seconds.labels(**labels).observe(duration)
        except Exception as e:
            logger.debug(f"Error tracking health check: {e}")
    
    def track_event(self, event_type: str, source: str = "unknown"):
        """Track event processing"""
        if not self._initialized or not self.events_processed_total:
            return
        
        try:
            labels = {
                'event_type': event_type,
                'source': source,
                **self._get_common_labels()
            }
            self.events_processed_total.labels(**labels).inc()
        except Exception as e:
            logger.debug(f"Error tracking event: {e}")
    
    def track_profile_update(self):
        """Track profile update"""
        if not self._initialized or not self.profiles_updated_total:
            return
        
        try:
            self.profiles_updated_total.labels(**self._get_common_labels()).inc()
        except Exception as e:
            logger.debug(f"Error tracking profile update: {e}")
    
    def track_workflow_execution(self, workflow_id: str, status: str):
        """Track workflow execution"""
        if not self._initialized or not self.workflows_executed_total:
            return
        
        try:
            labels = {
                'workflow_id': workflow_id,
                'status': status,
                **self._get_common_labels()
            }
            self.workflows_executed_total.labels(**labels).inc()
        except Exception as e:
            logger.debug(f"Error tracking workflow: {e}")


# Global instance
metrics_manager = MetricsManager()


@contextmanager
def track_request(method: str, endpoint: str):
    """Context manager for tracking HTTP requests"""
    if not metrics_manager._initialized:
        metrics_manager.initialize()
    
    start_time = time.time()
    status = 500  # Default to error
    
    try:
        # Track in progress
        if metrics_manager.http_requests_in_progress:
            labels = {
                'method': method,
                'endpoint': endpoint,
                **metrics_manager._get_common_labels()
            }
            metrics_manager.http_requests_in_progress.labels(**labels).inc()
        
        yield
        
        status = 200  # Success if no exception
    except Exception:
        status = 500
        raise
    finally:
        duration = time.time() - start_time
        metrics_manager.track_http_request(method, endpoint, status, duration)
        
        # Decrement in progress
        if metrics_manager.http_requests_in_progress:
            labels = {
                'method': method,
                'endpoint': endpoint,
                **metrics_manager._get_common_labels()
            }
            metrics_manager.http_requests_in_progress.labels(**labels).dec()


@contextmanager
def track_database_query(database: str, operation: str):
    """Context manager for tracking database queries"""
    if not metrics_manager._initialized:
        metrics_manager.initialize()
    
    start_time = time.time()
    
    try:
        yield
    finally:
        duration = time.time() - start_time
        metrics_manager.track_db_query(database, operation, duration)
