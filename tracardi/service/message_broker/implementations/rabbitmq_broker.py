"""
RabbitMQ Message Broker Implementation

Uses Kombu for RabbitMQ integration.
"""

import asyncio
import json
import logging
from typing import Dict, Any

from kombu import Connection, Exchange, Queue, Producer

from tracardi.service.message_broker.base_broker import MessageBroker
from tracardi.exceptions.log_handler import get_logger

logger = get_logger(__name__)


class RabbitMQBroker(MessageBroker):
    """
    RabbitMQ implementation of MessageBroker.
    
    Uses Kombu library for connection management and message publishing.
    """
    
    def __init__(self, config):
        super().__init__(config)
        self._connection: Connection = None
        self._exchange: Exchange = None
        self._queue: Queue = None
        self._producer: Producer = None
    
    def _sync_connect(self) -> None:
        """Synchronous connection setup"""
        # Create connection
        connection_url = self.config.broker_url
        
        # Add credentials if provided
        if self.config.username and self.config.password:
            # Parse URL and inject credentials
            if '://' in connection_url:
                protocol, rest = connection_url.split('://', 1)
                connection_url = f"{protocol}://{self.config.username}:{self.config.password}@{rest}"
        
        self._connection = Connection(
            connection_url,
            connect_timeout=self.config.timeout
        )
        
        # Ensure connection is established
        self._connection.connect()
        
        # Create channel
        channel = self._connection.channel()
        
        # Create exchange
        self._exchange = Exchange(
            self.config.topic,
            type=self.config.exchange_type,
            durable=self.config.durable,
            channel=channel
        )
        
        # Create queue
        self._queue = Queue(
            self.config.topic,
            exchange=self._exchange,
            routing_key=self.config.routing_key,
            durable=self.config.durable,
            channel=channel
        )
        
        # Bind and declare
        self._queue.maybe_bind(self._connection)
        self._queue.declare()
        
        # Create producer
        self._producer = Producer(
            exchange=self._exchange,
            channel=channel,
            routing_key=self._queue.routing_key,
            serializer='json',
            compression=None,
            auto_declare=True
        )
        
        self._client = self._connection  # Mark as connected
        
        logger.info(
            f"✓ Connected to RabbitMQ at {self.config.broker_url}, "
            f"topic: {self.config.topic}"
        )
    
    async def connect(self) -> None:
        """
        Establish connection to RabbitMQ.
        
        Creates connection, exchange, queue, and producer.
        Runs sync Kombu operations in thread pool to avoid blocking event loop.
        """
        try:
            # Run sync connection in thread pool to avoid blocking
            await asyncio.to_thread(self._sync_connect)
            
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise ConnectionError(f"RabbitMQ connection failed: {e}")
    
    def _sync_disconnect(self) -> None:
        """Synchronous disconnection"""
        if self._connection:
            self._connection.release()
            self._connection = None
            self._client = None
            self._producer = None
            logger.info("✓ Disconnected from RabbitMQ")
    
    async def disconnect(self) -> None:
        """
        Close RabbitMQ connection.
        Runs sync Kombu operations in thread pool to avoid blocking event loop.
        """
        try:
            # Run sync disconnect in thread pool
            await asyncio.to_thread(self._sync_disconnect)
        except Exception as e:
            logger.error(f"Error disconnecting from RabbitMQ: {e}")
    
    def _sync_publish(self, message: Dict[str, Any]) -> None:
        """Synchronous message publishing"""
        self._producer.publish(
            message,
            retry=True,
            retry_policy={
                'interval_start': 0,
                'interval_step': 2,
                'interval_max': 30,
                'max_retries': 3,
            }
        )
        logger.debug(f"Published message to RabbitMQ topic: {self.config.topic}")
    
    async def publish(self, message: Dict[str, Any]) -> None:
        """
        Publish message to RabbitMQ queue.
        
        Args:
            message: Dictionary containing tracker payload
            
        Raises:
            RuntimeError: If not connected
            PublishError: If publishing fails
        """
        if not self.is_connected():
            raise RuntimeError("Not connected to RabbitMQ. Call connect() first.")
        
        try:
            # Run sync publish in thread pool to avoid blocking
            await asyncio.to_thread(self._sync_publish, message)
            
        except Exception as e:
            logger.error(f"Failed to publish message to RabbitMQ: {e}")
            raise RuntimeError(f"RabbitMQ publish failed: {e}")
    
    async def health_check(self) -> bool:
        """
        Check RabbitMQ connection health.
        
        Returns:
            bool: True if healthy, False otherwise
        """
        try:
            if not self.is_connected():
                return False
            
            # Check if connection is alive
            return self._connection.connected
            
        except Exception as e:
            logger.error(f"RabbitMQ health check failed: {e}")
            return False
