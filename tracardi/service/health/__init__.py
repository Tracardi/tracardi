"""
Health check and readiness probe services for Kubernetes deployments.

This module provides comprehensive health checking for all stateful services:
- Elasticsearch
- MySQL
- Redis

Usage in FastAPI:
    from tracardi.service.health import HealthCheckService
    
    @app.get("/health")
    async def health():
        return await HealthCheckService.liveness()
    
    @app.get("/ready")
    async def readiness():
        return await HealthCheckService.readiness()
"""

from .health_check_service import HealthCheckService
from .models import HealthStatus, ComponentHealth, HealthCheckResponse

__all__ = [
    'HealthCheckService',
    'HealthStatus',
    'ComponentHealth',
    'HealthCheckResponse'
]
