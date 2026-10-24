# Grafana Loki Integration

This document describes the Grafana Loki integration for Tracardi, which enables optional centralized logging to Loki for enhanced monitoring and tracing capabilities.

## Overview

Tracardi now supports sending logs to Grafana Loki, a horizontally-scalable, highly-available log aggregation system. This integration is **completely optional** and can be enabled via environment variables without any code changes.

## Features

- **Optional Integration**: Enable/disable via environment variables
- **Batched Logging**: Efficient batch sending to reduce network overhead
- **Configurable Labels**: Custom labels for log categorization
- **Authentication Support**: Basic auth for secured Loki instances
- **Non-Blocking**: Logging errors don't affect application performance
- **Backward Compatible**: Works alongside existing Elasticsearch logging

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `LOKI_ENABLED` | No | `no` | Enable/disable Loki logging (`yes`/`no`) |
| `LOKI_URL` | Yes* | `None` | Loki server URL (e.g., `http://localhost:3100`) |
| `LOKI_USERNAME` | No | `None` | Basic auth username |
| `LOKI_PASSWORD` | No | `None` | Basic auth password |
| `LOKI_LABELS` | No | `service=tracardi,environment=production` | Comma-separated labels (e.g., `app=tracardi,env=prod`) |
| `LOKI_VERSION` | No | `1` | Loki API version |
| `LOKI_TIMEOUT` | No | `10` | Request timeout in seconds |
| `LOKI_BATCH_SIZE` | No | `100` | Number of logs to batch before sending |
| `LOKI_BATCH_INTERVAL` | No | `5` | Time in seconds before sending batch |

\* Required only when `LOKI_ENABLED=yes`

### Example Configuration

#### Docker Compose

```yaml
version: '3.8'

services:
  tracardi:
    image: tracardi/tracardi:latest
    environment:
      - LOKI_ENABLED=yes
      - LOKI_URL=http://loki:3100
      - LOKI_LABELS=service=tracardi,environment=production,instance=main
      - LOKI_BATCH_SIZE=50
      - LOKI_BATCH_INTERVAL=10
    depends_on:
      - loki

  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"
    volumes:
      - ./loki-config.yaml:/etc/loki/local-config.yaml
```

#### Kubernetes

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: tracardi-config
data:
  LOKI_ENABLED: "yes"
  LOKI_URL: "http://loki.monitoring.svc.cluster.local:3100"
  LOKI_LABELS: "service=tracardi,environment=production,cluster=k8s"
  LOKI_BATCH_SIZE: "100"
  LOKI_BATCH_INTERVAL: "5"
---
apiVersion: v1
kind: Secret
metadata:
  name: loki-credentials
type: Opaque
stringData:
  username: admin
  password: secret123
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tracardi
spec:
  template:
    spec:
      containers:
      - name: tracardi
        image: tracardi/tracardi:latest
        envFrom:
        - configMapRef:
            name: tracardi-config
        env:
        - name: LOKI_USERNAME
          valueFrom:
            secretKeyRef:
              name: loki-credentials
              key: username
        - name: LOKI_PASSWORD
          valueFrom:
            secretKeyRef:
              name: loki-credentials
              key: password
```

#### Environment File (.env)

```bash
# Loki Configuration
LOKI_ENABLED=yes
LOKI_URL=http://localhost:3100
LOKI_USERNAME=admin
LOKI_PASSWORD=secret123
LOKI_LABELS=service=tracardi,environment=development,host=localhost
LOKI_BATCH_SIZE=50
LOKI_BATCH_INTERVAL=10
LOKI_TIMEOUT=15
```

## Log Format

Logs sent to Loki include the following fields:

```json
{
  "date": "2026-01-12T10:30:00.000000",
  "message": "Log message",
  "logger": "tracardi.service.example",
  "file": "example.py",
  "line": 42,
  "level": "ERROR",
  "stack_info": "...",
  "module": "tracardi.service",
  "class_name": "ExampleClass",
  "origin": "root",
  "event_id": "event-uuid",
  "profile_id": "profile-uuid",
  "flow_id": "flow-uuid",
  "node_id": "node-uuid",
  "user_id": "user-uuid"
}
```

## Querying Logs in Grafana

### Example LogQL Queries

1. **All Tracardi logs:**
   ```logql
   {service="tracardi"}
   ```

2. **Error logs only:**
   ```logql
   {service="tracardi"} | json | level="ERROR"
   ```

3. **Logs for specific profile:**
   ```logql
   {service="tracardi"} | json | profile_id="profile-123"
   ```

4. **Logs with specific message pattern:**
   ```logql
   {service="tracardi"} | json | message =~ ".*database.*"
   ```

5. **Rate of errors per minute:**
   ```logql
   rate({service="tracardi"} | json | level="ERROR" [1m])
   ```

## Setting Up Grafana Loki

### Quick Start with Docker

```bash
# Create loki-config.yaml
cat > loki-config.yaml <<EOF
auth_enabled: false

