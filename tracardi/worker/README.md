# Running worker docker

```
docker run -e REDIS_HOST=redis://<redis-ip>:6379 -d tracardi/worker:0.9.0-dev
```

REDIS_HOST=192.168.1.110 ELASTIC_VERIFY_CERTS=no ELASTIC_HOST=http://192.168.1.110:9200 celery -A tracardi.worker.celery_worker worker -l info -E
REDIS_HOST=192.168.1.123 ELASTIC_VERIFY_CERTS=no ELASTIC_HOST=https://192.168.1.123:9200 celery -A tracardi.worker.celery_worker worker -l info -E

REDIS_HOST=192.168.1.110 ELASTIC_VERIFY_CERTS=no ELASTIC_HOST=http://192.168.1.110:9200 huey_consumer.py -q tracardi.worker.worker.queue



# Run worker as docker

```bash
docker run \
-e ELASTIC_HOST=http://192.168.1.110:9200 \
-e REDIS_HOST=redis://192.168.1.110:6379 \
-e LOGGING_LEVEL=info \
tracardi/worker:0.9.0-dev
```