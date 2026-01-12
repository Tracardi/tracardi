"""
Advanced Prometheus metrics for Tracardi CDP.

Tracks:
- Cache performance (Redis hit/miss)
- Plugin execution (success/error/duration)
- Rule engine performance
- Workflow errors
- Queue depths
- Destination dispatch
- Profile operations
"""
import logging
from contextlib import contextmanager
from typing import Optional

logger = logging.getLogger(__name__)


class AdvancedMetricsManager:
    """
    Advanced metrics for CDP-specific operations.
    """
    
    def __init__(self):
        self._initialized = False
        self._registry = None
        
        # Cache metrics
        self.cache_hits_total = None
        self.cache_misses_total = None
        self.cache_operations_duration_seconds = None
        
        # Plugin metrics
        self.plugin_executions_total = None
        self.plugin_execution_duration_seconds = None
        self.plugin_errors_total = None
        
        # Rule engine metrics
        self.rules_evaluated_total = None
        self.rules_matched_total = None
        self.rule_evaluation_duration_seconds = None
        
        # Workflow metrics
        self.workflow_errors_total = None
        self.workflow_nodes_executed_total = None
        
        # Queue metrics
        self.queue_depth = None
        self.queue_messages_total = None
        
        # Destination metrics
        self.destination_dispatch_total = None
        self.destination_dispatch_errors_total = None
        
        # Profile operations
        self.profile_merges_total = None
        self.profile_loads_total = None
        self.profile_saves_total = None
    
    def initialize(self, registry):
        """Initialize advanced metrics"""
        if self._initialized:
            return
        
        try:
            from prometheus_client import Counter, Histogram, Gauge
            from tracardi.service.metrics.config import prometheus_config
            
            if not prometheus_config.enabled:
                return
            
            self._registry = registry
            common_labels = ['service', 'environment', 'instance']
            
            # Cache Metrics
            self.cache_hits_total = Counter(
                'tracardi_cache_hits_total',
                'Cache hits',
                ['cache_type', 'operation'] + common_labels,
                registry=registry
            )
            
            self.cache_misses_total = Counter(
                'tracardi_cache_misses_total',
                'Cache misses',
                ['cache_type', 'operation'] + common_labels,
                registry=registry
            )
            
            self.cache_operations_duration_seconds = Histogram(
                'tracardi_cache_operation_duration_seconds',
                'Cache operation latency',
                ['cache_type', 'operation'] + common_labels,
                buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5],
                registry=registry
            )
            
            # Plugin Metrics
            self.plugin_executions_total = Counter(
                'tracardi_plugin_executions_total',
                'Plugin executions',
                ['plugin_id', 'plugin_name', 'status'] + common_labels,
                registry=registry
            )
            
            self.plugin_execution_duration_seconds = Histogram(
                'tracardi_plugin_execution_duration_seconds',
                'Plugin execution latency',
                ['plugin_id', 'plugin_name'] + common_labels,
                buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
                registry=registry
            )
            
            self.plugin_errors_total = Counter(
                'tracardi_plugin_errors_total',
                'Plugin errors',
                ['plugin_id', 'plugin_name', 'error_type'] + common_labels,
                registry=registry
            )
            
            # Rule Engine Metrics
            self.rules_evaluated_total = Counter(
                'tracardi_rules_evaluated_total',
                'Rules evaluated',
                ['event_type'] + common_labels,
                registry=registry
            )
            
            self.rules_matched_total = Counter(
                'tracardi_rules_matched_total',
                'Rules matched',
                ['rule_id', 'rule_name', 'event_type'] + common_labels,
                registry=registry
            )
            
            self.rule_evaluation_duration_seconds = Histogram(
                'tracardi_rule_evaluation_duration_seconds',
                'Rule evaluation latency',
                ['event_type'] + common_labels,
                buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5],
                registry=registry
            )
            
            # Workflow Error Metrics
            self.workflow_errors_total = Counter(
                'tracardi_workflow_errors_total',
                'Workflow errors',
                ['workflow_id', 'workflow_name', 'error_type'] + common_labels,
                registry=registry
            )
            
            self.workflow_nodes_executed_total = Counter(
                'tracardi_workflow_nodes_executed_total',
                'Workflow nodes executed',
                ['workflow_id', 'node_id', 'node_type'] + common_labels,
                registry=registry
            )
            
            # Queue Metrics
            self.queue_depth = Gauge(
                'tracardi_queue_depth',
                'Queue depth',
                ['queue_name', 'queue_type'] + common_labels,
                registry=registry
            )
            
            self.queue_messages_total = Counter(
                'tracardi_queue_messages_total',
                'Queue messages processed',
                ['queue_name', 'queue_type', 'status'] + common_labels,
                registry=registry
            )
            
            # Destination Metrics
            self.destination_dispatch_total = Counter(
                'tracardi_destination_dispatch_total',
                'Destination dispatches',
                ['destination_id', 'destination_type', 'status'] + common_labels,
                registry=registry
            )
            
            self.destination_dispatch_errors_total = Counter(
                'tracardi_destination_dispatch_errors_total',
                'Destination dispatch errors',
                ['destination_id', 'destination_type', 'error_type'] + common_labels,
                registry=registry
            )
            
            # Profile Operations
            self.profile_merges_total = Counter(
                'tracardi_profile_merges_total',
                'Profile merges',
                ['merge_type'] + common_labels,
                registry=registry
            )
            
            self.profile_loads_total = Counter(
                'tracardi_profile_loads_total',
                'Profile loads',
                ['source'] + common_labels,
                registry=registry
            )
            
            self.profile_saves_total = Counter(
                'tracardi_profile_saves_total',
                'Profile saves',
                ['destination'] + common_labels,
                registry=registry
            )
            
            self._initialized = True
            logger.info("✓ Advanced Prometheus metrics initialized")
            
        except ImportError:
            pass
        except Exception as e:
            logger.error(f"Failed to initialize advanced metrics: {e}")
    
    def _get_common_labels(self) -> dict:
        """Get common labels"""
        from tracardi.service.metrics.config import prometheus_config
        return {
            'service': prometheus_config.service_name,
            'environment': prometheus_config.environment,
            'instance': prometheus_config.instance
        }
    
    # Cache tracking
    def track_cache_hit(self, cache_type: str, operation: str = "get"):
        """Track cache hit"""
        if not self._initialized or not self.cache_hits_total:
            return
        try:
            labels = {'cache_type': cache_type, 'operation': operation, **self._get_common_labels()}
            self.cache_hits_total.labels(**labels).inc()
        except Exception as e:
            logger.debug(f"Error tracking cache hit: {e}")
    
    def track_cache_miss(self, cache_type: str, operation: str = "get"):
        """Track cache miss"""
        if not self._initialized or not self.cache_misses_total:
            return
        try:
            labels = {'cache_type': cache_type, 'operation': operation, **self._get_common_labels()}
            self.cache_misses_total.labels(**labels).inc()
        except Exception as e:
            logger.debug(f"Error tracking cache miss: {e}")
    
    def track_cache_operation(self, cache_type: str, operation: str, duration: float):
        """Track cache operation duration"""
        if not self._initialized or not self.cache_operations_duration_seconds:
            return
        try:
            labels = {'cache_type': cache_type, 'operation': operation, **self._get_common_labels()}
            self.cache_operations_duration_seconds.labels(**labels).observe(duration)
        except Exception as e:
            logger.debug(f"Error tracking cache operation: {e}")
    
    # Plugin tracking
    def track_plugin_execution(self, plugin_id: str, plugin_name: str, status: str, duration: float):
        """Track plugin execution"""
        if not self._initialized:
            return
        try:
            if self.plugin_executions_total:
                labels = {'plugin_id': plugin_id, 'plugin_name': plugin_name, 'status': status, **self._get_common_labels()}
                self.plugin_executions_total.labels(**labels).inc()
            
            if self.plugin_execution_duration_seconds and status == 'success':
                labels = {'plugin_id': plugin_id, 'plugin_name': plugin_name, **self._get_common_labels()}
                self.plugin_execution_duration_seconds.labels(**labels).observe(duration)
        except Exception as e:
            logger.debug(f"Error tracking plugin execution: {e}")
    
    def track_plugin_error(self, plugin_id: str, plugin_name: str, error_type: str):
        """Track plugin error"""
        if not self._initialized or not self.plugin_errors_total:
            return
        try:
            labels = {'plugin_id': plugin_id, 'plugin_name': plugin_name, 'error_type': error_type, **self._get_common_labels()}
            self.plugin_errors_total.labels(**labels).inc()
        except Exception as e:
            logger.debug(f"Error tracking plugin error: {e}")
    
    # Rule engine tracking
    def track_rule_evaluation(self, event_type: str, duration: float, matched_count: int):
        """Track rule evaluation"""
        if not self._initialized:
            return
        try:
            if self.rules_evaluated_total:
                labels = {'event_type': event_type, **self._get_common_labels()}
                self.rules_evaluated_total.labels(**labels).inc()
            
            if self.rule_evaluation_duration_seconds:
                labels = {'event_type': event_type, **self._get_common_labels()}
                self.rule_evaluation_duration_seconds.labels(**labels).observe(duration)
        except Exception as e:
            logger.debug(f"Error tracking rule evaluation: {e}")
    
    def track_rule_match(self, rule_id: str, rule_name: str, event_type: str):
        """Track rule match"""
        if not self._initialized or not self.rules_matched_total:
            return
        try:
            labels = {'rule_id': rule_id, 'rule_name': rule_name, 'event_type': event_type, **self._get_common_labels()}
            self.rules_matched_total.labels(**labels).inc()
        except Exception as e:
            logger.debug(f"Error tracking rule match: {e}")
    
    # Workflow tracking
    def track_workflow_error(self, workflow_id: str, workflow_name: str, error_type: str):
        """Track workflow error"""
        if not self._initialized or not self.workflow_errors_total:
            return
        try:
            labels = {'workflow_id': workflow_id, 'workflow_name': workflow_name, 'error_type': error_type, **self._get_common_labels()}
            self.workflow_errors_total.labels(**labels).inc()
        except Exception as e:
            logger.debug(f"Error tracking workflow error: {e}")
    
    def track_workflow_node_execution(self, workflow_id: str, node_id: str, node_type: str):
        """Track workflow node execution"""
        if not self._initialized or not self.workflow_nodes_executed_total:
            return
        try:
            labels = {'workflow_id': workflow_id, 'node_id': node_id, 'node_type': node_type, **self._get_common_labels()}
            self.workflow_nodes_executed_total.labels(**labels).inc()
        except Exception as e:
            logger.debug(f"Error tracking workflow node: {e}")
    
    # Queue tracking
    def set_queue_depth(self, queue_name: str, queue_type: str, depth: int):
        """Set queue depth"""
        if not self._initialized or not self.queue_depth:
            return
        try:
            labels = {'queue_name': queue_name, 'queue_type': queue_type, **self._get_common_labels()}
            self.queue_depth.labels(**labels).set(depth)
        except Exception as e:
            logger.debug(f"Error setting queue depth: {e}")
    
    def track_queue_message(self, queue_name: str, queue_type: str, status: str):
        """Track queue message"""
        if not self._initialized or not self.queue_messages_total:
            return
        try:
            labels = {'queue_name': queue_name, 'queue_type': queue_type, 'status': status, **self._get_common_labels()}
            self.queue_messages_total.labels(**labels).inc()
        except Exception as e:
            logger.debug(f"Error tracking queue message: {e}")
    
    # Destination tracking
    def track_destination_dispatch(self, destination_id: str, destination_type: str, status: str):
        """Track destination dispatch"""
        if not self._initialized or not self.destination_dispatch_total:
            return
        try:
            labels = {'destination_id': destination_id, 'destination_type': destination_type, 'status': status, **self._get_common_labels()}
            self.destination_dispatch_total.labels(**labels).inc()
        except Exception as e:
            logger.debug(f"Error tracking destination dispatch: {e}")
    
    def track_destination_error(self, destination_id: str, destination_type: str, error_type: str):
        """Track destination error"""
        if not self._initialized or not self.destination_dispatch_errors_total:
            return
        try:
            labels = {'destination_id': destination_id, 'destination_type': destination_type, 'error_type': error_type, **self._get_common_labels()}
            self.destination_dispatch_errors_total.labels(**labels).inc()
        except Exception as e:
            logger.debug(f"Error tracking destination error: {e}")
    
    # Profile operations
    def track_profile_merge(self, merge_type: str = "auto"):
        """Track profile merge"""
        if not self._initialized or not self.profile_merges_total:
            return
        try:
            labels = {'merge_type': merge_type, **self._get_common_labels()}
            self.profile_merges_total.labels(**labels).inc()
        except Exception as e:
            logger.debug(f"Error tracking profile merge: {e}")
    
    def track_profile_load(self, source: str = "database"):
        """Track profile load"""
        if not self._initialized or not self.profile_loads_total:
            return
        try:
            labels = {'source': source, **self._get_common_labels()}
            self.profile_loads_total.labels(**labels).inc()
        except Exception as e:
            logger.debug(f"Error tracking profile load: {e}")
    
    def track_profile_save(self, destination: str = "database"):
        """Track profile save"""
        if not self._initialized or not self.profile_saves_total:
            return
        try:
            labels = {'destination': destination, **self._get_common_labels()}
            self.profile_saves_total.labels(**labels).inc()
        except Exception as e:
            logger.debug(f"Error tracking profile save: {e}")


# Global instance
advanced_metrics_manager = AdvancedMetricsManager()


@contextmanager
def track_cache_operation(cache_type: str, operation: str = "get"):
    """Context manager for tracking cache operations"""
    import time
    start_time = time.time()
    hit = False
    
    try:
        yield lambda: setattr(track_cache_operation, 'hit', True)
        hit = getattr(track_cache_operation, 'hit', False)
    finally:
        duration = time.time() - start_time
        if hit:
            advanced_metrics_manager.track_cache_hit(cache_type, operation)
        else:
            advanced_metrics_manager.track_cache_miss(cache_type, operation)
        advanced_metrics_manager.track_cache_operation(cache_type, operation, duration)
