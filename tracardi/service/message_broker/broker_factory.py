"""
Message Broker Factory

Creates appropriate broker instance based on configuration.
"""

import logging
from typing import Optional

from tracardi.service.message_broker.base_broker import MessageBroker
from tracardi.service.message_broker.broker_config import message_broker_config
from tracardi.service.license import License
from tracardi.exceptions.log_handler import get_logger

logger = get_logger(__name__)

# Singleton instance
_broker_instance: Optional[MessageBroker] = None


def get_message_broker() -> MessageBroker:
    """
    Get message broker instance based on configuration.
    
    Returns singleton instance for the configured broker type.
    
    Supported brokers:
        - rabbitmq: RabbitMQ via Kombu (open source)
        - kafka: Apache Kafka via aiokafka (open source)
        - pulsar: Apache Pulsar (requires commercial license)
    
    Returns:
        MessageBroker: Configured broker instance
        
    Raises:
        ValueError: If broker type is unknown or not available
        ImportError: If required dependencies are missing
    """
    global _broker_instance
    
    # Return existing instance if already created
    if _broker_instance is not None:
        return _broker_instance
    
    broker_type = message_broker_config.broker_type.lower()
    
    logger.info(f"Initializing message broker: {broker_type}")
    
    try:
        if broker_type == 'rabbitmq':
            from tracardi.service.message_broker.implementations.rabbitmq_broker import RabbitMQBroker
            _broker_instance = RabbitMQBroker(message_broker_config)
            logger.info("✓ RabbitMQ broker initialized")
            
        elif broker_type == 'kafka':
            from tracardi.service.message_broker.implementations.kafka_broker import KafkaBroker
            _broker_instance = KafkaBroker(message_broker_config)
            logger.info("✓ Kafka broker initialized")
            
        elif broker_type == 'pulsar':
            # Pulsar requires commercial license
            if not License.has_license():
                raise ValueError(
                    "Apache Pulsar broker requires Tracardi commercial license. "
                    "Use 'rabbitmq' or 'kafka' for open source deployments."
                )
            
            # Import commercial Pulsar implementation
            try:
                from com_tracardi.service.message_broker.pulsar_broker import PulsarBroker
                _broker_instance = PulsarBroker(message_broker_config)
                logger.info("✓ Pulsar broker initialized (commercial)")
            except ImportError:
                raise ImportError(
                    "Commercial Pulsar broker not found. "
                    "Ensure com_tracardi package is installed."
                )
        
        else:
            raise ValueError(
                f"Unknown broker type: {broker_type}. "
                f"Supported: rabbitmq, kafka, pulsar"
            )
        
        return _broker_instance
        
    except ImportError as e:
        logger.error(f"Failed to import broker implementation: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to initialize broker: {e}")
        raise


def reset_broker_instance():
    """
    Reset singleton broker instance.
    
    Useful for testing or reconfiguration.
    """
    global _broker_instance
    _broker_instance = None
