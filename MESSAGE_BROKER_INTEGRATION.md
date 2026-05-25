# Message Broker Integration

## Overview

Tracardi supports multiple message brokers for asynchronous event processing:

- **RabbitMQ** (Open Source) - via Kombu
- **Apache Kafka** (Open Source) - via aiokafka  
- **Apache Pulsar** (Commercial) - Native support

This allows you to choose the message broker that best fits your infrastructure.

---

## Architecture

```
Event Tracking API
       ↓
Tracker (tracardi/service/tracker.py)
       ↓
  [Queue Required?]
       ↓
Message Broker Factory
       ├─→ RabbitMQ Broker
       ├─→ Kafka Broker
       └─→ Pulsar Broker (Commercial)
       ↓
Message Queue
       ↓
Worker Consumer
       ↓
Event Processing Pipeline
```

---

## Configuration

### Environment Variables

```bash
# Broker Selection
TRACARDI_MESSAGE_BROKER=rabbitmq  # rabbitmq, kafka, pulsar

# Connection
TRACARDI_BROKER_URL=amqp://localhost:5672//  # Broker URL
TRACARDI_BROKER_TOPIC=tracardi-events         # Topic/Queue name
TRACARDI_BROKER_TIMEOUT=30                     # Connection timeout (seconds)

# Authentication (Optional)
TRACARDI_BROKER_USERNAME=admin
TRACARDI_BROKER_PASSWORD=secret

# RabbitMQ Specific
TRACARDI_BROKER_EXCHANGE_TYPE=direct  # direct, topic, fanout
TRACARDI_BROKER_ROUTING_KEY=events
TRACARDI_BROKER_DURABLE=yes

# Kafka Specific
TRACARDI_BROKER_GROUP_ID=tracardi-consumer-group

# Pulsar Specific (Commercial)
TRACARDI_BROKER_LISTENER_NAME=external
```

---

## RabbitMQ Setup

### 1. Install RabbitMQ

**Docker:**
```bash
docker run -d \
  --name rabbitmq \
  -p 5672:5672 \
  -p 15672:15672 \
  -e RABBITMQ_DEFAULT_USER=admin \
  -e RABBITMQ_DEFAULT_PASS=secret \
  rabbitmq:3-management
```

**Ubuntu/Debian:**
```bash
sudo apt-get install rabbitmq-server
sudo systemctl enable rabbitmq-server
sudo systemctl start rabbitmq-server
```

### 2. Configure Tracardi

```bash
# .env or environment
TRACARDI_MESSAGE_BROKER=rabbitmq
TRACARDI_BROKER_URL=amqp://admin:secret@localhost:5672//
TRACARDI_BROKER_TOPIC=tracardi-events
```

### 3. Verify Connection

```bash
# RabbitMQ Management UI
http://localhost:15672
# Login: admin / secret

# Check queue
rabbitmqctl list_queues
```

---

## Kafka Setup

### 1. Install Kafka

**Docker (with Zookeeper):**
```bash
# docker-compose.yml
version: '3'
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:latest
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
    ports:
      - "2181:2181"
  
  kafka:
    image: confluentinc/cp-kafka:latest
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
```

```bash
docker-compose up -d
```

### 2. Install Python Dependencies

```bash
pip install aiokafka
```

### 3. Configure Tracardi

```bash
# .env or environment
TRACARDI_MESSAGE_BROKER=kafka
TRACARDI_BROKER_URL=localhost:9092
TRACARDI_BROKER_TOPIC=tracardi-events
TRACARDI_BROKER_GROUP_ID=tracardi-consumer-group
```

### 4. Create Topic

```bash
# Inside Kafka container
docker exec -it kafka kafka-topics \
  --create \
  --topic tracardi-events \
  --bootstrap-server localhost:9092 \
  --replication-factor 1 \
  --partitions 3
```

---

## Apache Pulsar Setup (Commercial)

### Prerequisites
- Tracardi Commercial License

### Configuration

```bash
TRACARDI_MESSAGE_BROKER=pulsar
TRACARDI_BROKER_URL=pulsar://localhost:6650
TRACARDI_BROKER_TOPIC=tracardi-events
TRACARDI_BROKER_USERNAME=admin
TRACARDI_BROKER_PASSWORD=<token>
TRACARDI_BROKER_LISTENER_NAME=external
```

---

## Usage

### Trigger Queue Processing

Events are automatically routed to the message broker when:

1. **Queue option is enabled** in tracker payload:
```javascript
// JavaScript SDK
tracardi.track("page-view", {
  // ... event properties
}, {
  queue: true  // Enable async processing
});
```

2. **Events are marked as async**:
```javascript
tracardi.track("analytics-event", {
  // ... properties
}, {
  queue: true,
  async: true
});
```

