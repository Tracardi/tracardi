# Running worker docker

```
docker run -e REDIS_HOST=redis://<redis-ip>:6379 -d tracardi/worker:0.8.1
```

REDIS_HOST=localhost ELASTIC_VERIFY_CERTS=no ELASTIC_HOST=http://locahost:9200 celery -A worker.celery_worker worker -l info -E