server:
  http_listen_port: 3100

ingester:
  lifecycler:
    address: 127.0.0.1
    ring:
      kvstore:
        store: inmemory
      replication_factor: 1
  chunk_idle_period: 5m
  chunk_retain_period: 30s

schema_config:
  configs:
    - from: 2020-05-15
      store: boltdb
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 168h

storage_config:
  boltdb:
    directory: /tmp/loki/index
  filesystem:
    directory: /tmp/loki/chunks

limits_config:
  enforce_metric_name: false
  reject_old_samples: true
  reject_old_samples_max_age: 168h
EOF

# Run Loki
docker run -d --name loki \
  -p 3100:3100 \
  -v $(pwd)/loki-config.yaml:/etc/loki/local-config.yaml \
  grafana/loki:latest

# Run Grafana
docker run -d --name grafana \
  -p 3000:3000 \
  grafana/grafana:latest
```

### Configure Grafana

1. Open Grafana at `http://localhost:3000` (default credentials: admin/admin)
2. Go to Configuration → Data Sources
3. Add Loki data source with URL: `http://loki:3100`
4. Save and test the connection

## Performance Considerations

- **Batch Size**: Larger batches reduce network calls but increase memory usage
- **Batch Interval**: Shorter intervals provide near real-time logs but increase network traffic
- **Log Level**: Only WARNING, ERROR, and CRITICAL logs are sent to Loki by default
- **Non-Blocking**: Failed Loki requests don't block the application

## Troubleshooting

### Logs not appearing in Loki

1. Check if Loki is enabled:
   ```bash
   echo $LOKI_ENABLED
   ```

2. Verify Loki URL is accessible:
   ```bash
   curl http://your-loki-url:3100/ready
   ```

3. Check Tracardi logs for Loki errors:
   ```bash
   docker logs tracardi | grep -i loki
   ```

### Authentication errors

Ensure `LOKI_USERNAME` and `LOKI_PASSWORD` are correctly set if your Loki instance requires authentication.

### High memory usage

Reduce `LOKI_BATCH_SIZE` or decrease `LOKI_BATCH_INTERVAL` to send logs more frequently.

## Architecture

```
┌─────────────┐
│  Tracardi   │
│  Logger     │
└──────┬──────┘
       │
       ├─────────────────┐
       │                 │
       ▼                 ▼
┌──────────────┐  ┌─────────────┐
│ Elasticsearch│  │    Loki     │
│   Handler    │  │   Handler   │
└──────────────┘  └──────┬──────┘
                         │
                         │ Batch
                         │ HTTP POST
                         ▼
                  ┌─────────────┐
                  │ Grafana Loki│
                  └─────────────┘
```

## Testing

Run the unit tests:

```bash
python -m pytest test/unit/test_loki_integration.py -v
```

## Contributing

This feature was contributed to support modern observability practices. If you find issues or have suggestions:

1. Open an issue on GitHub
2. Submit a pull request with improvements
3. Join the Tracardi Slack community for discussions

## License

This integration follows the same license as Tracardi (MIT with Common Clause).

## References

- [Grafana Loki Documentation](https://grafana.com/docs/loki/latest/)
- [LogQL Query Language](https://grafana.com/docs/loki/latest/logql/)
- [Tracardi Documentation](https://manual.tracardi.com)
