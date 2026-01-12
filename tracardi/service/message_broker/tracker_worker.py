"""
Tracker Worker with Message Broker Support

Provides async event processing via message brokers (RabbitMQ, Kafka, Pulsar).
"""

import json
from typing import Any, Dict

from tracardi.domain.event_source import EventSource
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.service.tracker_config import TrackerConfig
from tracardi.service.message_broker import get_message_broker
from tracardi.exceptions.log_handler import get_logger

logger = get_logger(__name__)


async def run_message_broker_tracker_worker(
    tracker_config: TrackerConfig,
    tracker_payload: TrackerPayload,
    source: EventSource
) -> Dict[str, Any]:
    """
    Process tracker payload via message broker.
    
    Publishes event to configured message broker (RabbitMQ/Kafka/Pulsar)
    for async processing by worker.
    
    Args:
        tracker_config: Tracker configuration
        tracker_payload: Incoming tracker payload with events
        source: Validated event source
        
    Returns:
        dict: Empty response (processing is async)
        
    Raises:
        RuntimeError: If broker connection or publish fails
    """
    try:
        # Get configured broker instance
        broker = get_message_broker()
        
        # Ensure connection
        if not broker.is_connected():
            await broker.connect()
        
        # Prepare message payload
        message = {
            'tracker_config': tracker_config.model_dump() if hasattr(tracker_config, 'model_dump') else tracker_config.__dict__,
            'tracker_payload': tracker_payload.model_dump() if hasattr(tracker_payload, 'model_dump') else tracker_payload.dict(),
            'source': source.model_dump() if hasattr(source, 'model_dump') else source.dict()
        }
        
        # Publish to broker
        await broker.publish(message)
        
        logger.info(
            f"Event published to message broker ({broker.config.broker_type}) "
            f"for async processing. Events: {len(tracker_payload.events)}, "
            f"Profile: {tracker_payload.profile.id if tracker_payload.profile else 'None'}"
        )
        
        # Return empty response - actual processing happens in worker
        return {}
        
    except Exception as e:
        logger.error(
            f"Failed to publish event to message broker: {e}",
            exc_info=True
        )
        raise RuntimeError(f"Message broker publish failed: {e}")


async def ensure_broker_connection():
    """
    Ensure message broker connection is established.
    
    Call this during application startup to initialize broker connection.
    """
    try:
        broker = get_message_broker()
        if not broker.is_connected():
            await broker.connect()
            logger.info(f"✓ Message broker ({broker.config.broker_type}) connected and ready")
        return True
    except Exception as e:
        logger.error(f"Failed to connect to message broker: {e}")
        return False


async def disconnect_broker():
    """
    Disconnect from message broker.
    
    Call this during application shutdown for graceful cleanup.
    """
    try:
        broker = get_message_broker()
        if broker.is_connected():
            await broker.disconnect()
            logger.info("✓ Message broker disconnected")
    except Exception as e:
        logger.error(f"Error disconnecting from message broker: {e}")
