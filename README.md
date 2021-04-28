# Tracardi Customer Data Platform

[Tracardi](http://www.tracardi.com) is a Graphic User Interface based on [Apache Unomi](https://unomi.apache.org).

Unomi is an open source Customer Data Platform that allows anyone to collect user profiles and manage them in a very robust way.

# Installation

In order to run tracardi you must have docker installed on your linux machine. Please refer to [docker installation manual](https://docs.docker.com/engine/install/) 
to see how to install docker. 

One the docker is installed run go to main folder of tracardi and run.

```
docker-compose build
docker-compose up
```

This will build and install tracardi and all required dependencies such as unomi and elastic on your computer.

After a while when everything is downloaded and installed open browser and go to http://0.0.0.0/app
Login with default:

```
 user: karaf
 password: karaf
```

## Tracardi without unomi and eleastic

When you have unomi and elastic already installed you can use a standalone version of tracardi.
File docker-standalone.yaml has everything you need. 

Edit docker-standalone.yaml and set connection to elastic and unomi.


```yaml
      UNOMI_PROTOCOL: http
      UNOMI_HOST: <unomi-ip-address>
      UNOMI_PORT: <unomi-port, either 8181 or 9443>
      UNOMI_USERNAME: <unomi-username>
      UNOMI_PASSWORD: <unomi-password>
      ELASTIC_HOST: <elastic-ip-address>
      ELASTIC_PORT: 9200
```

To start tracardi, run this command from the same directory where the docker-standalone.yaml file exists:

```
docker-compose -f docker-standalone.yaml up
```

## User interface
Open browser and go to http://0.0.0.0/app

Login with:

* UNOMI_USERNAME (default: karaf) and 
* UNOMI_PASSWORD(default: karaf)


## Trouble shooting

If you experience:

```
ERROR: for tracardi_tracardi_1  Cannot start service 
tracardi: driver failed programming external connectivity 
on endpoint tracardi_tracardi_1 
Error starting userland proxy: listen tcp4 0.0.0.0:80: 
bind: address already in use
``` 

That means you have something running on port 80. Change docker-compose.yaml to map tracardi to different port.

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

And open browser and do to url:

```yaml
http://0.0.0.0:8081/app
```