### API Request Example

```bash
curl -X POST http://localhost:8686/track \
  -H "Content-Type: application/json" \
  -d '{
    "source": {"id": "source-id"},
    "session": {"id": "session-id"},
    "events": [{
      "type": "page-view",
      "properties": {}
    }],
    "options": {
      "queue": true
    }
  }'
```

---

## Worker Setup

You need to run a worker process to consume messages from the broker.

### RabbitMQ Worker Example

```python
# worker.py
import asyncio
import json
from kombu import Connection, Queue, Exchange
from tracardi.service.tracking.tracker import os_tracker

def process_message(body, message):
    """Process tracker payload from RabbitMQ"""
    try:
        data = json.loads(body)
        tracker_config = data['tracker_config']
        tracker_payload = data['tracker_payload']
        source = data['source']
        
        # Process event
        asyncio.run(os_tracker(
            source,
            tracker_payload,
            tracker_config,
            tracking_start=0
        ))
        
        message.ack()
    except Exception as e:
        print(f"Error processing message: {e}")
        message.reject()

# Connect to RabbitMQ
conn = Connection('amqp://admin:secret@localhost:5672//')
queue = Queue('tracardi-events', Exchange('tracardi-events'))

# Consume messages
with conn.Consumer(queue, callbacks=[process_message]):
    conn.drain_events()
```

### Kafka Worker Example

```python
# kafka_worker.py
import asyncio
import json
from aiokafka import AIOKafkaConsumer

async def consume():
    consumer = AIOKafkaConsumer(
        'tracardi-events',
        bootstrap_servers='localhost:9092',
        group_id='tracardi-consumer-group'
    )
    
    await consumer.start()
    try:
        async for msg in consumer:
            data = json.loads(msg.value)
            # Process event...
            print(f"Consumed: {data}")
    finally:
        await consumer.stop()

asyncio.run(consume())
```

---

## Monitoring

### RabbitMQ Metrics

```bash
# Queue depth
rabbitmqctl list_queues name messages

# Connection status
rabbitmqctl list_connections

# Consumer info
rabbitmqctl list_consumers
```

### Kafka Metrics

```bash
# Consumer lag
kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --describe \
  --group tracardi-consumer-group

# Topic info
kafka-topics \
  --bootstrap-server localhost:9092 \
  --describe \
  --topic tracardi-events
```

---

## Troubleshooting

### Connection Errors

```bash
# Check broker is running
docker ps | grep rabbitmq
docker ps | grep kafka

# Test connection
telnet localhost 5672  # RabbitMQ
telnet localhost 9092  # Kafka
```

### Message Not Being Consumed

1. **Check worker is running**
2. **Verify queue/topic exists**
3. **Check permissions**
4. **Inspect logs**:
```bash
tail -f /var/log/tracardi/worker.log
```

### Import Errors

```bash
# RabbitMQ
pip install kombu

# Kafka
pip install aiokafka
```

---

## Performance Tuning

### RabbitMQ

```bash
# Increase connection pool
TRACARDI_BROKER_POOL_SIZE=10

# Enable compression
TRACARDI_BROKER_COMPRESSION=gzip
```

### Kafka

```bash
# Increase partitions for parallelism
kafka-topics --alter \
  --topic tracardi-events \
  --partitions 10

# Consumer config
TRACARDI_BROKER_MAX_POLL_RECORDS=500
TRACARDI_BROKER_FETCH_MIN_BYTES=1048576
```

---

## Migration from Pulsar

If you're migrating from Pulsar to RabbitMQ/Kafka:

1. **Run both brokers in parallel**
2. **Gradually shift traffic** using feature flags
3. **Monitor queue depths**
4. **Switch DNS/environment variables**
5. **Decommission Pulsar** after verification

```bash
# Phase 1: Run both
TRACARDI_MESSAGE_BROKER=pulsar

# Phase 2: Switch
TRACARDI_MESSAGE_BROKER=rabbitmq

# Phase 3: Verify & cleanup
```

---

## Contributing

To add support for a new broker:

1. Create `tracardi/service/message_broker/implementations/yourbroker_broker.py`
2. Extend `MessageBroker` base class
3. Implement: `connect()`, `disconnect()`, `publish()`, `health_check()`
4. Add to `broker_factory.py`
5. Submit PR!

---

## License

- **RabbitMQ & Kafka support**: MIT License (Open Source)
- **Pulsar support**: Commercial License required

---

## Support

- **Documentation**: https://docs.tracardi.com
- **GitHub Issues**: https://github.com/Tracardi/tracardi/issues
- **Community**: https://join.slack.com/t/tracardi/
