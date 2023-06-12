# Running worker docker

```
docker run -e REDIS_HOST=redis://<redis-ip>:6379 -d tracardi/worker:0.8.1
```

REDIS_HOST=192.168.1.101 ELASTIC_VERIFY_CERTS=no ELASTIC_HOST=http://192.168.1.101:9200 celery -A tracardi.worker.celery_worker worker -l info -E