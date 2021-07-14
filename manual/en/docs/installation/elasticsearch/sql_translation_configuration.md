# Elasticsearch SQL translation configuration

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