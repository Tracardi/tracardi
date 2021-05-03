[![header.jpg](https://i.postimg.cc/9XRJYRqY/header.jpg)](https://postimg.cc/23YQz5G1)

[![Tests of Tracardi 0.3.0-dev](https://github.com/atompie/tracardi/actions/workflows/python-package.yml/badge.svg?branch=master)](https://github.com/atompie/tracardi/actions/workflows/python-package.yml)

# Tracardi Customer Data Platform

[Tracardi](http://www.tracardi.com)  is a Graphic User Interface based on [Apache Unomi](https://unomi.apache.org).
Unomi is an open-source Customer Data Platform that allows anyone to collect user-profiles and manage them in a very robust way.

# Installation

In order to run [Tracardi](http://www.tracardi.com) you must have docker installed on your linux machine. Please refer to [docker installation manual](https://docs.docker.com/engine/install/) 
to see how to install docker. 

Once the docker is installed go to main folder of tracardi and run.

```
docker-compose build
docker-compose up
```

This will build and install tracardi and all required dependencies such as unomi and elastic on your computer. 
Hence that this type of setup is for demonstration purpose only.

# Running Tracardi

After a while when everything is downloaded and installed open browser and go to http://0.0.0.0/app
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

#### Nof found exception

If you see error in source section similar to this screenshot:

[![source_error](https://i.postimg.cc/qvNDnF20/scope-error.png)](https://i.postimg.cc/qvNDnF20/scope-error.png)

This can be ignored. Once you create first source it disapears. Next version will display information about empty source index.

#### Authentication Exception

If you experience Authentication Error 

[![Auth_exception](https://i.postimg.cc/y6WL25rR/auth-exception.png)](https://i.postimg.cc/y6WL25rR/auth-exception.png)

This means there is something wrong with the connection to elastic search. 
Please take a close look at Tracardi configuration. You probably need to provide username and password for elastic search connection. 

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
      ELASTIC_HOST: https://user:name@elastic-search-ip:443  <- change here
    ports:
      - 80:80  
    depends_on:
      - unomi
      - elasticsearch
```

If you still experience problems with connection to elastic search, below you can find the section on how to configure a connection to elastic search cluster. 

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


# Support us

If you would like to support us please follow us on [Facebook](https://www.facebook.com/TRACARDI/) or [Twitter](https://twitter.com/tracardi), tag us and leave your comments. Subscribe to our [Youtube channel](https://www.youtube.com/channel/UC0atjYqW43MdqNiSJBvN__Q) to see development process and new upcoming features.

Spread the news about TRACARDI so anyone interested get to know TRACARDI.

We appreciate any help that helps make TRACARDI popular. 