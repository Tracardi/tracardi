# Running worker docker

```
docker run -e REDIS_HOST=redis://<redis-ip>:6379 -d tracardi/worker:0.8.0.-dev
```