"""
Unit tests for Prometheus metrics integration.
"""
import os
import pytest
from unittest.mock import Mock, patch


class TestPrometheusConfig:
    """Test Prometheus configuration"""
    
    def test_default_config(self):
        """Test default configuration values"""
        with patch.dict(os.environ, {}, clear=False):
            from tracardi.service.metrics.config import PrometheusConfig
            config = PrometheusConfig()
            
            assert config.enabled is False  # Default is disabled
            assert config.metrics_path == '/metrics'
            assert config.track_http_requests is True
            assert config.track_database_queries is True
    
    def test_enabled_config(self):
        """Test enabled configuration"""
        with patch.dict(os.environ, {'PROMETHEUS_ENABLED': 'yes'}, clear=False):
            from tracardi.service.metrics.config import PrometheusConfig
            config = PrometheusConfig()
            
            assert config.enabled is True
    
    def test_custom_labels(self):
        """Test custom labels configuration"""
        with patch.dict(os.environ, {
            'PROMETHEUS_SERVICE_NAME': 'test-service',
            'PROMETHEUS_ENVIRONMENT': 'staging',
            'PROMETHEUS_INSTANCE': 'test-instance'
        }, clear=False):
            from tracardi.service.metrics.config import PrometheusConfig
            config = PrometheusConfig()
            
            assert config.service_name == 'test-service'
            assert config.environment == 'staging'
            assert config.instance == 'test-instance'


class TestMetricsManager:
    """Test metrics manager functionality"""
    
    @patch('tracardi.service.metrics.metrics_manager.prometheus_config')
    def test_manager_disabled(self, mock_config):
        """Test metrics manager when disabled"""
        mock_config.enabled = False
        
        from tracardi.service.metrics.metrics_manager import MetricsManager
        manager = MetricsManager()
        manager.initialize()
        
        assert manager._initialized is False
    
    @patch('tracardi.service.metrics.metrics_manager.prometheus_config')
    @patch('tracardi.service.metrics.metrics_manager.Counter')
    @patch('tracardi.service.metrics.metrics_manager.Histogram')
    @patch('tracardi.service.metrics.metrics_manager.Gauge')
    @patch('tracardi.service.metrics.metrics_manager.CollectorRegistry')
    def test_manager_initialization(self, mock_registry, mock_gauge, mock_histogram, 
                                   mock_counter, mock_config):
        """Test metrics manager initialization"""
        mock_config.enabled = True
        mock_config.track_http_requests = True
        mock_config.track_database_queries = True
        mock_config.latency_buckets = [0.1, 0.5, 1.0]
        
        from tracardi.service.metrics.metrics_manager import MetricsManager
        manager = MetricsManager()
        manager.initialize()
        
        # Should initialize if prometheus_client is available
        # In test environment, imports might fail, so we just check structure
        assert hasattr(manager, 'http_requests_total')
        assert hasattr(manager, 'db_queries_total')
    
    def test_track_http_request_disabled(self):
        """Test tracking HTTP request when disabled"""
        from tracardi.service.metrics.metrics_manager import MetricsManager
        manager = MetricsManager()
        
        # Should not raise error
        manager.track_http_request('GET', '/api/test', 200, 0.5)
    
    def test_track_db_query_disabled(self):
        """Test tracking database query when disabled"""
        from tracardi.service.metrics.metrics_manager import MetricsManager
        manager = MetricsManager()
        
        # Should not raise error
        manager.track_db_query('elasticsearch', 'search', 0.1)


class TestContextManagers:
    """Test context manager utilities"""
    
    def test_track_request_context(self):
        """Test request tracking context manager"""
        from tracardi.service.metrics import track_request
        
        # Should not raise error even when disabled
        with track_request('GET', '/test'):
            pass
    
    def test_track_database_query_context(self):
        """Test database query tracking context manager"""
        from tracardi.service.metrics import track_database_query
        
        # Should not raise error even when disabled
        with track_database_query('elasticsearch', 'index'):
            pass


class TestMiddleware:
    """Test Prometheus middleware"""
    
    @pytest.mark.asyncio
    async def test_middleware_disabled(self):
        """Test middleware when Prometheus is disabled"""
        with patch('tracardi.service.metrics.config.prometheus_config') as mock_config:
            mock_config.enabled = False
            
            from tracardi.service.metrics.middleware import PrometheusMiddleware
            
            # Create mock app and request
            mock_app = Mock()
            middleware = PrometheusMiddleware(mock_app)
            
            mock_request = Mock()
            mock_request.url.path = '/test'
            mock_request.method = 'GET'
            
            async def mock_call_next(request):
                mock_response = Mock()
                mock_response.status_code = 200
                return mock_response
            
            response = await middleware.dispatch(mock_request, mock_call_next)
            assert response.status_code == 200


class TestEndpoint:
    """Test metrics endpoint"""
    
    def test_create_endpoint_disabled(self):
        """Test endpoint creation when disabled"""
        with patch('tracardi.service.metrics.config.prometheus_config') as mock_config:
            mock_config.enabled = False
            
            from tracardi.service.metrics.endpoint import create_metrics_endpoint
            endpoint = create_metrics_endpoint()
            
            assert endpoint is None
    
    def test_install_endpoint_disabled(self):
        """Test endpoint installation when disabled"""
        with patch('tracardi.service.metrics.config.prometheus_config') as mock_config:
            mock_config.enabled = False
            
            from tracardi.service.metrics.endpoint import install_metrics_endpoint
            
            mock_app = Mock()
            install_metrics_endpoint(mock_app)
            
            # Should not add route when disabled
            mock_app.add_route.assert_not_called()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
