# Event Worker - Production Deployment Guide

## Overview

The Event Worker consumes events from message brokers (RabbitMQ/Kafka) and processes them through the full Tracardi pipeline.

This is the **consumer** side of the message broker integration.

---

## Quick Start

### 1. Configure Message Broker

```bash
# RabbitMQ
export TRACARDI_MESSAGE_BROKER=rabbitmq
export TRACARDI_BROKER_URL=amqp://localhost:5672//
export TRACARDI_BROKER_TOPIC=tracardi-events

# OR Kafka
export TRACARDI_MESSAGE_BROKER=kafka
export TRACARDI_BROKER_URL=localhost:9092
export TRACARDI_BROKER_TOPIC=tracardi-events
export TRACARDI_BROKER_GROUP_ID=tracardi-consumer-group
```

### 2. Run Worker

```bash
# From Tracardi root directory
python -m tracardi.worker.event_worker
```

---

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Tracardi
COPY tracardi/ ./tracardi/

# Run event worker
CMD ["python", "-m", "tracardi.worker.event_worker"]
```

### Build & Run

```bash
# Build
docker build -t tracardi-event-worker .

# Run (RabbitMQ)
docker run -d \
  --name tracardi-worker \
  -e TRACARDI_MESSAGE_BROKER=rabbitmq \
  -e TRACARDI_BROKER_URL=amqp://rabbitmq:5672// \
  -e TRACARDI_BROKER_TOPIC=tracardi-events \
  -e ELASTICSEARCH_URL=http://elasticsearch:9200 \
  -e REDIS_HOST=redis://redis:6379 \
  tracardi-event-worker

# Scale workers
docker run -d --name tracardi-worker-1 tracardi-event-worker
docker run -d --name tracardi-worker-2 tracardi-event-worker
docker run -d --name tracardi-worker-3 tracardi-event-worker
```

---

## Docker Compose

```yaml
version: '3.8'

services:
  # Message Broker
  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - "5672:5672"
      - "15672:15672"
    environment:
      RABBITMQ_DEFAULT_USER: admin
      RABBITMQ_DEFAULT_PASS: secret
  
  # Tracardi API
  tracardi-api:
    image: tracardi/tracardi-api
    ports:
      - "8686:80"
    environment:
      TRACARDI_MESSAGE_BROKER: rabbitmq
      TRACARDI_BROKER_URL: amqp://rabbitmq:5672//
      TRACARDI_BROKER_TOPIC: tracardi-events
      ELASTICSEARCH_URL: http://elasticsearch:9200
      REDIS_HOST: redis://redis:6379
    depends_on:
      - rabbitmq
      - elasticsearch
      - redis
  
  # Event Workers (scaled to 3)
  tracardi-worker:
    image: tracardi/tracardi-api
    command: python -m tracardi.worker.event_worker
    environment:
      TRACARDI_MESSAGE_BROKER: rabbitmq
      TRACARDI_BROKER_URL: amqp://rabbitmq:5672//
      TRACARDI_BROKER_TOPIC: tracardi-events
      ELASTICSEARCH_URL: http://elasticsearch:9200
      REDIS_HOST: redis://redis:6379
    depends_on:
      - rabbitmq
      - elasticsearch
      - redis
    deploy:
      replicas: 3  # 3 workers for parallelism
  
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.9.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
  
  redis:
    image: redis:alpine
```

**Start:**
```bash
docker-compose up -d

# Scale workers
docker-compose up -d --scale tracardi-worker=5
```

---

## Kubernetes Deployment

### Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tracardi-event-worker
spec:
  replicas: 3
  selector:
    matchLabels:
      app: tracardi-worker
  template:
    metadata:
      labels:
        app: tracardi-worker
    spec:
      containers:
      - name: worker
        image: tracardi/tracardi-api:latest
        command: ["python", "-m", "tracardi.worker.event_worker"]
        env:
        - name: TRACARDI_MESSAGE_BROKER
          value: "rabbitmq"
        - name: TRACARDI_BROKER_URL
          value: "amqp://rabbitmq:5672//"
        - name: TRACARDI_BROKER_TOPIC
          value: "tracardi-events"
        - name: ELASTICSEARCH_URL
          value: "http://elasticsearch:9200"
        - name: REDIS_HOST
          value: "redis://redis:6379"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          exec:
            command:
            - python
            - -c
            - "import sys; sys.exit(0)"
          initialDelaySeconds: 30
          periodSeconds: 30
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: tracardi-worker-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: tracardi-event-worker
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

---

## Systemd Service

```ini
# /etc/systemd/system/tracardi-worker.service
[Unit]
Description=Tracardi Event Worker
After=network.target rabbitmq.service

