[![header.jpg](https://i.postimg.cc/9XRJYRqY/header.jpg)](https://postimg.cc/23YQz5G1)

[![Tests of Tracardi 0.3.0-dev](https://github.com/atompie/tracardi/actions/workflows/python-package.yml/badge.svg?branch=master)](https://github.com/atompie/tracardi/actions/workflows/python-package.yml)

# Tracardi Customer Data Platform

[Tracardi](http://www.tracardi.com)  is a Graphic User Interface based on [Apache Unomi](https://unomi.apache.org).
Unomi is an open-source Customer Data Platform that allows anyone to collect user-profiles and manage them in a very robust way.

This repository contains source for tracardi-unomi-api. You must run it with [https://github.com/atompie/tracardi-unomi-gui] 
to see the frontend. 

# Installation

In order to run [Tracardi](http://www.tracardi.com) you must have docker installed on your linux machine. Please refer to [docker installation manual](https://docs.docker.com/engine/install/) 
to see how to install docker. 

Once the docker is installed go to main folder of tracardi and run.

```
git clone https://github.com/atompie/tracardi.git
docker-compose build
docker-compose up
```

This will build and install Tracardi and all required API dependencies such as unomi and elastic on your computer. 
Hence that this type of setup is for demonstration purpose only.

If you do not have docker-compose installed you can run it one by one:
You will need for that your laptop IP. On linux machine you may run ifconfig or other similar command to get IP. 
Then replace ```<your-laptop-ip>``` with that IP

###Start Elasticsearch
```
docker run -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch:7.5.2
```

###Start Unomi
Remember to replace ```<your-laptop-ip>``` with IP

```
docker run -p 8181:8181 -p 9443:9443 -p 8102:8102 -e UNOMI_ELASTICSEARCH_ADDRESSES=<your-laptop-ip>:9200 \
      -e ELASTICSEARCH_PORT=9300 apache/unomi:1.5.4
```

###Start Tracardi API
Remember to replace ```<your-laptop-ip>``` with IP

```
git clone https://github.com/atompie/tracardi.git
docker build . -t tracardi-unomi-api
docker run -p 8686:80 -e UNOMI_PROTOCOL=http -e UNOMI_HOST=<your-laptop-ip> -e UNOMI_PORT=8181 \
       -e UNOMI_USERNAME=karaf -e UNOMI_PASSWORD=karaf -e ELASTIC_HOST=http://<your-laptop-ip>:9200 \
        tracardi-unomi-api
```

# Test if Tracardi API is running

Go to http://localhost:8686/docs and see if you get the API documentation


# Running Tracardi GUI

Now its time to run Frontend.

```
git clone https://github.com/atompie/tracardi-unomi-gui.git
docker build . -t tracardi-unomi-gui
docker run -p 80:80 -e API_URL=http://127.0.0.1:8686 tracardi-unomi-gui
```


After a while when everything is downloaded and installed open browser and go to http://127.0.0.1
Login with default:

```
 user: karaf
 password: karaf
```

## User interface authentication
Default user and password are configured in a docker compose file:

* UNOMI_USERNAME (default: karaf) and 
* UNOMI_PASSWORD(default: karaf)

Access to Tracardi interface is restricted by the Unomi password. 
If you change Unomi password you will have to change it in Tracardi 
as well.

## Features

Tracardi allows for:

 * **Customer Data Integration** - You can ingest, aggregate and store customer data
   from multiple sources in real time at any scale and speed due to elastic search backend.
   
 * **Customer Data Modelling** -  You can manage data. Define rules that will model data delivered
   from your page and copy it into user profile. You can segment customers into custom segments.
   
 * **User Experience Personalization** - You can personalize user experience with
   real-time customer segmentation and targeting.
   
 * **Profile Unification** - You can merge customer data from various sources to
   single profile. Auto de-duplicate customer records. Blend customers in one account.
   
 * **Automation** - TRACARDI is a great framework for creating
   marketing automation apps. You can send your data to other systems easily
 
 
## Screenshots

![Screenshot 1](https://scontent.fpoz4-1.fna.fbcdn.net/v/t1.6435-9/176281298_116889430506445_8902050899484618905_n.png?_nc_cat=103&ccb=1-3&_nc_sid=730e14&_nc_ohc=qehNGVOamjoAX8JKEXJ&_nc_ht=scontent.fpoz4-1.fna&oh=9419256671a7058fac91911c447e73a5&oe=60ADAEC3)

Browsing events

![Screenshot 2](https://scontent.fpoz4-1.fna.fbcdn.net/v/t1.6435-9/175559890_116889497173105_1808472980796796178_n.png?_nc_cat=111&ccb=1-3&_nc_sid=730e14&_nc_ohc=oJ3KuoD5VRUAX8DfexE&_nc_oc=AQmE0kCdaLRYwJYtc9HQRLJlPNSl-zBxxi7tG4hv7sZTuInCc0rBZtleTf3sTh_EmoY&_nc_ht=scontent.fpoz4-1.fna&oh=39a60c561d5f27c4e7f04863650ae2d3&oe=60AE3690)

Editing rules

## Video introduction

[YOUTUBE Tracardi](https://www.youtube.com/channel/UC0atjYqW43MdqNiSJBvN__Q)

## Trouble shooting

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

## Tracardi without unomi and eleastic

When you have unomi and elastic already installed you can use a 
standalone version of Tracardi. This is usually a production type of configuration. 

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

To start Tracardi, run this command from the same directory where the docker-standalone.yaml file exists:

```
docker-compose -f docker-standalone.yaml up
```

## Advanced configuration

### Long running service

Tracardi can be configured to inspect the elastic state to get 
a list of nodes upon startup, periodically and/or on failure. 

To do that add the following to Tracardi configuration. 
I hope the config is self-explanatory

```yaml
    ELASTIC_SNIFFER_TIMEOUT: 60,
    ELASTIC_SNIFF_ON_START: True,
    ELASTIC_SNIFF_ON_CONNECTION_FAIL: True,
```

### Max connections to elastic

By default there are open up to 10 connections to each node, 
if you require more  calls the ELASTIC_MAX_CONN parameter to raise the limit:

Add the following to Tracardi configuration.

```yaml
    ELASTIC_MAX_CONN: 10
```


## Connecting to elastic cluster

To connect to elastic cluster you must provide location to all cluster nodes.
To configure Tracardi connection to elastic change ELASTIC_HOST in docker-standalone.yaml file.

```yaml
    ELASTIC_HOST: "node-1,node-2,node-3"
```
 
### SSL and Authentication
You can configure Tracardi to use SSL for connecting to your 
elasticsearch cluster:

```yaml
    ELASTIC_HOST: "node-1,node-2,node-3",
    ELASTIC_PORT: 443,
    ELASTIC_SCHEME: "https",
    ELASTIC_HTTP_AUTH_USERNAME: "user",
    ELASTIC_HTTP_AUTH_PASSWORD: "pass",
```

or you can use RFC-1738 to specify the url:

```yaml
    ELASTIC_HOST: "https://user:secret@node-1:443,https://user:secret@node-2:443,https://user:secret@node-3:443"
```

To include certificate verification and HTTP auth if needed add the following line:

```yaml
    ELASTIC_CAFILE: "path to certificate",
```

### Connect using API_KEY

Here is the configuration for connection with API_KEY

```yaml
    ELASTIC_HOST: "site-1.local,site-2,site-3.com",
    ELASTIC_HTTP_AUTH_USERNAME: "user",
    ELASTIC_HTTP_AUTH_PASSWORD: "pass",
    ELASTIC_API_KEY: 'api-key',
```

### Connect using CLOUD_ID

Here is the configuration for connection with CLOUD_ID

```yaml
    ELASTIC_HOST: "site-1.local,site-2,site-3.com",
    ELASTIC_CLOUD_ID: 'cluster-1:dXMa5Fx...',
```

### Other connection types

If there is a need for more advanced connection configuration the change in /app/globals/elastic_client.py
should handle all mare advanced connection types from Tracardi to elastic. 


## SQL translation configuration

Some cloud providers have different Elastic Search _sql/translate endpoints.
AWS use its own endpoint so there may be a need to change how Tracardi queries elastic search.
To set new SQL translate endpoint add additional variable in docker 
compose file. 

```yaml
  tracardi:
    ...
    environment:
      ELASTIC_SQL_TRANSLATE_URL: "/_opendistro/_sql/translate"
    ...
```

If there is a need for a change of default "POST" SQL translation method add:

```yaml
  tracardi:
    ...
    environment:
      ELASTIC_SQL_TRANSLATE_METHOD: "PUT"
    ...
```

# Support us

If you would like to support us please follow us on [Facebook](https://www.facebook.com/TRACARDI/) or [Twitter](https://twitter.com/tracardi), tag us and leave your comments. Subscribe to our [Youtube channel](https://www.youtube.com/channel/UC0atjYqW43MdqNiSJBvN__Q) to see development process and new upcoming features.

Spread the news about TRACARDI so anyone interested get to know TRACARDI.

We appreciate any help that helps make TRACARDI popular. 