"""
Health check and readiness probe services for Kubernetes deployments.

This module provides comprehensive health checking for all stateful services:
- Elasticsearch
- MySQL  
- Redis

All checks are configurable via environment variables to support optional services.

Usage in FastAPI:
    from tracardi.service.health import HealthCheckService
    
    @app.get("/health")
    async def health():
        return await HealthCheckService.liveness()
    
    @app.get("/ready")
    async def readiness():
        return await HealthCheckService.readiness()

Configuration via environment variables:
    HEALTH_CHECK_ELASTICSEARCH=yes|no  (default: yes)
    HEALTH_CHECK_MYSQL=yes|no          (default: yes)
    HEALTH_CHECK_REDIS=yes|no          (default: yes)
    HEALTH_CHECK_TIMEOUT=5.0           (default: 5.0 seconds)
    
    SHUTDOWN_CLOSE_ELASTICSEARCH=yes|no  (default: yes)
    SHUTDOWN_CLOSE_MYSQL=yes|no          (default: yes)
    SHUTDOWN_CLOSE_REDIS=yes|no          (default: yes)
    SHUTDOWN_FLUSH_LOKI=yes|no           (default: yes)
    GRACEFUL_SHUTDOWN_TIMEOUT=30.0       (default: 30.0 seconds)
    
    STARTUP_WARMUP_ELASTICSEARCH=yes|no  (default: yes)
    STARTUP_WARMUP_MYSQL=yes|no          (default: yes)
    STARTUP_WARMUP_REDIS=yes|no          (default: yes)
    STARTUP_WAIT_FOR_DEPENDENCIES=yes|no (default: yes)
    STARTUP_WAIT_TIMEOUT=60.0            (default: 60.0 seconds)
"""

from .health_check_service import HealthCheckService
from .models import HealthStatus, ComponentHealth, HealthCheckResponse
from .config import health_check_config, graceful_shutdown_config, startup_config

__all__ = [
    'HealthCheckService',
    'HealthStatus',
    'ComponentHealth',
    'HealthCheckResponse',
    'health_check_config',
    'graceful_shutdown_config',
    'startup_config'
]
