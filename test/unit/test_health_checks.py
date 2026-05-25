"""
Unit tests for Kubernetes health check and graceful shutdown functionality.
"""
import unittest
from unittest.mock import Mock, patch, AsyncMock
import asyncio

from tracardi.service.health.models import HealthStatus, ComponentHealth, HealthCheckResponse
from tracardi.service.health.health_check_service import HealthCheckService


class TestHealthModels(unittest.TestCase):
    """Test health check data models"""
    
    def test_health_status_enum(self):
        """Test HealthStatus enum values"""
        self.assertEqual(HealthStatus.HEALTHY, "healthy")
        self.assertEqual(HealthStatus.UNHEALTHY, "unhealthy")
        self.assertEqual(HealthStatus.DEGRADED, "degraded")
        self.assertEqual(HealthStatus.UNKNOWN, "unknown")
    
    def test_component_health_creation(self):
        """Test ComponentHealth model creation"""
        component = ComponentHealth(
            status=HealthStatus.HEALTHY,
            message="Test message",
            response_time_ms=42.5
        )
        
        self.assertEqual(component.status, HealthStatus.HEALTHY)
        self.assertEqual(component.message, "Test message")
        self.assertEqual(component.response_time_ms, 42.5)
    
    def test_health_check_response_is_healthy(self):
        """Test is_healthy() method"""
        response = HealthCheckResponse(
            status=HealthStatus.HEALTHY,
            components={}
        )
        
        self.assertTrue(response.is_healthy())
        
        response.status = HealthStatus.UNHEALTHY
        self.assertFalse(response.is_healthy())
    
    def test_health_check_response_is_ready(self):
        """Test is_ready() method"""
        # All components healthy
        response = HealthCheckResponse(
            status=HealthStatus.HEALTHY,
            components={
                "elasticsearch": ComponentHealth(status=HealthStatus.HEALTHY),
                "mysql": ComponentHealth(status=HealthStatus.HEALTHY),
                "redis": ComponentHealth(status=HealthStatus.HEALTHY)
            }
        )
        self.assertTrue(response.is_ready())
        
        # One component unhealthy
        response.components["mysql"] = ComponentHealth(status=HealthStatus.UNHEALTHY)
        self.assertFalse(response.is_ready())


class TestHealthCheckService(unittest.IsolatedAsyncioTestCase):
    """Test HealthCheckService"""
    
    async def test_liveness_always_healthy(self):
        """Test that liveness check always returns healthy"""
        response = await HealthCheckService.liveness()
        
        self.assertEqual(response.status, HealthStatus.HEALTHY)
        self.assertIn("application", response.components)
        self.assertEqual(response.components["application"].status, HealthStatus.HEALTHY)
    
    @patch('tracardi.service.health.health_check_service.HealthCheckService._check_elasticsearch')
    @patch('tracardi.service.health.health_check_service.HealthCheckService._check_mysql')
    @patch('tracardi.service.health.health_check_service.HealthCheckService._check_redis')
    async def test_readiness_all_healthy(self, mock_redis, mock_mysql, mock_elastic):
        """Test readiness when all components are healthy"""
        # Mock all components as healthy
        mock_elastic.return_value = ComponentHealth(status=HealthStatus.HEALTHY)
        mock_mysql.return_value = ComponentHealth(status=HealthStatus.HEALTHY)
        mock_redis.return_value = ComponentHealth(status=HealthStatus.HEALTHY)
        
        response = await HealthCheckService.readiness(timeout=1.0)
        
        self.assertEqual(response.status, HealthStatus.HEALTHY)
        self.assertTrue(response.is_ready())
    
    @patch('tracardi.service.health.health_check_service.HealthCheckService._check_elasticsearch')
    @patch('tracardi.service.health.health_check_service.HealthCheckService._check_mysql')
    @patch('tracardi.service.health.health_check_service.HealthCheckService._check_redis')
    async def test_readiness_one_unhealthy(self, mock_redis, mock_mysql, mock_elastic):
        """Test readiness when one component is unhealthy"""
        mock_elastic.return_value = ComponentHealth(status=HealthStatus.HEALTHY)
        mock_mysql.return_value = ComponentHealth(status=HealthStatus.UNHEALTHY, message="Connection failed")
        mock_redis.return_value = ComponentHealth(status=HealthStatus.HEALTHY)
        
        response = await HealthCheckService.readiness(timeout=1.0)
        
        self.assertEqual(response.status, HealthStatus.UNHEALTHY)
        self.assertFalse(response.is_ready())
        self.assertEqual(response.components["mysql"].message, "Connection failed")
    
    @patch('tracardi.service.health.health_check_service.HealthCheckService._check_elasticsearch')
    async def test_readiness_check_timeout(self, mock_elastic):
        """Test readiness handles timeout gracefully"""
        # Mock timeout
        async def timeout_mock(timeout):
            await asyncio.sleep(timeout + 1)
        
        mock_elastic.side_effect = timeout_mock
        
        response = await HealthCheckService.readiness(
            check_mysql=False,
            check_redis=False,
            timeout=0.1
        )
        
        # Should still return a response
        self.assertIsInstance(response, HealthCheckResponse)
    
    async def test_elasticsearch_check_timeout(self):
        """Test Elasticsearch check with timeout"""
        with patch('tracardi.service.health.health_check_service.elastic_health') as mock_health:
            # Simulate timeout
            async def slow_health():
                await asyncio.sleep(10)
            
            mock_health.side_effect = slow_health
            
            component = await HealthCheckService._check_elasticsearch(timeout=0.1)
            
            self.assertEqual(component.status, HealthStatus.UNHEALTHY)
            self.assertIn("timeout", component.message.lower())
    
    async def test_elasticsearch_check_error(self):
        """Test Elasticsearch check with connection error"""
        with patch('tracardi.service.health.health_check_service.elastic_health') as mock_health:
            mock_health.side_effect = Exception("Connection refused")
            
            component = await HealthCheckService._check_elasticsearch(timeout=1.0)
            
            self.assertEqual(component.status, HealthStatus.UNHEALTHY)
            self.assertIn("Connection refused", component.message)
    
    def test_get_cached_status(self):
        """Test cached status retrieval"""
        HealthCheckService._elasticsearch_available = True
        HealthCheckService._mysql_available = False
        HealthCheckService._redis_available = True
        
        status = HealthCheckService.get_cached_status()
        
        self.assertTrue(status["elasticsearch"])
        self.assertFalse(status["mysql"])
        self.assertTrue(status["redis"])


