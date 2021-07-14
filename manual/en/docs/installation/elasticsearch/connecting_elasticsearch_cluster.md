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

