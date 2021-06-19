# Tracardi Customer Data Platform

[Tracardi](http://www.tracardi.com)  is a Graphic User Interface based on [Apache Unomi](https://unomi.apache.org).
Unomi is an open-source Customer Data Platform that allows anyone to collect user-profiles and manage them in a very robust way.



## Features

 
 
## Screenshots

![Screenshot 1](https://scontent.fpoz4-1.fna.fbcdn.net/v/t1.6435-9/176281298_116889430506445_8902050899484618905_n.png?_nc_cat=103&ccb=1-3&_nc_sid=730e14&_nc_ohc=qehNGVOamjoAX8JKEXJ&_nc_ht=scontent.fpoz4-1.fna&oh=9419256671a7058fac91911c447e73a5&oe=60ADAEC3)

Browsing events

![Screenshot 2](https://scontent.fpoz4-1.fna.fbcdn.net/v/t1.6435-9/175559890_116889497173105_1808472980796796178_n.png?_nc_cat=111&ccb=1-3&_nc_sid=730e14&_nc_ohc=oJ3KuoD5VRUAX8DfexE&_nc_oc=AQmE0kCdaLRYwJYtc9HQRLJlPNSl-zBxxi7tG4hv7sZTuInCc0rBZtleTf3sTh_EmoY&_nc_ht=scontent.fpoz4-1.fna&oh=39a60c561d5f27c4e7f04863650ae2d3&oe=60AE3690)

Editing rules

## Video introduction

[YOUTUBE Tracardi](https://www.youtube.com/channel/UC0atjYqW43MdqNiSJBvN__Q)


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

# Open source version of Frontend

This repository comes with compiled version of react scripts. If you want to self compile the frontend 
scripts head to https://github.com/atompie/tracardi-unomi-gui.



# Donate

You can support us on [BOUNTY-SOURCE](https://www.bountysource.com/teams/tracardi)
