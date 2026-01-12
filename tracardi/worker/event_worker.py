"""
Event Processing Worker

Consumes events from message brokers (RabbitMQ/Kafka) and processes them
through the full Tracardi pipeline.

This is a production-ready worker implementation that complements the 
message broker abstraction layer.
"""

import asyncio
import json
import logging
import os
import signal
import sys
from typing import Optional

from tracardi.exceptions.log_handler import get_logger
from tracardi.service.message_broker.broker_config import MessageBrokerConfig
from tracardi.service.tracking.tracker import os_tracker
from tracardi.service.tracker_config import TrackerConfig
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.domain.event_source import EventSource
from tracardi.context import Context, ServerContext

logger = get_logger(__name__)


class EventWorker:
    """
    Base event worker class.
    
    Handles common functionality for all broker types.
    """
    
    def __init__(self, config: MessageBrokerConfig):
        self.config = config
        self.running = True
        self.processed_count = 0
        self.error_count = 0
    
    def setup_signal_handlers(self):
        """Setup graceful shutdown on SIGTERM/SIGINT"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down gracefully...")
            self.running = False
        
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
    
    async def process_event(self, message_data: dict) -> bool:
        """
        Process a single event message.
        
        Args:
            message_data: Dictionary with tracker_config, tracker_payload, source
            
        Returns:
            bool: True if processing succeeded, False otherwise
        """
        try:
            # Extract components
            tracker_config = TrackerConfig(**message_data['tracker_config'])
            tracker_payload = TrackerPayload(**message_data['tracker_payload'])
            source = EventSource(**message_data['source'])
            context_data = message_data.get('context')
            
            # Setup context if provided
            if context_data:
                context = Context(**context_data)
                with ServerContext(context):
                    # Process through full Tracardi pipeline
                    await os_tracker(
                        source=source,
                        tracker_payload=tracker_payload,
                        tracker_config=tracker_config,
                        tracking_start=0
                    )
            else:
                # No context, process directly
                await os_tracker(
                    source=source,
                    tracker_payload=tracker_payload,
                    tracker_config=tracker_config,
                    tracking_start=0
                )
            
            self.processed_count += 1
            
            # Log progress every 100 events
            if self.processed_count % 100 == 0:
                logger.info(
                    f"Worker stats: processed={self.processed_count}, "
                    f"errors={self.error_count}"
                )
            
            return True
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"Failed to process event: {e}", exc_info=True)
            return False


class RabbitMQWorker(EventWorker):
    """
    RabbitMQ consumer worker.
    
    Uses Kombu for RabbitMQ integration.
    """
    
    def __init__(self, config: MessageBrokerConfig):
        super().__init__(config)
        self.connection = None
        self.consumer = None
    
    def start(self):
        """Start RabbitMQ consumer (blocking)"""
        from kombu import Connection, Queue, Exchange
        from kombu.mixins import ConsumerMixin
        
        logger.info(
            f"Starting RabbitMQ worker: {self.config.broker_url}, "
            f"queue: {self.config.topic}"
        )
        
        class Consumer(ConsumerMixin):
            def __init__(self, connection, worker, queue_name, exchange_type, routing_key):
                self.connection = connection
                self.worker = worker
                
                # Setup exchange and queue
                exchange = Exchange(
                    queue_name,
                    type=exchange_type,
                    durable=self.worker.config.durable
                )
                self.queue = Queue(
                    queue_name,
                    exchange=exchange,
                    routing_key=routing_key,
                    durable=self.worker.config.durable
                )
            
            def get_consumers(self, Consumer, channel):
                return [Consumer(
                    queues=[self.queue],
                    callbacks=[self.on_message],
                    prefetch_count=10  # Process 10 messages at a time
                )]
            
            def on_message(self, body, message):
                """Process single message"""
                try:
                    # Deserialize
                    data = json.loads(body) if isinstance(body, (str, bytes)) else body
                    
                    # Process event
                    success = asyncio.run(self.worker.process_event(data))
                    
                    if success:
                        # Acknowledge success
                        message.ack()
                    else:
                        # On error, requeue once, then reject
                        if message.delivery_info.get('redelivered'):
                            logger.error("Message failed after retry, rejecting")
                            message.reject()  # Send to DLQ if configured
                        else:
                            message.requeue()  # Retry once
                
                except Exception as e:
                    logger.error(f"Error processing message: {e}", exc_info=True)
                    message.reject()
            
            def should_stop(self):
                """Check if should stop consuming"""
                return not self.worker.running
        
        # Setup connection
        self.connection = Connection(self.config.broker_url)
        
        # Create consumer
        consumer = Consumer(
            self.connection,
            self,
            self.config.topic,
            self.config.exchange_type,
            self.config.routing_key
        )
        
        # Setup signal handlers
        self.setup_signal_handlers()
        
        try:
            # Start consuming (blocking)
            consumer.run()
        except KeyboardInterrupt:
            logger.info("Worker interrupted")
        finally:
            logger.info(
                f"Worker stopped. Processed: {self.processed_count}, "
                f"Errors: {self.error_count}"
            )


class KafkaWorker(EventWorker):
    """
    Kafka consumer worker.
    
    Uses aiokafka for async Kafka integration.
    """
    
    def __init__(self, config: MessageBrokerConfig):
        super().__init__(config)
        self.consumer = None
    
    async def start(self):
        """Start Kafka consumer"""
        from aiokafka import AIOKafkaConsumer
        
        logger.info(
            f"Starting Kafka worker: {self.config.broker_url}, "
            f"topic: {self.config.topic}"
        )
        
        # Parse bootstrap servers
        bootstrap_servers = self.config.broker_url
        if bootstrap_servers.startswith('kafka://'):
            bootstrap_servers = bootstrap_servers.replace('kafka://', '')
        
        # Create consumer
        consumer_config = {
            'bootstrap_servers': bootstrap_servers,
            'group_id': os.getenv('TRACARDI_BROKER_GROUP_ID', 'tracardi-consumer-group'),
            'value_deserializer': lambda m: json.loads(m.decode('utf-8')),
            'auto_offset_reset': 'earliest',
            'enable_auto_commit': False,  # Manual commit for reliability
            'max_poll_records': 10
        }
        
        # Add SASL if credentials provided
        if self.config.username:
            consumer_config.update({
                'security_protocol': 'SASL_SSL',
                'sasl_mechanism': 'PLAIN',
                'sasl_plain_username': self.config.username,
                'sasl_plain_password': self.config.password
            })
        
        self.consumer = AIOKafkaConsumer(
            self.config.topic,
            **consumer_config
        )
        
        # Start consumer
        await self.consumer.start()
        logger.info("✓ Kafka consumer started")
        
        # Setup signal handlers
        self.setup_signal_handlers()
        
        try:
            # Consume loop
            async for message in self.consumer:
                if not self.running:
                    break
                
                # Process event
                success = await self.process_event(message.value)
                
                # Commit offset after processing
                await self.consumer.commit()
                
                if not success:
                    logger.warning(f"Failed to process offset {message.offset}, moving on")
        
        except Exception as e:
            logger.error(f"Consumer error: {e}", exc_info=True)
        
        finally:
            # Stop consumer
            await self.consumer.stop()
            logger.info(
                f"Worker stopped. Processed: {self.processed_count}, "
                f"Errors: {self.error_count}"
            )


def main():
    """
    Main entry point for event worker.
    
    Automatically selects the correct worker based on TRACARDI_MESSAGE_BROKER.
    """
    # Load configuration
    config = MessageBrokerConfig.from_env()
    
    if not config.broker_type:
        logger.error("TRACARDI_MESSAGE_BROKER not set!")
        sys.exit(1)
    
    logger.info(f"Starting Tracardi event worker: {config.broker_type}")
    
    # Create appropriate worker
    if config.broker_type == 'rabbitmq':
        worker = RabbitMQWorker(config)
        worker.start()  # Blocking
    
    elif config.broker_type == 'kafka':
        worker = KafkaWorker(config)
        asyncio.run(worker.start())  # Async
    
    else:
        logger.error(f"Unsupported broker type: {config.broker_type}")
        logger.info("Supported: rabbitmq, kafka")
        sys.exit(1)


if __name__ == '__main__':
    main()
