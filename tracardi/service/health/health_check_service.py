"""
Unified health check service for all Tracardi components.
"""
import asyncio
from time import time
from typing import Optional
import logging

from tracardi.service.health.models import (
    HealthStatus,
    ComponentHealth,
    HealthCheckResponse
)
from tracardi.version import version

logger = logging.getLogger(__name__)


class HealthCheckService:
    """
    Comprehensive health check service for Kubernetes deployments.
    
    Provides two types of checks:
    1. Liveness: Is the application running? (process health)
    2. Readiness: Can the application serve traffic? (dependencies health)
    """
    
    _elasticsearch_available = None
    _mysql_available = None
    _redis_available = None
    
    @classmethod
    async def liveness(cls) -> HealthCheckResponse:
        """
        Liveness probe - checks if the application process is alive.
        
        This is a lightweight check that should always pass if the process is running.
        Kubernetes will restart the pod if this fails.
        
        Returns:
            HealthCheckResponse: Basic health status
        """
        return HealthCheckResponse(
            status=HealthStatus.HEALTHY,
            version=version.version,
            components={
                "application": ComponentHealth(
                    status=HealthStatus.HEALTHY,
                    message="Application process is running"
                )
            }
        )
    
    @classmethod
    async def readiness(cls, check_elasticsearch: bool = True,
                       check_mysql: bool = True,
                       check_redis: bool = True,
                       timeout: float = 5.0) -> HealthCheckResponse:
        """
        Readiness probe - checks if the application can serve traffic.
        
        This checks all critical dependencies. Kubernetes will remove the pod
        from service if this fails, but won't restart it.
        
        Args:
            check_elasticsearch: Check Elasticsearch health
            check_mysql: Check MySQL health
            check_redis: Check Redis health
            timeout: Timeout for each check in seconds
            
        Returns:
            HealthCheckResponse: Detailed health status of all components
        """
        components = {}
        tasks = []
        
        # Collect all check tasks
        if check_elasticsearch:
            tasks.append(("elasticsearch", cls._check_elasticsearch(timeout)))
        if check_mysql:
            tasks.append(("mysql", cls._check_mysql(timeout)))
        if check_redis:
            tasks.append(("redis", cls._check_redis(timeout)))
        
        # Run all checks concurrently
        for name, task in tasks:
            try:
                component_health = await task
                components[name] = component_health
            except Exception as e:
                logger.error(f"Health check failed for {name}: {e}")
                components[name] = ComponentHealth(
                    status=HealthStatus.UNHEALTHY,
                    message=f"Health check error: {str(e)}"
                )
        
        # Determine overall status
        all_healthy = all(c.status == HealthStatus.HEALTHY for c in components.values())
        any_unhealthy = any(c.status == HealthStatus.UNHEALTHY for c in components.values())
        
        if all_healthy:
            overall_status = HealthStatus.HEALTHY
        elif any_unhealthy:
            overall_status = HealthStatus.UNHEALTHY
        else:
            overall_status = HealthStatus.DEGRADED
        
        return HealthCheckResponse(
            status=overall_status,
            version=version.version,
            components=components
        )
    
    @classmethod
    async def _check_elasticsearch(cls, timeout: float) -> ComponentHealth:
        """Check Elasticsearch health"""
        start_time = time()
        
        try:
            # Import here to avoid circular dependencies
            from tracardi.service.storage.elastic.interface.raw import health as elastic_health
            
            # Run with timeout
            health_data = await asyncio.wait_for(
                elastic_health(),
                timeout=timeout
            )
            
            response_time = (time() - start_time) * 1000
            
            # Check cluster health
            cluster_status = health_data.get('status', 'unknown')
            
            if cluster_status == 'green':
                status = HealthStatus.HEALTHY
                message = "Elasticsearch cluster is healthy"
            elif cluster_status == 'yellow':
                status = HealthStatus.DEGRADED
                message = "Elasticsearch cluster is degraded (yellow)"
            else:
                status = HealthStatus.UNHEALTHY
                message = f"Elasticsearch cluster is unhealthy ({cluster_status})"
            
            cls._elasticsearch_available = True
            
            return ComponentHealth(
                status=status,
                message=message,
                response_time_ms=response_time,
                details={
                    "cluster_name": health_data.get('cluster_name'),
                    "number_of_nodes": health_data.get('number_of_nodes'),
                    "active_shards": health_data.get('active_shards')
                }
            )
            
        except asyncio.TimeoutError:
            cls._elasticsearch_available = False
            return ComponentHealth(
                status=HealthStatus.UNHEALTHY,
                message=f"Elasticsearch health check timeout after {timeout}s"
            )
        except Exception as e:
            cls._elasticsearch_available = False
            return ComponentHealth(
                status=HealthStatus.UNHEALTHY,
                message=f"Elasticsearch connection error: {str(e)}"
            )
    
    @classmethod
    async def _check_mysql(cls, timeout: float) -> ComponentHealth:
        """Check MySQL health"""
        start_time = time()
        
        try:
            # Import here to avoid circular dependencies
            from tracardi.service.storage.mysql.engine import AsyncMySqlEngine
            
            engine = AsyncMySqlEngine()
            
            # Simple query to check connection
            async def check_connection():
                async with engine.get_connection() as conn:
                    async with conn.cursor() as cursor:
                        await cursor.execute("SELECT 1")
                        result = await cursor.fetchone()
                        return result is not None
            
            # Run with timeout
            is_connected = await asyncio.wait_for(
                check_connection(),
                timeout=timeout
            )
            
            response_time = (time() - start_time) * 1000
            
            if is_connected:
                cls._mysql_available = True
                return ComponentHealth(
                    status=HealthStatus.HEALTHY,
                    message="MySQL is accessible",
                    response_time_ms=response_time
                )
            else:
                cls._mysql_available = False
                return ComponentHealth(
                    status=HealthStatus.UNHEALTHY,
                    message="MySQL query failed"
                )
                
        except asyncio.TimeoutError:
            cls._mysql_available = False
            return ComponentHealth(
                status=HealthStatus.UNHEALTHY,
                message=f"MySQL health check timeout after {timeout}s"
            )
        except Exception as e:
            cls._mysql_available = False
            return ComponentHealth(
                status=HealthStatus.UNHEALTHY,
                message=f"MySQL connection error: {str(e)}"
            )
    
    @classmethod
    async def _check_redis(cls, timeout: float) -> ComponentHealth:
        """Check Redis health"""
        start_time = time()
        
        try:
            # Import here to avoid circular dependencies
            from tracardi.service.storage.redis.driver.redis_client import RedisClient
            
            redis_client = RedisClient()
            
            # Run ping with timeout
            async def check_ping():
                return redis_client.ping()
            
            is_alive = await asyncio.wait_for(
                asyncio.to_thread(check_ping),
                timeout=timeout
            )
            
            response_time = (time() - start_time) * 1000
            
            if is_alive:
                cls._redis_available = True
                return ComponentHealth(
                    status=HealthStatus.HEALTHY,
                    message="Redis is accessible",
                    response_time_ms=response_time
                )
            else:
                cls._redis_available = False
                return ComponentHealth(
                    status=HealthStatus.UNHEALTHY,
                    message="Redis ping failed"
                )
                
        except asyncio.TimeoutError:
            cls._redis_available = False
            return ComponentHealth(
                status=HealthStatus.UNHEALTHY,
                message=f"Redis health check timeout after {timeout}s"
            )
        except Exception as e:
            cls._redis_available = False
            return ComponentHealth(
                status=HealthStatus.UNHEALTHY,
                message=f"Redis connection error: {str(e)}"
            )
    
    @classmethod
    def get_cached_status(cls) -> dict:
        """Get cached availability status of components"""
        return {
            "elasticsearch": cls._elasticsearch_available,
            "mysql": cls._mysql_available,
            "redis": cls._redis_available
        }
