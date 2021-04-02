# Installation

## Docker build
docker build . -t tracardi-free

## Set connection to elastic and unomi

Edit docer-compose.yaml and set connection to elastic and unomi.


```
      UNOMI_PROTOCOL: http
      UNOMI_HOST: 192.168.1.1
      UNOMI_PORT: 8181
      UNOMI_USERNAME: karaf
      UNOMI_PASSWORD: karaf
      ELASTIC_HOST: 192.168.1.1
      ELASTIC_PORT: 9200
```

## Run docker compose
docker-compose up

## Open browser
Open browser and go to http://0.0.0.0/app

Login with:

* UNOMI_USERNAME (default: karaf) and 
* UNOMI_PASSWORD(default: karaf)

