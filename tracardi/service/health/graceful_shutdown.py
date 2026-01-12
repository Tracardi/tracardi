"""
Graceful shutdown handlers for Kubernetes deployments.

Handles SIGTERM signals and ensures clean shutdown of all services.
"""
import asyncio
import signal
import logging
from typing import Callable, List, Awaitable
from functools import wraps

logger = logging.getLogger(__name__)


class GracefulShutdownHandler:
    """
    Manages graceful shutdown of the application.
    
    When a SIGTERM is received (e.g., from Kubernetes), this handler:
    1. Stops accepting new requests
    2. Waits for ongoing requests to complete
    3. Closes all database connections
    4. Flushes logs
    5. Exits cleanly
    
    Usage:
        shutdown_handler = GracefulShutdownHandler(
            shutdown_timeout=30.0
        )
        
        # Register cleanup functions
        shutdown_handler.register_cleanup(close_database)
        shutdown_handler.register_cleanup(flush_logs)
        
        # Install signal handlers
        shutdown_handler.install_signal_handlers()
    """
    
    def __init__(self, shutdown_timeout: float = 30.0):
        """
        Initialize graceful shutdown handler.
        
        Args:
            shutdown_timeout: Maximum time to wait for shutdown in seconds
        """
        self.shutdown_timeout = shutdown_timeout
        self._cleanup_functions: List[Callable[[], Awaitable[None]]] = []
        self._is_shutting_down = False
        self._shutdown_event = asyncio.Event()
    
    def register_cleanup(self, cleanup_fn: Callable[[], Awaitable[None]]):
        """
        Register a cleanup function to be called during shutdown.
        
        Args:
            cleanup_fn: Async function to call during shutdown
        """
        self._cleanup_functions.append(cleanup_fn)
        logger.info(f"Registered cleanup function: {cleanup_fn.__name__}")
    
    def is_shutting_down(self) -> bool:
        """Check if shutdown has been initiated"""
        return self._is_shutting_down
    
    async def wait_for_shutdown(self):
        """Wait for shutdown signal"""
        await self._shutdown_event.wait()
    
    async def shutdown(self):
        """
        Perform graceful shutdown.
        
        This method:
        1. Sets shutdown flag
        2. Runs all cleanup functions
        3. Waits for completion or timeout
        """
        if self._is_shutting_down:
            logger.warning("Shutdown already in progress")
            return
        
        self._is_shutting_down = True
        logger.info("=" * 60)
        logger.info("Graceful shutdown initiated")
        logger.info("=" * 60)
        
        try:
            # Run all cleanup functions
            cleanup_tasks = []
            for cleanup_fn in self._cleanup_functions:
                logger.info(f"Running cleanup: {cleanup_fn.__name__}")
                task = asyncio.create_task(cleanup_fn())
                cleanup_tasks.append(task)
            
            if cleanup_tasks:
                # Wait for all cleanups with timeout
                done, pending = await asyncio.wait(
                    cleanup_tasks,
                    timeout=self.shutdown_timeout,
                    return_when=asyncio.ALL_COMPLETED
                )
                
                if pending:
                    logger.warning(
                        f"Timeout: {len(pending)} cleanup tasks did not complete "
                        f"within {self.shutdown_timeout}s"
                    )
                    # Cancel pending tasks
                    for task in pending:
                        task.cancel()
                
                # Check for errors
                for task in done:
                    try:
                        await task
                    except Exception as e:
                        logger.error(f"Cleanup task failed: {e}", exc_info=True)
            
            logger.info("=" * 60)
            logger.info("Graceful shutdown completed")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}", exc_info=True)
        finally:
            self._shutdown_event.set()
    
    def install_signal_handlers(self):
        """
        Install signal handlers for SIGTERM and SIGINT.
        
        This allows the application to respond to Kubernetes termination signals.
        """
        def handle_signal(signum, frame):
            """Signal handler that triggers graceful shutdown"""
            sig_name = signal.Signals(signum).name
            logger.info(f"Received {sig_name} signal, initiating graceful shutdown...")
            
            # Create shutdown task
            loop = asyncio.get_event_loop()
            loop.create_task(self.shutdown())
        
        # Register handlers
        signal.signal(signal.SIGTERM, handle_signal)
        signal.signal(signal.SIGINT, handle_signal)
        
        logger.info("Signal handlers installed (SIGTERM, SIGINT)")


# Convenience decorator for cleanup functions
def cleanup_on_shutdown(handler: GracefulShutdownHandler):
    """
    Decorator to automatically register a function as a shutdown cleanup handler.
    
    Usage:
        shutdown_handler = GracefulShutdownHandler()
        
        @cleanup_on_shutdown(shutdown_handler)
        async def close_database():
            await db.close()
    """
    def decorator(func: Callable[[], Awaitable[None]]):
        handler.register_cleanup(func)
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        
        return wrapper
    
    return decorator


# Default cleanup functions
async def close_elasticsearch():
    """Close Elasticsearch connections"""
    try:
        from tracardi.service.storage.elastic.interface.client import elastic_close
        await elastic_close()
        logger.info("✓ Elasticsearch connections closed")
    except Exception as e:
        logger.error(f"Error closing Elasticsearch: {e}")


async def close_mysql():
    """Close MySQL connections"""
    try:
        from tracardi.service.storage.mysql.engine import AsyncMySqlEngine
        engine = AsyncMySqlEngine()
        await engine.dispose()
        logger.info("✓ MySQL connections closed")
    except Exception as e:
        logger.error(f"Error closing MySQL: {e}")


async def close_redis():
    """Close Redis connections"""
    try:
        from tracardi.service.storage.redis.driver.redis_client import RedisClient
        redis_client = RedisClient()
        await asyncio.to_thread(redis_client.close)
        logger.info("✓ Redis connections closed")
    except Exception as e:
        logger.error(f"Error closing Redis: {e}")


async def flush_loki_logs():
    """Flush any pending Loki logs"""
    try:
        from tracardi.exceptions.log_handler import loki_handler
        if loki_handler is not None:
            loki_handler.flush()
            logger.info("✓ Loki logs flushed")
    except Exception as e:
        logger.error(f"Error flushing Loki logs: {e}")


def create_default_shutdown_handler(shutdown_timeout: float = None) -> GracefulShutdownHandler:
    """
    Create a shutdown handler with default cleanup functions.
    
    Cleanup functions are registered based on environment configuration:
    - SHUTDOWN_CLOSE_ELASTICSEARCH (default: yes)
    - SHUTDOWN_CLOSE_MYSQL (default: yes)
    - SHUTDOWN_CLOSE_REDIS (default: yes)
    - SHUTDOWN_FLUSH_LOKI (default: yes)
    
    Args:
        shutdown_timeout: Maximum time to wait for shutdown (None = use env config)
        
    Returns:
        Configured GracefulShutdownHandler
    """
    from tracardi.service.health.config import graceful_shutdown_config
    
    # Use env config if not set
    if shutdown_timeout is None:
        shutdown_timeout = graceful_shutdown_config.shutdown_timeout
    
    handler = GracefulShutdownHandler(shutdown_timeout=shutdown_timeout)
    
    # Register cleanups based on configuration
    if graceful_shutdown_config.close_elasticsearch:
        handler.register_cleanup(close_elasticsearch)
    
    if graceful_shutdown_config.close_mysql:
        handler.register_cleanup(close_mysql)
    
    if graceful_shutdown_config.close_redis:
        handler.register_cleanup(close_redis)
    
    if graceful_shutdown_config.flush_loki:
        handler.register_cleanup(flush_loki_logs)
    
    return handler
