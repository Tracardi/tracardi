"""
Prometheus /metrics endpoint for FastAPI.
"""
from typing import Optional


def create_metrics_endpoint():
    """
    Create /metrics endpoint for Prometheus scraping.
    
    Usage in FastAPI:
        from tracardi.service.metrics.endpoint import create_metrics_endpoint
        
        metrics_endpoint = create_metrics_endpoint()
        if metrics_endpoint:
            app.add_route("/metrics", metrics_endpoint)
    
    Returns:
        Callable or None if Prometheus is disabled
    """
    try:
        from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
        from tracardi.service.metrics.config import prometheus_config
        from tracardi.service.metrics import metrics_manager
        
        if not prometheus_config.enabled:
            return None
        
        # Initialize metrics on first call
        metrics_manager.initialize()
        
        async def metrics():
            """Expose Prometheus metrics"""
            registry = metrics_manager.get_registry()
            metrics_output = generate_latest(registry)
            
            # Return Response (FastAPI/Starlette)
            from starlette.responses import Response
            return Response(
                content=metrics_output,
                media_type=CONTENT_TYPE_LATEST
            )
        
        return metrics
        
    except ImportError:
        return None
    except Exception as e:
        import logging
        logging.error(f"Failed to create metrics endpoint: {e}")
        return None


def install_metrics_endpoint(app, path: Optional[str] = None):
    """
    Install /metrics endpoint on FastAPI app.
    
    Args:
        app: FastAPI application instance
        path: Custom path for metrics endpoint (default: /metrics)
    
    Example:
        from fastapi import FastAPI
        from tracardi.service.metrics.endpoint import install_metrics_endpoint
        
        app = FastAPI()
        install_metrics_endpoint(app)
    """
    from tracardi.service.metrics.config import prometheus_config
    
    if not prometheus_config.enabled:
        return
    
    if path is None:
        path = prometheus_config.metrics_path
    
    metrics_endpoint = create_metrics_endpoint()
    if metrics_endpoint:
        app.add_route(path, metrics_endpoint, methods=["GET"])
        import logging
        logging.info(f"✓ Prometheus metrics endpoint installed at {path}")
