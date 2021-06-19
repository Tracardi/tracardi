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
      UNOMI_PROTOCOL: http
      UNOMI_HOST: unomi
      UNOMI_PORT: 8181
      UNOMI_USERNAME: karaf
      UNOMI_PASSWORD: karaf
      ELASTIC_HOST: elasticsearch
      ELASTIC_PORT: 9200
    ports:
      - 8081:80  <- CHANGE HERE
    depends_on:
      - unomi
      - elasticsearch
```

#### Not found exception

If you see error in source section similar to this screenshot:

[![source_error](https://i.postimg.cc/qvNDnF20/scope-error.png)](https://i.postimg.cc/qvNDnF20/scope-error.png)

This can be ignored. Once you create first source it disappears. Next version of Tracardi will 
display alert about empty source index. Currently we are not enforcing creation of empty indexes. 
Index is created with the first created record. 

#### Authentication Exception

If you experience Authentication Error please take a closer look at the Tracardi configuration. 
You probably need to provide a username and password for an elastic-search connection. 


File docker-standalone.yaml
```yaml
  tracardi:
    build: .
    environment:
      UNOMI_PROTOCOL: http
      UNOMI_HOST: unomi
      UNOMI_PORT: 8181
      UNOMI_USERNAME: karaf
      UNOMI_PASSWORD: karaf
      ELASTIC_HOST: https://user:name@elastic-search-ip:443  <- change here for ssl connection
    ports:
      - 80:80  
    depends_on:
      - unomi
      - elasticsearch
```
For unencrypted connection set ELASTIC_HOST in docker-standalone.yaml to:

```yaml
  tracardi:
    ...
    environment:
      ELASTIC_HOST: user:name@elastic-search-ip:9200
    ...
```

If you still experience problems with connection to elastic search, you can find the section on how to configure a connection to elastic search cluster below. 
