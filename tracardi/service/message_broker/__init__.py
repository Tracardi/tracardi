"""
Message Broker Abstraction Layer for Tracardi

Supports multiple message brokers for event queue processing:
- RabbitMQ (via Kombu)
- Apache Kafka (via aiokafka)
- Apache Pulsar (commercial)

Broker selection via environment variable:
    TRACARDI_MESSAGE_BROKER=rabbitmq|kafka|pulsar
"""

from .broker_factory import get_message_broker
from .broker_config import message_broker_config

__all__ = [
    'get_message_broker',
    'message_broker_config'
]
