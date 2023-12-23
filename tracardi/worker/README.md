# Running worker docker

```
docker run -e REDIS_HOST=redis://<redis-ip>:6379 -d tracardi/worker:0.9.0-dev
```

REDIS_HOST=192.168.1.107 ELASTIC_VERIFY_CERTS=no ELASTIC_HOST=http://192.168.1.107:9200 celery -A tracardi.worker.celery_worker worker -l info -E
REDIS_HOST=192.168.1.123 ELASTIC_VERIFY_CERTS=no ELASTIC_HOST=https://192.168.1.123:9200 celery -A tracardi.worker.celery_worker worker -l info -E