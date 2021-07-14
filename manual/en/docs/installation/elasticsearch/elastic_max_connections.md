# Max connections to elastic

By default there are open up to 10 connections to each node, 
if you require more  calls the ELASTIC_MAX_CONN parameter to raise the limit:

Add the following to Tracardi configuration.

```yaml
    ELASTIC_MAX_CONN: 10
```