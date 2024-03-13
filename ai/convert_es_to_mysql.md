You must convert a Elasticsearch (ES) mapping to python script that uses the SQLAlchemy to create a MySQL Table. To do
this in the section `Elasticsearch table mapping` you will get a mapping form Elastic search. It wil look like this:

```json
{
  "mappings": {
    "properties": {
      "name": {
        "type": "text"
      },
      "age": {
        "type": "integer"
      },
      "address": {
        "properties": {
          "street": {
            "type": "text",
            "ignore_above": 64
          },
          "city": {
            "type": "text"
          }
        }
      },
      "tags": {
        "type": "keyword"
      },
      "external_id": {
        "type": "keyword"
      }
    }
  }
}
```

It defines all available fields in ES index. This mapping creates the following field.

- name
- age
- address.street
- address.city
- tags

Some fields are embedded like `address.street`. Each field has a data type. For example "type": "keyword".
Map elastic data types to Mysql datatypes so it matches the Mysql datatypes the following way:

keyword - varchar
text - varchar
date - datetime
number - integer
float - float
object - json
flattended - json
boolean - BOOLEAN
binary - BLOB

if there is no mapping come up with the closest type that you think will fit.

Your task is to create a SQLAlchemy python script that creates a MySQL Table based on the provided Elasticsearch mapping
in a section `Elasticsearch table mapping`. Mapping should be converted to a SQlAlchemy code this way that all fields
should be available in the table. Embedded fields like address.street should be converted to address_street.
Table name should be taken from `Elasticsearch index name` section.

If there is `ignore_above` use this value to set max string length. If the field name indicates that this is and id, eg.
flow_id then convert it to `String(40)`. If there is `id` field convert it to: `id = Column(String(40), primary_key=True)`. 
If there is no `ignore_above` for string values like text or keyword make the max length 255. If there is "null_value"
use it as default field value. 
Convert all mapping do not left any field unconverted event if there is like 100
fields. All fields must be in the script so it can be executed just by coping it.

Expected result of such converted script for example above and `Elasticsearch index name` set to `my_index` could look
like
this:

```python

from sqlalchemy import Column, Integer, String, DateTime, Float, PrimaryKeyConstraint, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class MyIndexTable(Base):
    __tablename__ = 'my_index'

    id = Column(String(40))  # No primary key
    tenant = Column(String(40))  # Add this field for multitenance
    production = Column(Boolean) # Add this field for multitenance
    name = Column(String(128))  # Elasticsearch 'text' type is similar to MySQL 'VARCHAR'. Name field should have always 128
    age = Column(Integer)  # 'integer' in ES is the same as in MySQL
    address_street = Column(
        String(64))  # Nested 'text' fields converted to 'VARCHAR', and ignore_above set as max String length
    address_city = Column(String(255))
    tags = Column(String(255))  # 'keyword' type in ES corresponds to 'VARCHAR' in MySQL
    external_id = Column(String(40))  # Always 40 char string

    # Notice that all fields are converted.
    
    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant', 'production'),
    )

```

Do not write any explanation only full code.

# Elasticsearch index name

settings

# Elasticsearch index mapping

```json
{
  "settings": {
    "number_of_shards": %%CONF_SHARDS%%,
    "number_of_replicas": %%REPLICAS%%
  },
  "mappings": {
    "_meta": {
      "version": "%%VERSION%%",
      "name": "%%PREFIX%%"
    },
    "dynamic": "strict",
    "properties": {
      "id": {
        "type": "keyword",
        "ignore_above": 48
      },
      "timestamp": {
        "type": "date"
      },
      "name": {
        "type": "keyword"
      },
      "description": {
        "type": "text"
      },
      "type": {
        "type": "keyword"
      },
      "enabled": {
        "type": "boolean"
      },
      "content": {
        "type": "object",
        "dynamic": "true",
        "enabled": false
      },
      "config": {
        "type": "flattened"
      }
    }
  },
  "aliases": {
    "%%ALIAS%%": {}
  }
}


```