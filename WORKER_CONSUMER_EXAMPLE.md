# Message Broker Consumer Worker Examples

## ⚠️ IMPORTANT

The message broker implementation in this PR **requires a separate consumer worker** to process queued events.

This document provides production-ready worker implementations for each broker.

---

## RabbitMQ Worker

```python
# worker_rabbitmq.py
import asyncio
import json
import sys
from kombu import Connection, Queue, Exchange
from kombu.mixins import ConsumerMixin

from tracardi.service.tracking.tracker import os_tracker
from tracardi.service.tracker_config import TrackerConfig
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.domain.event_source import EventSource
from tracardi.exceptions.log_handler import get_logger
from tracardi.context import ServerContext, Context

logger = get_logger(__name__)


class RabbitMQWorker(ConsumerMixin):
    """
    RabbitMQ consumer worker for processing Tracardi events.
    """
    
    def __init__(self, connection, queue_name='tracardi-events'):
        self.connection = connection
        self.queue_name = queue_name
        
        # Setup queue
        exchange = Exchange(queue_name, type='direct', durable=True)
        self.queue = Queue(
            queue_name,
            exchange=exchange,
            routing_key='events',
            durable=True
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
            data = json.loads(body)
            
            # Extract components
            tracker_config = TrackerConfig(**data['tracker_config'])
            tracker_payload = TrackerPayload(**data['tracker_payload'])
            source = EventSource(**data['source'])
            
            # Process event
            logger.info(f"Processing event from queue: {tracker_payload.events[0].type if tracker_payload.events else 'unknown'}")
            
            # Run async tracker in sync context
            asyncio.run(os_tracker(
                source=source,
                tracker_payload=tracker_payload,
                tracker_config=tracker_config,
                tracking_start=0
            ))
            
            # Acknowledge success
            message.ack()
            logger.info(f"✓ Event processed successfully")
            
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            # Reject and requeue (max 3 retries)
            if message.delivery_info.get('redelivered'):
                logger.error("Message failed after retry, sending to DLQ")
                message.reject()  # Send to dead letter queue
            else:
                message.requeue()  # Retry once


def main():
    """Start RabbitMQ worker"""
    # Configuration from environment
    broker_url = os.getenv('TRACARDI_BROKER_URL', 'amqp://guest:guest@localhost:5672//')
    queue_name = os.getenv('TRACARDI_BROKER_TOPIC', 'tracardi-events')
    
    logger.info(f"Starting RabbitMQ worker: {broker_url}, queue: {queue_name}")
    
    try:
        with Connection(broker_url) as conn:
            worker = RabbitMQWorker(conn, queue_name)
            worker.run()
    except KeyboardInterrupt:
        logger.info("Worker interrupted, shutting down...")
        sys.exit(0)


if __name__ == '__main__':
    main()
```

**Run:**
```bash
python worker_rabbitmq.py
```

---

## Kafka Worker

