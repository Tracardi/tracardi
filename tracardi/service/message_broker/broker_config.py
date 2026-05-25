"""
Message Broker Configuration

Environment Variables:
    TRACARDI_MESSAGE_BROKER: Broker type (rabbitmq, kafka, pulsar)
    TRACARDI_BROKER_URL: Broker connection URL
    TRACARDI_BROKER_TOPIC: Topic/queue name for events
    TRACARDI_BROKER_USERNAME: Authentication username (optional)
    TRACARDI_BROKER_PASSWORD: Authentication password (optional)
    TRACARDI_BROKER_TIMEOUT: Connection timeout in seconds (default: 30)
"""

import os
from typing import Optional
from pydantic import BaseModel, field_validator


class MessageBrokerConfig(BaseModel):
    """
    Configuration for message broker connection.
    """
    
    broker_type: str = 'rabbitmq'  # rabbitmq, kafka, pulsar
    broker_url: str = 'amqp://localhost:5672//'
    topic: str = 'tracardi-events'
    username: Optional[str] = None
    password: Optional[str] = None
    timeout: int = 30
    
    # RabbitMQ specific
    virtual_host: Optional[str] = None
    exchange_type: str = 'direct'
    routing_key: str = 'events'
    durable: bool = True
    
    # Kafka specific
    group_id: Optional[str] = 'tracardi-consumer-group'
    
    # Pulsar specific
    listener_name: Optional[str] = None
    
    @field_validator('broker_type')
    @classmethod
    def validate_broker_type(cls, value):
        valid_brokers = ['rabbitmq', 'kafka', 'pulsar']
        if value not in valid_brokers:
            raise ValueError(
                f"Invalid broker_type: {value}. "
                f"Must be one of: {', '.join(valid_brokers)}"
            )
        return value
    
    @classmethod
    def from_env(cls):
        """Load configuration from environment variables"""
        env = os.environ
        
        broker_type = env.get('TRACARDI_MESSAGE_BROKER', 'rabbitmq').lower()
        
        # Set default URL based on broker type
        default_urls = {
            'rabbitmq': 'amqp://localhost:5672//',
            'kafka': 'localhost:9092',
            'pulsar': 'pulsar://localhost:6650'
        }
        
        return cls(
            broker_type=broker_type,
            broker_url=env.get('TRACARDI_BROKER_URL', default_urls.get(broker_type, '')),
            topic=env.get('TRACARDI_BROKER_TOPIC', 'tracardi-events'),
            username=env.get('TRACARDI_BROKER_USERNAME'),
            password=env.get('TRACARDI_BROKER_PASSWORD'),
            timeout=int(env.get('TRACARDI_BROKER_TIMEOUT', '30')),
            virtual_host=env.get('TRACARDI_BROKER_VIRTUAL_HOST'),
            exchange_type=env.get('TRACARDI_BROKER_EXCHANGE_TYPE', 'direct'),
            routing_key=env.get('TRACARDI_BROKER_ROUTING_KEY', 'events'),
            durable=env.get('TRACARDI_BROKER_DURABLE', 'yes').lower() in ('yes', 'true', '1'),
            group_id=env.get('TRACARDI_BROKER_GROUP_ID', 'tracardi-consumer-group'),
            listener_name=env.get('TRACARDI_BROKER_LISTENER_NAME')
        )


# Global config instance
# Lazy initialization to avoid errors if broker not configured
try:
    message_broker_config = MessageBrokerConfig.from_env()
except Exception as e:
    # If env vars invalid, use default (won't be used unless queue is explicitly enabled)
    import logging
    logging.warning(f"Failed to load message broker config: {e}. Using defaults.")
    message_broker_config = MessageBrokerConfig()
