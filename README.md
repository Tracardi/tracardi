# Tracardi Customer Data Platform
Tracardi is a Graphic User Interface based on Apache Unomi.
Unomi is an open source Customer Data Platform that allows anyone to collect user profiles and manage them in a very robust way.

# Installation

## Docker build
docker build . -t tracardi-free

## Set connection to elastic and unomi

Edit docker-compose.yaml and set connection to elastic and unomi.


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

