# Kubernetes Health Probes & Graceful Shutdown

This document describes the Kubernetes health probe and graceful shutdown implementation for Tracardi.

## Overview

Tracardi now includes production-ready health check endpoints and graceful shutdown handlers specifically designed for Kubernetes deployments.

## Features

✅ **Liveness Probe** - Checks if application is running  
✅ **Readiness Probe** - Checks if application can serve traffic  
✅ **Startup Probe** - Gives application time to start  
✅ **Graceful Shutdown** - Clean termination with connection cleanup  
✅ **Dependency Health Checks** - Elasticsearch, MySQL, Redis  
✅ **Configurable Timeouts** - Customizable check intervals  

## Health Check Endpoints

### `/health` - Liveness Probe

**Purpose**: Checks if the application process is alive and running.

**Kubernetes Usage**: If this fails, Kubernetes will restart the pod.

**Response Example**:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-12T10:30:00.000Z",
  "version": "1.1.0",
  "components": {
    "application": {
      "status": "healthy",
      "message": "Application process is running"
    }
  }
}
```

**Characteristics**:
- Lightweight check
- Always passes if process is running
- Fast response time (< 50ms)

### `/ready` - Readiness Probe

**Purpose**: Checks if the application can serve traffic by verifying all dependencies.

**Kubernetes Usage**: If this fails, Kubernetes removes the pod from service load balancer.

**Response Example**:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-12T10:30:00.000Z",
  "version": "1.1.0",
  "components": {
    "elasticsearch": {
      "status": "healthy",
      "message": "Elasticsearch cluster is healthy",
      "response_time_ms": 45.2,
      "details": {
        "cluster_name": "tracardi-cluster",
        "number_of_nodes": 3,
        "active_shards": 24
      }
    },
    "mysql": {
      "status": "healthy",
      "message": "MySQL is accessible",
      "response_time_ms": 12.8
    },
    "redis": {
      "status": "healthy",
      "message": "Redis is accessible",
      "response_time_ms": 8.5
    }
  }
}
```

**Checks**:
- Elasticsearch cluster health
- MySQL connection
- Redis connection

## Graceful Shutdown

When Kubernetes sends a SIGTERM signal (pod termination), Tracardi:

1. **Stops accepting new requests** (readiness probe fails)
2. **Waits for ongoing requests** to complete
3. **Closes database connections** cleanly
4. **Flushes logs** (including Loki if enabled)
5. **Exits with code 0**

### Shutdown Sequence

```
SIGTERM received
    ↓
Stop accepting traffic (readiness = false)
    ↓
Wait for ongoing requests (max 30s)
    ↓
Close Elasticsearch connections
    ↓
Close MySQL connections
    ↓
Close Redis connections
    ↓
Flush Loki logs (if enabled)
    ↓
Exit cleanly
```

### Configuration

```python
from tracardi.service.health import (
    HealthCheckService,
    GracefulShutdownHandler,
    create_default_shutdown_handler
)

# In your FastAPI app
@app.get("/health")
async def health():
    return await HealthCheckService.liveness()

@app.get("/ready")
async def readiness():
    return await HealthCheckService.readiness()

# Install shutdown handler
shutdown_handler = create_default_shutdown_handler(shutdown_timeout=30.0)
shutdown_handler.install_signal_handlers()

@app.on_event("shutdown")
async def shutdown():
    await shutdown_handler.shutdown()
```

## Kubernetes Configuration

### Deployment with Health Probes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tracardi
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: tracardi
        image: tracardi/tracardi-api:latest
        
        # Liveness probe
        livenessProbe:
          httpGet:
            path: /health
            port: 8686
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        
        # Readiness probe
        readinessProbe:
          httpGet:
            path: /ready
            port: 8686
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        
        # Startup probe
        startupProbe:
          httpGet:
            path: /health
            port: 8686
          periodSeconds: 5
          failureThreshold: 12  # 60s total startup time
        
        # Graceful shutdown
        lifecycle:
          preStop:
            exec:
              command: ["/bin/sh", "-c", "sleep 15"]
      
      terminationGracePeriodSeconds: 30
```

### Recommended Settings

| Probe | initialDelay | period | timeout | failureThreshold |
|-------|--------------|--------|---------|------------------|
| **Liveness** | 30s | 10s | 5s | 3 |
| **Readiness** | 10s | 5s | 3s | 3 |
| **Startup** | 0s | 5s | 3s | 12 |

### Rolling Update Strategy

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1          # Add 1 new pod before removing old
    maxUnavailable: 0    # Always maintain capacity
```

## Health Check Implementation

### Component Health Checks

#### Elasticsearch
- Checks cluster health status (green/yellow/red)
- Verifies node availability
- Measures response time
- Timeout: 5s

#### MySQL
- Executes `SELECT 1` query
- Verifies connection pool
- Measures response time
- Timeout: 5s

