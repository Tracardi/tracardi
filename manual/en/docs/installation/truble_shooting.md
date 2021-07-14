#### Address already in use

If you experience:

```
ERROR: for tracardi_tracardi_1  Cannot start service 
tracardi: driver failed programming external connectivity 
on endpoint tracardi_tracardi_1 
Error starting userland proxy: listen tcp4 0.0.0.0:80: 
bind: address already in use
``` 

That means you have something running on port 80. Change docker-compose.yaml to map 
Tracardi to different port.

```yaml
  tracardi:
    build: .
    environment:
      ELASTIC_HOST: elasticsearch
      ELASTIC_PORT: 9200
    ports:
      - 8081:80  <- CHANGE HERE
    depends_on:
      - unomi
      - elasticsearch
```

