# Tracardi Customer Data Platform

[Tracardi](http://www.tracardi.com)  is the Customer Data Platform


## Features

 
 
## Screenshots

### Browsing events

![Screenshot 1](https://github.com/atompie/tracardi/raw/0.4.0-dev/screenshots/main.png)

### Workflow of consumer data collection and enhancement 

![Workflow](https://pbs.twimg.com/media/E3WHL7nWUAA7men?format=jpg&name=large)

### Trigger rules

![Screenshot 2](https://github.com/atompie/tracardi/raw/0.4.0-dev/screenshots/main1.png)

### Editing plugins

![Screenshot 3](https://pbs.twimg.com/media/E4FqslsVEAgRS6d?format=jpg&name=large)

## Video introduction

[YOUTUBE Tracardi](https://www.youtube.com/channel/UC0atjYqW43MdqNiSJBvN__Q)



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