class TestGracefulShutdown(unittest.IsolatedAsyncioTestCase):
    """Test graceful shutdown handler"""
    
    async def test_shutdown_handler_initialization(self):
        """Test shutdown handler can be initialized"""
        from tracardi.service.health.graceful_shutdown import GracefulShutdownHandler
        
        handler = GracefulShutdownHandler(shutdown_timeout=10.0)
        
        self.assertEqual(handler.shutdown_timeout, 10.0)
        self.assertFalse(handler.is_shutting_down())
    
    async def test_register_cleanup(self):
        """Test cleanup function registration"""
        from tracardi.service.health.graceful_shutdown import GracefulShutdownHandler
        
        handler = GracefulShutdownHandler()
        
        async def dummy_cleanup():
            pass
        
        handler.register_cleanup(dummy_cleanup)
        
        self.assertEqual(len(handler._cleanup_functions), 1)
    
    async def test_shutdown_runs_cleanups(self):
        """Test that shutdown runs all cleanup functions"""
        from tracardi.service.health.graceful_shutdown import GracefulShutdownHandler
        
        handler = GracefulShutdownHandler(shutdown_timeout=5.0)
        
        cleanup_called = []
        
        async def cleanup1():
            cleanup_called.append(1)
        
        async def cleanup2():
            cleanup_called.append(2)
        
        handler.register_cleanup(cleanup1)
        handler.register_cleanup(cleanup2)
        
        await handler.shutdown()
        
        self.assertTrue(handler.is_shutting_down())
        self.assertEqual(len(cleanup_called), 2)
        self.assertIn(1, cleanup_called)
        self.assertIn(2, cleanup_called)
    
    async def test_shutdown_timeout(self):
        """Test shutdown respects timeout"""
        from tracardi.service.health.graceful_shutdown import GracefulShutdownHandler
        
        handler = GracefulShutdownHandler(shutdown_timeout=0.5)
        
        async def slow_cleanup():
            await asyncio.sleep(10)  # Longer than timeout
        
        handler.register_cleanup(slow_cleanup)
        
        import time
        start = time.time()
        await handler.shutdown()
        duration = time.time() - start
        
        # Should complete around timeout, not wait for full 10s
        self.assertLess(duration, 2.0)


class TestStartupHandler(unittest.IsolatedAsyncioTestCase):
    """Test startup handler"""
    
    async def test_startup_handler_initialization(self):
        """Test startup handler can be initialized"""
        from tracardi.service.health.startup_handler import StartupHandler
        
        handler = StartupHandler(max_retries=5, retry_delay=1.0)
        
        self.assertEqual(handler.max_retries, 5)
        self.assertEqual(handler.retry_delay, 1.0)
    
    async def test_register_init(self):
        """Test init function registration"""
        from tracardi.service.health.startup_handler import StartupHandler
        
        handler = StartupHandler()
        
        async def dummy_init():
            pass
        
        handler.register_init(dummy_init)
        
        self.assertEqual(len(handler._init_functions), 1)
    
    @patch('tracardi.service.health.startup_handler.HealthCheckService.readiness')
    async def test_wait_for_dependencies_success(self, mock_readiness):
        """Test waiting for dependencies when they're ready"""
        from tracardi.service.health.startup_handler import StartupHandler
        
        # Mock readiness as ready
        mock_response = Mock()
        mock_response.is_ready.return_value = True
        mock_readiness.return_value = mock_response
        
        handler = StartupHandler(max_retries=3, retry_delay=0.1)
        
        # Should complete without error
        await handler.wait_for_dependencies(timeout=5.0)
        
        self.assertTrue(mock_readiness.called)
    
    @patch('tracardi.service.health.startup_handler.HealthCheckService.readiness')
    async def test_wait_for_dependencies_timeout(self, mock_readiness):
        """Test waiting for dependencies with timeout"""
        from tracardi.service.health.startup_handler import StartupHandler
        
        # Mock readiness as never ready
        mock_response = Mock()
        mock_response.is_ready.return_value = False
        mock_readiness.return_value = mock_response
        
        handler = StartupHandler(max_retries=2, retry_delay=0.1)
        
        # Should raise timeout error
        with self.assertRaises(TimeoutError):
            await handler.wait_for_dependencies(timeout=0.5)


if __name__ == '__main__':
    unittest.main()
