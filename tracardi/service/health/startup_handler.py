"""
Startup handlers for initializing and warming up services.
"""
import asyncio
import logging
from typing import Callable, List, Awaitable

logger = logging.getLogger(__name__)


class StartupHandler:
    """
    Manages application startup and service initialization.
    
    This handler:
    1. Waits for dependencies to be available
    2. Runs initialization tasks
    3. Warms up caches
    4. Validates configuration
    
    Usage:
        startup_handler = StartupHandler()
        startup_handler.register_init(init_database)
        await startup_handler.run()
    """
    
    def __init__(self, max_retries: int = 10, retry_delay: float = 2.0):
        """
        Initialize startup handler.
        
        Args:
            max_retries: Maximum retries for dependency checks
            retry_delay: Delay between retries in seconds
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._init_functions: List[Callable[[], Awaitable[None]]] = []
    
    def register_init(self, init_fn: Callable[[], Awaitable[None]]):
        """Register an initialization function"""
        self._init_functions.append(init_fn)
        logger.info(f"Registered startup function: {init_fn.__name__}")
    
    async def wait_for_dependencies(self, timeout: float = 60.0):
        """
        Wait for all critical dependencies to be available.
        
        Args:
            timeout: Maximum time to wait for dependencies
        """
        from tracardi.service.health import HealthCheckService
        
        logger.info("Waiting for dependencies...")
        start_time = asyncio.get_event_loop().time()
        
        for attempt in range(1, self.max_retries + 1):
            try:
                # Check readiness
                health = await HealthCheckService.readiness(timeout=5.0)
                
                if health.is_ready():
                    logger.info("✓ All dependencies are ready")
                    return
                
                # Log which components are not ready
                for name, component in health.components.items():
                    if component.status != "healthy":
                        logger.warning(f"  {name}: {component.status} - {component.message}")
                
            except Exception as e:
                logger.warning(f"Dependency check failed (attempt {attempt}/{self.max_retries}): {e}")
            
            # Check timeout
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed >= timeout:
                raise TimeoutError(f"Dependencies not ready after {timeout}s")
            
            # Wait before retry
            logger.info(f"Retrying in {self.retry_delay}s...")
            await asyncio.sleep(self.retry_delay)
        
        raise RuntimeError(f"Dependencies not ready after {self.max_retries} attempts")
    
    async def run(self):
        """
        Run all startup initialization tasks.
        
        This method runs all registered initialization functions in order.
        """
        logger.info("=" * 60)
        logger.info("Application startup initiated")
        logger.info("=" * 60)
        
        # Wait for dependencies first
        try:
            await self.wait_for_dependencies()
        except Exception as e:
            logger.error(f"Failed to wait for dependencies: {e}")
            raise
        
        # Run initialization functions
        for init_fn in self._init_functions:
            try:
                logger.info(f"Running initialization: {init_fn.__name__}")
                await init_fn()
                logger.info(f"✓ {init_fn.__name__} completed")
            except Exception as e:
                logger.error(f"Initialization failed: {init_fn.__name__}: {e}", exc_info=True)
                raise
        
        logger.info("=" * 60)
        logger.info("Application startup completed")
        logger.info("=" * 60)


# Default startup functions
async def warm_up_elasticsearch():
    """Warm up Elasticsearch connections"""
    try:
        from tracardi.service.storage.elastic.interface.raw import health
        await health()
        logger.info("✓ Elasticsearch warmed up")
    except Exception as e:
        logger.error(f"Failed to warm up Elasticsearch: {e}")
        raise


async def warm_up_mysql():
    """Warm up MySQL connections"""
    try:
        from tracardi.service.storage.mysql.engine import AsyncMySqlEngine
        engine = AsyncMySqlEngine()
        async with engine.get_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT 1")
        logger.info("✓ MySQL warmed up")
    except Exception as e:
        logger.error(f"Failed to warm up MySQL: {e}")
        raise


async def warm_up_redis():
    """Warm up Redis connections"""
    try:
        from tracardi.service.storage.redis.driver.redis_client import RedisClient
        redis_client = RedisClient()
        await asyncio.to_thread(redis_client.ping)
        logger.info("✓ Redis warmed up")
    except Exception as e:
        logger.error(f"Failed to warm up Redis: {e}")
        raise


def create_default_startup_handler() -> StartupHandler:
    """
    Create a startup handler with default initialization functions.
    
    Warmup functions are registered based on environment configuration:
    - STARTUP_WARMUP_ELASTICSEARCH (default: yes)
    - STARTUP_WARMUP_MYSQL (default: yes)
    - STARTUP_WARMUP_REDIS (default: yes)
    """
    from tracardi.service.health.config import startup_config
    
    handler = StartupHandler(
        max_retries=startup_config.wait_max_retries,
        retry_delay=startup_config.wait_retry_delay
    )
    
    # Register warmups based on configuration
    if startup_config.warm_up_elasticsearch:
        handler.register_init(warm_up_elasticsearch)
    
    if startup_config.warm_up_mysql:
        handler.register_init(warm_up_mysql)
    
    if startup_config.warm_up_redis:
        handler.register_init(warm_up_redis)
    
    return handler
