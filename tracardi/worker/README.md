# Running worker docker

docker run \
-e LICENSE=xxx \
-e ELASTIC_HOST=http://192.168.0.116:9200 \
-e REDIS_HOST=redis://192.168.0.116:6379 \
-e MYSQL_HOST=192.168.0.116 \
-e PULSAR_HOST=pulsar://192.168.0.116:6650 \
-e PULSAR_API=http://192.168.0.116:8080 \
-e LOGGING_LEVEL=info \
tracardi/init:2.0.0


docker run \
-e LICENSE=xxx \
-e ELASTIC_HOST=http://192.168.0.116:9200 \
-e REDIS_HOST=redis://192.168.0.116:6379 \
-e MYSQL_HOST=192.168.0.116 \
-e PULSAR_HOST=pulsar://192.168.0.116:6650 \
-e PULSAR_API=http://192.168.0.116:8080 \
-e LOGGING_LEVEL=info \
tracardi/background-worker:2.0.0
```
