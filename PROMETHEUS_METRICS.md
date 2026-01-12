# Prometheus Metrics Integration

Optional Prometheus metrics collection for monitoring Tracardi in production.

## Quick Start

### Enable Prometheus

```bash
export PROMETHEUS_ENABLED=yes
```

### In FastAPI App

```python
from fastapi import FastAPI
from tracardi.service.metrics import install_prometheus_middleware, install_metrics_endpoint

app = FastAPI()

# Auto-instrument HTTP requests
install_prometheus_middleware(app)

# Add /metrics endpoint
install_metrics_endpoint(app)
```

## Configuration

```bash
# Core
PROMETHEUS_ENABLED=yes|no               # Default: no

# Metrics types
PROMETHEUS_TRACK_HTTP=yes|no            # Default: yes
PROMETHEUS_TRACK_DATABASE=yes|no        # Default: yes
PROMETHEUS_TRACK_HEALTH=yes|no          # Default: yes
PROMETHEUS_TRACK_EVENTS=yes|no          # Default: yes

# Labels
PROMETHEUS_SERVICE_NAME=tracardi         # Default: tracardi
PROMETHEUS_ENVIRONMENT=production        # Default: production
PROMETHEUS_INSTANCE=$HOSTNAME            # Default: hostname

# Endpoint
PROMETHEUS_METRICS_PATH=/metrics         # Default: /metrics
```

## Available Metrics

### HTTP Metrics
- `tracardi_http_requests_total` - Total requests (counter)
- `tracardi_http_request_duration_seconds` - Request latency (histogram)
- `tracardi_http_requests_in_progress` - Active requests (gauge)

### Database Metrics
- `tracardi_db_queries_total` - Total queries (counter)
- `tracardi_db_query_duration_seconds` - Query latency (histogram)
- `tracardi_db_connections_active` - Active connections (gauge)

### Health Check Metrics
- `tracardi_health_check_status` - Health status (gauge, 1=healthy, 0=unhealthy)
- `tracardi_health_check_duration_seconds` - Check duration (histogram)

### Event Processing Metrics
- `tracardi_events_processed_total` - Events processed (counter)
- `tracardi_profiles_updated_total` - Profiles updated (counter)
- `tracardi_workflows_executed_total` - Workflows executed (counter)

## Prometheus Configuration

### prometheus.yml

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'tracardi'
    static_configs:
      - targets: ['tracardi:8686']
    metrics_path: /metrics
```

### Kubernetes ServiceMonitor

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: tracardi
spec:
  selector:
    matchLabels:
      app: tracardi
  endpoints:
  - port: http
    path: /metrics
    interval: 15s
```

## Custom Metrics

```python
from tracardi.service.metrics import metrics_manager

# Track custom event
metrics_manager.track_event("page_view", source="web")

# Track profile update
metrics_manager.track_profile_update()

# Track workflow
metrics_manager.track_workflow_execution("workflow-123", "success")
```

## Example Queries

### Request Rate
```promql
rate(tracardi_http_requests_total[5m])
```

### 95th Percentile Latency
```promql
histogram_quantile(0.95, rate(tracardi_http_request_duration_seconds_bucket[5m]))
```

### Error Rate
```promql
rate(tracardi_http_requests_total{status=~"5.."}[5m])
```

### Database Connection Pool
```promql
tracardi_db_connections_active{database="mysql"}
```

## Grafana Dashboard

Import dashboard ID: (to be created)

Or use the example dashboard in `prometheus-examples/grafana-dashboard.json`

## Best Practices

1. Enable only needed metrics
2. Use appropriate label cardinality
3. Set reasonable scrape intervals (15-60s)
4. Monitor /metrics endpoint performance
5. Use recording rules for complex queries

## Performance Impact

- Minimal overhead (< 1ms per request)
- Memory: ~10MB for typical metric set
- CPU: < 0.5% additional usage

## Troubleshooting

### Metrics not appearing

```bash
# Check if enabled
curl http://localhost:8686/metrics

# Check logs
docker logs tracardi | grep -i prometheus
```

### High cardinality warnings

Reduce label values or disable specific metrics.

