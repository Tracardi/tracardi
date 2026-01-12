# Health Check Configuration Examples

## Optional MySQL (Using StarRocks)

If you're using StarRocks instead of MySQL:

```bash
# Disable MySQL health checks and cleanup
export HEALTH_CHECK_MYSQL=no
export SHUTDOWN_CLOSE_MYSQL=no
export STARTUP_WARMUP_MYSQL=no
```

## Optional Redis (No Caching)

If Redis is not available:

```bash
export HEALTH_CHECK_REDIS=no
export SHUTDOWN_CLOSE_REDIS=no
export STARTUP_WARMUP_REDIS=no
```

## Minimal Setup (Elasticsearch Only)

For minimal deployments:

```bash
# Only check Elasticsearch
export HEALTH_CHECK_ELASTICSEARCH=yes
export HEALTH_CHECK_MYSQL=no
export HEALTH_CHECK_REDIS=no

export SHUTDOWN_CLOSE_ELASTICSEARCH=yes
export SHUTDOWN_CLOSE_MYSQL=no
export SHUTDOWN_CLOSE_REDIS=no

export STARTUP_WARMUP_ELASTICSEARCH=yes
export STARTUP_WARMUP_MYSQL=no
export STARTUP_WARMUP_REDIS=no
```

## Custom Timeouts

```bash
# Slower network? Increase timeouts
export HEALTH_CHECK_TIMEOUT=10.0
export GRACEFUL_SHUTDOWN_TIMEOUT=60.0
export STARTUP_WAIT_TIMEOUT=120.0
```

## Docker Compose Example

```yaml
version: '3.8'

services:
  tracardi:
    image: tracardi/tracardi-api:latest
    environment:
      # Core services
      - ELASTIC_HOST=elasticsearch:9200
      
      # MySQL is optional - using StarRocks
      - HEALTH_CHECK_MYSQL=no
      - SHUTDOWN_CLOSE_MYSQL=no
      - STARTUP_WARMUP_MYSQL=no
      
      # Redis optional
      - HEALTH_CHECK_REDIS=no
      - SHUTDOWN_CLOSE_REDIS=no
      - STARTUP_WARMUP_REDIS=no
      
      # Timeouts
      - HEALTH_CHECK_TIMEOUT=5.0
      - GRACEFUL_SHUTDOWN_TIMEOUT=30.0
```

## Kubernetes ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: tracardi-health-config
data:
  # Health checks
  HEALTH_CHECK_ELASTICSEARCH: "yes"
  HEALTH_CHECK_MYSQL: "no"    # Using StarRocks
  HEALTH_CHECK_REDIS: "yes"
  HEALTH_CHECK_TIMEOUT: "5.0"
  
  # Graceful shutdown
  SHUTDOWN_CLOSE_ELASTICSEARCH: "yes"
  SHUTDOWN_CLOSE_MYSQL: "no"
  SHUTDOWN_CLOSE_REDIS: "yes"
  SHUTDOWN_FLUSH_LOKI: "yes"
  GRACEFUL_SHUTDOWN_TIMEOUT: "30.0"
  
  # Startup
  STARTUP_WARMUP_ELASTICSEARCH: "yes"
  STARTUP_WARMUP_MYSQL: "no"
  STARTUP_WARMUP_REDIS: "yes"
  STARTUP_WAIT_TIMEOUT: "60.0"
```
