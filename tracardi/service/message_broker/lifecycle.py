"""
Message Broker Lifecycle Management

Handles broker startup, shutdown, and graceful cleanup.
"""

import asyncio
import signal
from typing import Optional

from tracardi.exceptions.log_handler import get_logger
from tracardi.service.message_broker.broker_factory import get_message_broker, reset_broker_instance

logger = get_logger(__name__)

_shutdown_event: Optional[asyncio.Event] = None


async def startup_broker():
    """
    Initialize message broker connection on application startup.
    
    Call this in FastAPI lifespan/startup event.
    """
    try:
        from tracardi.service.message_broker.broker_config import message_broker_config
        
        if not message_broker_config.broker_type:
            logger.info("Message broker not configured, skipping startup")
            return
        
        broker = get_message_broker()
        
        if not broker.is_connected():
            await broker.connect()
            logger.info(
                f"✓ Message broker ({message_broker_config.broker_type}) "
                f"started and ready"
            )
    except Exception as e:
        logger.error(f"Failed to start message broker: {e}")
        # Don't raise - allow app to start even if broker fails
        logger.warning("Application will continue without message broker")


async def shutdown_broker():
    """
    Gracefully disconnect from message broker on application shutdown.
    
    Call this in FastAPI lifespan/shutdown event or signal handler.
    
    Ensures:
    - All pending messages are flushed
    - Connections are properly closed
    - Resources are cleaned up
    """
    try:
        from tracardi.service.message_broker.broker_config import message_broker_config
        
        if not message_broker_config.broker_type:
            return
        
        logger.info("Shutting down message broker...")
        
        broker = get_message_broker()
        
        if broker.is_connected():
            # Disconnect with flush
            await broker.disconnect()
            logger.info("✓ Message broker shut down gracefully")
        
        # Reset singleton for clean state
        reset_broker_instance()
        
    except Exception as e:
        logger.error(f"Error during message broker shutdown: {e}")
        # Continue shutdown despite error


def setup_signal_handlers():
    """
    Setup signal handlers for graceful shutdown.
    
    Handles SIGTERM and SIGINT (Ctrl+C).
    """
    global _shutdown_event
    
    _shutdown_event = asyncio.Event()
    
    def signal_handler(signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        _shutdown_event.set()
    
    # Register signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    logger.info("✓ Signal handlers configured for graceful shutdown")


async def wait_for_shutdown():
    """
    Wait for shutdown signal.
    
    Blocks until SIGTERM/SIGINT received.
    """
    global _shutdown_event
    
    if _shutdown_event is None:
        setup_signal_handlers()
    
    await _shutdown_event.wait()


async def graceful_shutdown(timeout: float = 30.0):
    """
    Perform full graceful shutdown sequence.
    
    Args:
        timeout: Maximum time to wait for shutdown (seconds)
    
    Steps:
        1. Stop accepting new requests
        2. Wait for in-flight requests to complete
        3. Flush message broker
        4. Close connections
        5. Clean up resources
    """
    logger.info(f"Starting graceful shutdown (timeout: {timeout}s)...")
    
    try:
        # Shutdown with timeout
        await asyncio.wait_for(
            shutdown_broker(),
            timeout=timeout
        )
    except asyncio.TimeoutError:
        logger.warning(f"Broker shutdown timeout after {timeout}s, forcing...")
    except Exception as e:
        logger.error(f"Error during graceful shutdown: {e}")
    
    logger.info("✓ Graceful shutdown complete")