[Service]
Type=simple
User=tracardi
WorkingDirectory=/opt/tracardi
Environment="TRACARDI_MESSAGE_BROKER=rabbitmq"
Environment="TRACARDI_BROKER_URL=amqp://localhost:5672//"
Environment="TRACARDI_BROKER_TOPIC=tracardi-events"
Environment="ELASTICSEARCH_URL=http://localhost:9200"
Environment="REDIS_HOST=redis://localhost:6379"
ExecStart=/usr/bin/python3 -m tracardi.worker.event_worker
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Enable & Start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable tracardi-worker
sudo systemctl start tracardi-worker
sudo systemctl status tracardi-worker

# View logs
sudo journalctl -u tracardi-worker -f
```

---

## Monitoring

### Worker Logs

```bash
# Docker
docker logs -f tracardi-worker

# Systemd
sudo journalctl -u tracardi-worker -f

# Kubernetes
kubectl logs -f deployment/tracardi-event-worker
```

### Metrics

Worker logs progress every 100 events:
```
Worker stats: processed=1000, errors=5
```

### RabbitMQ Monitoring

```bash
# Queue depth
rabbitmqctl list_queues name messages consumers

# Consumer count
rabbitmqctl list_consumers
```

### Kafka Monitoring

```bash
# Consumer lag
kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --describe \
  --group tracardi-consumer-group
```

---

## Troubleshooting

### Worker Not Consuming

1. **Check broker connection:**
   ```bash
   # RabbitMQ
   rabbitmqctl status
   
   # Kafka
   kafka-topics --list --bootstrap-server localhost:9092
   ```

2. **Verify queue exists:**
   ```bash
   # RabbitMQ
   rabbitmqctl list_queues
   ```

3. **Check worker logs:**
   ```bash
   docker logs tracardi-worker
   ```

### High Error Rate

1. **Check Elasticsearch:**
   ```bash
   curl http://localhost:9200/_cluster/health
   ```

2. **Check Redis:**
   ```bash
   redis-cli ping
   ```

3. **Review error logs:**
   ```bash
   docker logs tracardi-worker 2>&1 | grep ERROR
   ```

### Performance Issues

1. **Scale workers:**
   ```bash
   docker-compose up -d --scale tracardi-worker=5
   ```

2. **Increase prefetch:**
   Edit `event_worker.py`, line with `prefetch_count=10` → `prefetch_count=50`

3. **Monitor resources:**
   ```bash
   docker stats tracardi-worker
   ```

---

## Production Checklist

- [ ] Message broker deployed and accessible
- [ ] Dead Letter Queue configured (RabbitMQ)
- [ ] Worker replicas configured (3+ recommended)
- [ ] Auto-scaling enabled (Kubernetes HPA)
- [ ] Monitoring/alerting configured
- [ ] Log aggregation setup
- [ ] Resource limits configured
- [ ] Health checks implemented
- [ ] Graceful shutdown tested
- [ ] Backup/recovery plan

---

## Architecture

```
┌──────────────┐
│ Tracardi API │
└──────┬───────┘
       │ publish
       ↓
┌──────────────────┐
│ Message Broker   │ (RabbitMQ/Kafka)
│ ┌──────────────┐ │
│ │    Queue     │ │
│ └──────────────┘ │
└────────┬─────────┘
         │ consume
    ┌────┴────┬────────┬────────┐
    ↓         ↓        ↓        ↓
┌─────────┐ ┌─────────┐ ┌─────────┐
│Worker 1 │ │Worker 2 │ │Worker N │
└────┬────┘ └────┬────┘ └────┬────┘
     │           │           │
     └───────────┴───────────┘
                 │
         ┌───────┴────────┐
         │ Event Pipeline │
         │ - Profile load │
         │ - Validation   │
         │ - Workflows    │
         │ - DB save      │
         │ - Destinations │
         └────────────────┘
```

---

## Next Steps

1. **Deploy worker** using one of the methods above
2. **Monitor** queue depth and worker performance
3. **Scale** based on load
4. **Configure** alerts for queue buildup
5. **Test** end-to-end flow

---

## Support

- GitHub Issues: https://github.com/Tracardi/tracardi/issues
- Documentation: https://docs.tracardi.com
- Community: https://join.slack.com/t/tracardi/
