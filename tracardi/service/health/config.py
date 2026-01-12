"""
Configuration for health check and graceful shutdown behavior.
"""
import os
from tracardi.service.utils.environment import get_env_as_bool, get_env_as_int, get_env_as_float


class HealthCheckConfig:
    """Configuration for health check probes"""
    
    def __init__(self):
        # Enable/disable specific health checks
        self.check_elasticsearch = get_env_as_bool('HEALTH_CHECK_ELASTICSEARCH', 'yes')
        self.check_mysql = get_env_as_bool('HEALTH_CHECK_MYSQL', 'yes')
        self.check_redis = get_env_as_bool('HEALTH_CHECK_REDIS', 'yes')
        
        # Timeouts
        self.check_timeout = get_env_as_float('HEALTH_CHECK_TIMEOUT', 5.0)
        
        # Readiness probe behavior
        self.readiness_fail_on_degraded = get_env_as_bool('HEALTH_READINESS_FAIL_ON_DEGRADED', 'no')


class GracefulShutdownConfig:
    """Configuration for graceful shutdown behavior"""
    
    def __init__(self):
        # Shutdown timeout
        self.shutdown_timeout = get_env_as_float('GRACEFUL_SHUTDOWN_TIMEOUT', 30.0)
        
        # Enable/disable specific cleanup tasks
        self.close_elasticsearch = get_env_as_bool('SHUTDOWN_CLOSE_ELASTICSEARCH', 'yes')
        self.close_mysql = get_env_as_bool('SHUTDOWN_CLOSE_MYSQL', 'yes')
        self.close_redis = get_env_as_bool('SHUTDOWN_CLOSE_REDIS', 'yes')
        self.flush_loki = get_env_as_bool('SHUTDOWN_FLUSH_LOKI', 'yes')


class StartupConfig:
    """Configuration for startup behavior"""
    
    def __init__(self):
        # Dependency wait configuration
        self.wait_for_dependencies = get_env_as_bool('STARTUP_WAIT_FOR_DEPENDENCIES', 'yes')
        self.wait_timeout = get_env_as_float('STARTUP_WAIT_TIMEOUT', 60.0)
        self.wait_max_retries = get_env_as_int('STARTUP_WAIT_MAX_RETRIES', 10)
        self.wait_retry_delay = get_env_as_float('STARTUP_WAIT_RETRY_DELAY', 2.0)
        
        # Warm-up configuration
        self.warm_up_elasticsearch = get_env_as_bool('STARTUP_WARMUP_ELASTICSEARCH', 'yes')
        self.warm_up_mysql = get_env_as_bool('STARTUP_WARMUP_MYSQL', 'yes')
        self.warm_up_redis = get_env_as_bool('STARTUP_WARMUP_REDIS', 'yes')


# Global instances
health_check_config = HealthCheckConfig()
graceful_shutdown_config = GracefulShutdownConfig()
startup_config = StartupConfig()