#### Redis  
- Executes `PING` command
- Verifies connection
- Measures response time
- Timeout: 5s

### Status Codes

- **healthy**: Component is fully operational
- **degraded**: Component is operational but sub-optimal (e.g., ES yellow)
- **unhealthy**: Component is down or unreachable
- **unknown**: Unable to determine status

### Overall Status Logic

```python
if all components healthy:
    status = "healthy"
elif any component unhealthy:
    status = "unhealthy"
else:
    status = "degraded"
```

## Startup Sequence

The application follows this startup sequence:

1. **Process starts**
2. **Wait for dependencies** (max 60s)
   - Check Elasticsearch
   - Check MySQL
   - Check Redis
3. **Warm up connections**
4. **Start accepting traffic**

### Dependency Wait Logic

```python
from tracardi.service.health import StartupHandler

startup_handler = StartupHandler(max_retries=10, retry_delay=2.0)

@app.on_event("startup")
async def startup():
    await startup_handler.run()
```

## Troubleshooting

### Pod stuck in CrashLoopBackOff

**Possible causes**:
- Dependencies (Elasticsearch/MySQL/Redis) not available
- Startup probe timeout too short
- Liveness probe failing

**Solution**:
```bash
# Check pod logs
kubectl logs pod/tracardi-xxx

# Check events
kubectl describe pod/tracardi-xxx

# Increase startup time
failureThreshold: 20  # 100s startup time
```

### Pod not receiving traffic

**Possible causes**:
- Readiness probe failing
- Dependencies unhealthy

**Solution**:
```bash
# Check readiness
kubectl get pod tracardi-xxx -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}'

# Test endpoint manually
kubectl port-forward pod/tracardi-xxx 8686:8686
curl http://localhost:8686/ready
```

### Slow shutdown

**Possible causes**:
- Connections not closing cleanly
- terminationGracePeriodSeconds too short

**Solution**:
```yaml
terminationGracePeriodSeconds: 60  # Increase if needed
```

## Monitoring

### Prometheus Metrics (Future Enhancement)

```prometheus
# Health check duration
tracardi_health_check_duration_seconds{component="elasticsearch"}
tracardi_health_check_duration_seconds{component="mysql"}
tracardi_health_check_duration_seconds{component="redis"}

# Health check status
tracardi_health_check_status{component="elasticsearch"} 1  # 1=healthy, 0=unhealthy

# Shutdown duration
tracardi_shutdown_duration_seconds
```

### Logging

All health checks and shutdown events are logged:

```
2026-01-12 10:30:00 [INFO] Received SIGTERM signal, initiating graceful shutdown...
2026-01-12 10:30:00 [INFO] Running cleanup: close_elasticsearch
2026-01-12 10:30:01 [INFO] ✓ Elasticsearch connections closed
2026-01-12 10:30:01 [INFO] Running cleanup: close_mysql
2026-01-12 10:30:01 [INFO] ✓ MySQL connections closed
2026-01-12 10:30:01 [INFO] Running cleanup: close_redis
2026-01-12 10:30:02 [INFO] ✓ Redis connections closed
2026-01-12 10:30:02 [INFO] Graceful shutdown completed
```

## Best Practices

1. **Always use readiness probe** for production
2. **Set appropriate timeouts** based on your infrastructure
3. **Use startupProbe** for slow-starting applications
4. **Configure terminationGracePeriodSeconds** >= longest request timeout
5. **Monitor health check metrics** in production
6. **Test shutdown behavior** in staging environment

## Testing

### Manual Testing

```bash
# Test liveness
curl http://localhost:8686/health

# Test readiness
curl http://localhost:8686/ready

# Test graceful shutdown
kubectl delete pod tracardi-xxx --grace-period=30
kubectl logs -f tracardi-xxx  # Watch shutdown logs
```

### Load Testing

```bash
# Generate traffic during pod termination
while true; do curl http://tracardi/api/test; sleep 0.1; done &

# Terminate pod
kubectl delete pod tracardi-xxx

# Should see zero failed requests during shutdown
```

## Migration Guide

### For Existing Deployments

1. **Update Tracardi** to version with health probes
2. **Add health check endpoints** to deployment YAML
3. **Configure terminationGracePeriodSeconds**
4. **Deploy with rolling update strategy**
5. **Monitor for any issues**

### Breaking Changes

**None** - This is a backward-compatible addition.

## Contributing

Improvements welcome! Areas for enhancement:
- Additional health checks (e.g., disk space, memory)
- Prometheus metrics integration
- Custom probe configurations
- Advanced shutdown strategies

## License

Same as Tracardi (MIT with Common Clause).

## References

- [Kubernetes Liveness, Readiness and Startup Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- [Kubernetes Pod Lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)
- [Graceful Shutdown in Kubernetes](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#pod-termination)
