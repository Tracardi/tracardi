"""
Prometheus middleware for automatic request instrumentation.
"""
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class PrometheusMiddleware(BaseHTTPMiddleware):
    """
    Middleware for automatic Prometheus metrics collection.
    
    Automatically tracks:
    - HTTP request count
    - HTTP request duration
    - HTTP requests in progress
    - Status codes
    
    Usage in FastAPI:
        from fastapi import FastAPI
        from tracardi.service.metrics.middleware import PrometheusMiddleware
        
        app = FastAPI()
        app.add_middleware(PrometheusMiddleware)
    """
    
    def __init__(self, app):
        super().__init__(app)
        self._initialized = False
        self._metrics_manager = None
        self._config = None
        self._init()
    
    def _init(self):
        """Initialize metrics manager"""
        try:
            from tracardi.service.metrics import metrics_manager, prometheus_config
            from tracardi.service.metrics.config import prometheus_config as config
            
            if not config.enabled:
                return
            
            self._config = config
            self._metrics_manager = metrics_manager
            self._metrics_manager.initialize()
            self._initialized = True
            
        except ImportError:
            pass
        except Exception as e:
            import logging
            logging.error(f"Failed to initialize Prometheus middleware: {e}")
    
    async def dispatch(self, request: Request, call_next):
        """Process request and track metrics"""
        if not self._initialized:
            return await call_next(request)
        
        # Skip metrics endpoint itself
        if request.url.path == self._config.metrics_path:
            return await call_next(request)
        
        # Track request
        start_time = time.time()
        method = request.method
        endpoint = request.url.path
        
        # Increment in-progress
        if self._metrics_manager.http_requests_in_progress:
            try:
                labels = {
                    'method': method,
                    'endpoint': endpoint,
                    **self._metrics_manager._get_common_labels()
                }
                self._metrics_manager.http_requests_in_progress.labels(**labels).inc()
            except:
                pass
        
        # Process request
        status = 500
        try:
            response = await call_next(request)
            status = response.status_code
            return response
        except Exception as e:
            status = 500
            raise
        finally:
            # Track metrics
            duration = time.time() - start_time
            self._metrics_manager.track_http_request(method, endpoint, status, duration)
            
            # Decrement in-progress
            if self._metrics_manager.http_requests_in_progress:
                try:
                    labels = {
                        'method': method,
                        'endpoint': endpoint,
                        **self._metrics_manager._get_common_labels()
                    }
                    self._metrics_manager.http_requests_in_progress.labels(**labels).dec()
                except:
                    pass


def install_prometheus_middleware(app):
    """
    Install Prometheus middleware on FastAPI app.
    
    Args:
        app: FastAPI application instance
    
    Example:
        from fastapi import FastAPI
        from tracardi.service.metrics.middleware import install_prometheus_middleware
        
        app = FastAPI()
        install_prometheus_middleware(app)
    """
    from tracardi.service.metrics.config import prometheus_config
    
    if not prometheus_config.enabled:
        return
    
    app.add_middleware(PrometheusMiddleware)
    
    import logging
    logging.info("✓ Prometheus middleware installed")
