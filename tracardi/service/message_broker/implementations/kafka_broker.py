"""
Kafka Message Broker Implementation

Uses aiokafka for Kafka integration.
"""

import json
import logging
from typing import Dict, Any

from tracardi.service.message_broker.base_broker import MessageBroker
from tracardi.exceptions.log_handler import get_logger

logger = get_logger(__name__)


class KafkaBroker(MessageBroker):
    """
    Kafka implementation of MessageBroker.
    
    Uses aiokafka library for async Kafka operations.
    """
    
    def __init__(self, config):
        super().__init__(config)
        self._producer = None
    
    async def connect(self) -> None:
        """
        Establish connection to Kafka.
        """
        try:
            from aiokafka import AIOKafkaProducer
            
            # Parse bootstrap servers
            bootstrap_servers = self.config.broker_url
            if not bootstrap_servers.startswith('kafka://'):
                bootstrap_servers = bootstrap_servers.replace('kafka://', '')
            
            # Create producer
            self._producer = AIOKafkaProducer(
                bootstrap_servers=bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                compression_type='gzip',
                request_timeout_ms=self.config.timeout * 1000,
                # Add SASL if credentials provided
                security_protocol='SASL_SSL' if self.config.username else 'PLAINTEXT',
                sasl_mechanism='PLAIN' if self.config.username else None,
                sasl_plain_username=self.config.username,
                sasl_plain_password=self.config.password
            )
            
            # Start producer
            await self._producer.start()
            
            self._client = self._producer  # Mark as connected
            
            logger.info(
                f"✓ Connected to Kafka at {self.config.broker_url}, "
                f"topic: {self.config.topic}"
            )
            
        except ImportError:
            raise ImportError(
                "aiokafka is not installed. "
                "Install it with: pip install aiokafka"
            )
        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            raise ConnectionError(f"Kafka connection failed: {e}")
    
    async def disconnect(self) -> None:
        """
        Close Kafka connection with graceful flush.
        
        Ensures all pending messages are sent before disconnecting.
        """
        try:
            if self._producer:
                # Flush any pending messages before stopping
                try:
                    await self._producer.flush()
                    logger.debug("✓ Kafka messages flushed")
                except Exception as flush_error:
                    logger.warning(f"Error flushing Kafka messages: {flush_error}")
                
                # Stop producer gracefully
                await self._producer.stop()
                self._producer = None
                self._client = None
                logger.info("✓ Disconnected from Kafka")
        except Exception as e:
            logger.error(f"Error disconnecting from Kafka: {e}")
    
    async def publish(self, message: Dict[str, Any]) -> None:
        """
        Publish message to Kafka topic with timeout.
        
        Args:
            message: Dictionary containing tracker payload
            
        Raises:
            RuntimeError: If not connected
            PublishError: If publishing fails
        """
        if not self.is_connected():
            raise RuntimeError("Not connected to Kafka. Call connect() first.")
        
        try:
            import asyncio
            
            # Send message with timeout to prevent indefinite hanging
            send_task = self._producer.send_and_wait(
                self.config.topic,
                value=message
            )
            
            # Apply timeout (default: config timeout + 5 seconds buffer)
            timeout = self.config.timeout + 5
            await asyncio.wait_for(send_task, timeout=timeout)
            
            logger.debug(f"Published message to Kafka topic: {self.config.topic}")
            
        except asyncio.TimeoutError:
            logger.error(f"Kafka publish timeout after {timeout}s")
            raise RuntimeError(f"Kafka publish timeout after {timeout}s")
        except Exception as e:
            logger.error(f"Failed to publish message to Kafka: {e}")
            raise RuntimeError(f"Kafka publish failed: {e}")
    
    async def health_check(self) -> bool:
        """
        Check Kafka connection health.
        
        Returns:
            bool: True if healthy, False otherwise
        """
        try:
            if not self.is_connected():
                return False
            
            # Kafka producer doesn't have a direct health check
            # We assume it's healthy if connected
            return True
            
        except Exception as e:
            logger.error(f"Kafka health check failed: {e}")
            return False