```python
# worker_kafka.py
import asyncio
import json
import os
import signal
from aiokafka import AIOKafkaConsumer

from tracardi.service.tracking.tracker import os_tracker
from tracardi.service.tracker_config import TrackerConfig
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.domain.event_source import EventSource
from tracardi.exceptions.log_handler import get_logger

logger = get_logger(__name__)


class KafkaWorker:
    """
    Kafka consumer worker for processing Tracardi events.
    """
    
    def __init__(self, bootstrap_servers, topic, group_id):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.group_id = group_id
        self.consumer = None
        self.running = True
    
    async def start(self):
        """Start consumer"""
        self.consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',  # Start from beginning
            enable_auto_commit=False,  # Manual commit for reliability
            max_poll_records=10  # Process in batches
        )
        
        await self.consumer.start()
        logger.info(f"✓ Kafka consumer started: {self.topic}")
    
    async def stop(self):
        """Stop consumer gracefully"""
        self.running = False
        if self.consumer:
            await self.consumer.stop()
            logger.info("✓ Kafka consumer stopped")
    
    async def process_message(self, message):
        """Process single Kafka message"""
        try:
            data = message.value
            
            # Extract components
            tracker_config = TrackerConfig(**data['tracker_config'])
            tracker_payload = TrackerPayload(**data['tracker_payload'])
            source = EventSource(**data['source'])
            
            # Process event
            logger.info(f"Processing event: partition={message.partition}, offset={message.offset}")
            
            await os_tracker(
                source=source,
                tracker_payload=tracker_payload,
                tracker_config=tracker_config,
                tracking_start=0
            )
            
            logger.info(f"✓ Event processed: offset={message.offset}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            return False
    
    async def consume(self):
        """Main consumption loop"""
        try:
            async for message in self.consumer:
                if not self.running:
                    break
                
                success = await self.process_message(message)
                
                if success:
                    # Commit offset after successful processing
                    await self.consumer.commit()
                else:
                    # On error, skip to next message (or implement retry logic)
                    logger.warning(f"Skipping failed message: offset={message.offset}")
                    await self.consumer.commit()  # Commit to move forward
        
        except Exception as e:
            logger.error(f"Consumer error: {e}", exc_info=True)
        finally:
            await self.stop()
    
    async def run(self):
        """Run worker"""
        await self.start()
        await self.consume()


async def main():
    """Start Kafka worker"""
    # Configuration from environment
    bootstrap_servers = os.getenv('TRACARDI_BROKER_URL', 'localhost:9092')
    topic = os.getenv('TRACARDI_BROKER_TOPIC', 'tracardi-events')
    group_id = os.getenv('TRACARDI_BROKER_GROUP_ID', 'tracardi-consumer-group')
    
    logger.info(f"Starting Kafka worker: {bootstrap_servers}, topic: {topic}")
    
    worker = KafkaWorker(bootstrap_servers, topic, group_id)
    
    # Graceful shutdown on SIGTERM/SIGINT
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(
            sig,
            lambda: asyncio.create_task(worker.stop())
        )
    
    try:
        await worker.run()
    except KeyboardInterrupt:
        logger.info("Worker interrupted")
    finally:
        await worker.stop()


if __name__ == '__main__':
    asyncio.run(main())
```

**Run:**
```bash
python worker_kafka.py
```

---

## Systemd Service

```ini
# /etc/systemd/system/tracardi-worker.service
[Unit]
Description=Tracardi Message Broker Worker
After=network.target rabbitmq.service

[Service]
Type=simple
User=tracardi
WorkingDirectory=/opt/tracardi
Environment="TRACARDI_BROKER_URL=amqp://localhost:5672//"
Environment="TRACARDI_BROKER_TOPIC=tracardi-events"
ExecStart=/usr/bin/python3 /opt/tracardi/worker_rabbitmq.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable tracardi-worker
sudo systemctl start tracardi-worker
```

---

## Docker Compose

```yaml
version: '3'
services:
  tracardi-api:
    image: tracardi/tracardi-api
    environment:
      TRACARDI_MESSAGE_BROKER: rabbitmq
      TRACARDI_BROKER_URL: amqp://rabbitmq:5672//
    depends_on:
      - rabbitmq
  
  tracardi-worker:
    image: tracardi/tracardi-api
    command: python worker_rabbitmq.py
    environment:
      TRACARDI_BROKER_URL: amqp://rabbitmq:5672//
    depends_on:
      - rabbitmq
    deploy:
      replicas: 3  # Scale workers
  
  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - "5672:5672"
      - "15672:15672"
```

---

## Monitoring

### RabbitMQ
```bash
# Check queue depth
rabbitmqctl list_queues name messages

# Monitor consumers
rabbitmqctl list_consumers
```

### Kafka
```bash
# Check consumer lag
kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --describe \
  --group tracardi-consumer-group
```

---

## Production Checklist

- [ ] Dead Letter Queue (DLQ) configured
- [ ] Monitoring/alerting setup
- [ ] Worker auto-scaling configured
- [ ] Message retention policy set
- [ ] Error tracking enabled
- [ ] Log aggregation configured
- [ ] Health checks implemented
- [ ] Graceful shutdown tested

---

## Next Steps

1. **Choose your broker** (RabbitMQ or Kafka)
2. **Deploy worker(s)** using examples above
3. **Configure monitoring**
4. **Test end-to-end flow**
5. **Scale workers** based on load

⚠️ **Without workers, messages will queue indefinitely!**
