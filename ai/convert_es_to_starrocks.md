You must convert a Elasticsearch (ES) mapping to python script that uses the SQLAlchemy to create a StarRocks Table. To do
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
Map elastic data types to Starrocks datatypes so it matches the Starrocks datatypes the following way:

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

Your task is to create a SQLAlchemy python script that creates a Starrocks Table based on the provided Elasticsearch mapping
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
    name = Column(String(128))  # Elasticsearch 'text' type is similar to Starrocks 'VARCHAR'. Name field should have always 128
    age = Column(Integer)  # 'integer' in ES is the same as in Starrocks
    address_street = Column(
        String(64))  # Nested 'text' fields converted to 'VARCHAR', and ignore_above set as max String length
    address_city = Column(String(255))
    tags = Column(String(255))  # 'keyword' type in ES corresponds to 'VARCHAR' in Starrocks
    external_id = Column(String(40))  # Always 40 char string

    # Notice that all fields are converted.
    
    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant', 'production'),
    )

```

Do not write any explanation only full code.

# Elasticsearch index name

profile

# Elasticsearch index mapping

```json
{
  "index_patterns": [
    "%%TEMPLATE_PATTERN%%"
  ],
  "template": {
    "settings": {
      "number_of_shards": %%SHARDS%%,
      "number_of_replicas": %%REPLICAS%%,
      "index.mapping.total_fields.limit": 2000
    },
    "mappings": {
      "_meta": {
        "version": "%%VERSION%%",
        "name": "%%PREFIX%%"
      },
      "dynamic": "strict",
      "date_detection": false,
      "properties": {
        "id": {
          "type": "keyword",
          "ignore_above": 64
        },
        "ids": {
          "type": "keyword"
        },
        "metadata": {
          "properties": {
            "status": {
              "type": "keyword",
              "null_value": "NULL",
              "ignore_above": 32
            },
            "aux": {
              "type": "flattened"
            },
            "system": {
              "type": "flattened"
            },
            "fields": {
              "type": "object",
              "enabled": false
            },
            "time": {
              "properties": {
                "insert": {
                  "type": "date",
                  "format": "yyyy-MM-dd HH:mm:ss||strict_date_optional_time ||epoch_millis"
                },
                "create": {
                  "type": "date",
                  "format": "yyyy-MM-dd HH:mm:ss||strict_date_optional_time ||epoch_millis"
                },
                "update": {
                  "type": "date",
                  "format": "yyyy-MM-dd HH:mm:ss||strict_date_optional_time ||epoch_millis"
                },
                "segmentation": {
                  "type": "date",
                  "format": "yyyy-MM-dd HH:mm:ss||strict_date_optional_time ||epoch_millis"
                },
                "visit": {
                  "properties": {
                    "last": {
                      "type": "date",
                      "format": "yyyy-MM-dd HH:mm:ss||strict_date_optional_time ||epoch_millis"
                    },
                    "current": {
                      "type": "date",
                      "format": "yyyy-MM-dd HH:mm:ss||strict_date_optional_time ||epoch_millis"
                    },
                    "count": {
                      "type": "integer"
                    },
                    "tz": {
                      "type": "keyword"
                    }
                  }
                }
              }
            }
          }
        },
        "data": {
          "properties": {
            "anonymous": {
              "type": "boolean"
            },
            "media": {
              "properties": {
                "image": {
                  "type": "keyword"
                },
                "webpage": {
                  "type": "keyword"
                },
                "social": {
                  "properties": {
                    "twitter": {
                      "type": "keyword"
                    },
                    "facebook": {
                      "type": "keyword"
                    },
                    "youtube": {
                      "type": "keyword"
                    },
                    "instagram": {
                      "type": "keyword"
                    },
                    "tiktok": {
                      "type": "keyword"
                    },
                    "linkedin": {
                      "type": "keyword"
                    },
                    "reddit": {
                      "type": "keyword"
                    },
                    "other": {
                      "type": "flattened"
                    }
                  }
                }
              }
            },
            "pii": {
              "properties": {
                "firstname": {
                  "type": "keyword"
                },
                "lastname": {
                  "type": "keyword"
                },
                "display_name": {
                  "type": "keyword"
                },
                "birthday": {
                  "type": "date",
                  "format": "yyyy-MM-dd HH:mm:ss||strict_date_optional_time ||epoch_millis"
                },
                "language": {
                  "properties": {
                    "native": {
                      "type": "keyword"
                    },
                    "spoken": {
                      "type": "keyword"
                    }
                  }
                },
                "gender": {
                  "type": "keyword"
                },
                "education": {
                  "properties": {
                    "level": {
                      "type": "keyword"
                    }
                  }
                },
                "civil": {
                  "properties": {
                    "status": {
                      "type": "keyword"
                    }
                  }
                },
                "attributes": {
                  "properties": {
                    "height": {
                      "type": "float"
                    },
                    "weight": {
                      "type": "float"
                    },
                    "shoe_number": {
                      "type": "float"
                    }
                  }
                }
              }
            },
            "identifier": {
              "properties": {
                "id": {
                  "type": "keyword",
                  "ignore_above": 64
                },
                "badge": {
                  "type": "keyword",
                  "ignore_above": 64
                },
                "passport": {
                  "type": "keyword",
                  "ignore_above": 32
                },
                "credit_card": {
                  "type": "keyword",
                  "ignore_above": 24
                },
                "token": {
                  "type": "keyword",
                  "ignore_above": 96
                },
                "coupons": {
                  "type": "keyword",
                  "ignore_above": 32
                }
              }
            },
            "contact": {
              "properties": {
                "email": {
                  "properties": {
                    "main": {
                      "type": "keyword",
                      "ignore_above": 64
                    },
                    "private": {
                      "type": "keyword",
                      "ignore_above": 64
                    },
                    "business": {
                      "type": "keyword",
                      "ignore_above": 64
                    }
                  }
                },
                "phone": {
                  "properties": {
                    "main": {
                      "type": "keyword",
                      "ignore_above": 32
                    },
                    "business": {
                      "type": "keyword",
                      "ignore_above": 32
                    },
                    "mobile": {
                      "type": "keyword",
                      "ignore_above": 32
                    },
                    "whatsapp": {
                      "type": "keyword",
                      "ignore_above": 32
                    }
                  }
                },
                "app": {
                  "properties": {
                    "whatsapp": {
                      "type": "keyword"
                    },
                    "discord": {
                      "type": "keyword"
                    },
                    "slack": {
                      "type": "keyword"
                    },
                    "twitter": {
                      "type": "keyword"
                    },
                    "telegram": {
                      "type": "keyword"
                    },
                    "wechat": {
                      "type": "keyword"
                    },
                    "viber": {
                      "type": "keyword"
                    },
                    "signal": {
                      "type": "keyword"
                    },
                    "other": {
                      "type": "flattened"
                    }
                  }
                },
                "address": {
                  "properties": {
                    "town": {
                      "type": "keyword"
                    },
                    "county": {
                      "type": "keyword"
                    },
                    "country": {
                      "type": "keyword"
                    },
                    "postcode": {
                      "type": "keyword"
                    },
                    "street": {
                      "type": "keyword"
                    },
                    "other": {
                      "type": "keyword"
                    }
                  }
                },
                "confirmations": {
                  "type": "keyword"
                }
              }
            },
            "job": {
              "properties": {
                "position": {
                  "type": "keyword"
                },
                "salary": {
                  "type": "float"
                },
                "type": {
                  "type": "keyword"
                },
                "company": {
                  "properties": {
                    "name": {
                      "type": "keyword"
                    },
                    "size": {
                      "type": "keyword"
                    },
                    "segment": {
                      "type": "keyword"
                    },
                    "country": {
                      "type": "keyword"
                    }
                  }
                },
                "department": {
                  "type": "keyword"
                }
              }
            },
            "preferences": {
              "properties": {
                "purchases": {
                  "type": "keyword"
                },
                "colors": {
                  "type": "keyword"
                },
                "sizes": {
                  "type": "keyword"
                },
                "devices": {
                  "type": "keyword"
                },
                "channels": {
                  "type": "keyword"
                },
                "payments": {
                  "type": "keyword"
                },
                "brands": {
                  "type": "keyword"
                },
                "fragrances": {
                  "type": "keyword"
                },
                "services": {
                  "type": "keyword"
                },
                "other": {
                  "type": "keyword"
                }
              }
            },
            "devices": {
              "properties": {
                "push": {"type": "keyword", "ignore_above": 40},
                "other": {"type": "keyword", "ignore_above": 40},
                "last": {
                  "properties": {
                    "geo": {
                      "properties": {
                        "country": {
                          "properties": {
                            "name": {
                              "type": "keyword",
                              "ignore_above": 64
                            },
                            "code": {
                              "type": "keyword",
                              "ignore_above": 10
                            }
                          }
                        },
                        "county": {
                          "type": "keyword",
                          "ignore_above": 64
                        },
                        "city": {
                          "type": "keyword",
                          "ignore_above": 64
                        },
                        "latitude": {
                          "type": "float"
                        },
                        "longitude": {
                          "type": "float"
                        },
                        "location": {
                          "ignore_malformed": true,
                          "type": "geo_point"
                        },
                        "postal": {
                          "type": "keyword",
                          "ignore_above": 24
                        }
                      }
                    }
                  }
                }
              }
            },
            "metrics": {
              "properties": {
                "ltv": {
                  "type": "float"
                },
                "ltcosc": {
                  "type": "integer"
                },
                "ltcocc": {
                  "type": "integer"
                },
                "ltcop": {
                  "type": "float"
                },
                "ltcosv": {
                  "type": "float"
                },
                "ltcocv": {
                  "type": "float"
                },
                "next": {
                  "type": "date",
                  "format": "yyyy-MM-dd HH:mm:ss||strict_date_optional_time ||epoch_millis"
                },
                "custom": {
                  "type": "object",
                  "dynamic": "true"
                }
              }
            },
            "loyalty": {
              "properties": {
                "codes": {
                  "type": "keyword"
                },
                "card": {
                  "properties": {
                    "id": {
                      "type": "keyword", "ignore_above": 64
                    },
                    "name": {
                      "type": "keyword"
                    },
                    "issuer": {
                      "type": "keyword"
                    },
                    "points": {
                      "type": "float"
                    },
                    "expires": {
                      "type": "date",
                      "format": "yyyy-MM-dd HH:mm:ss||strict_date_optional_time ||epoch_millis"
                    }
                  }
                }
              }
            }
          }
        },
        "stats": {
          "type": "flattened"
        },
        "traits": {
            "dynamic": "true",
            "type": "object"
        },
        "collections": {
          "type": "nested"
        },
        "segments": {
          "type": "keyword",
          "ignore_above": 64
        },
        "consents": {
          "type": "flattened"
        },
        "active": {
          "type": "boolean"
        },
        "interests": {
          "type": "flattened"
        },
        "aux": {
          "type": "flattened"
        },
        "trash": {
          "type": "flattened"
        },
        "misc": {
          "type": "object",
          "enabled": false
        }
      }
    },
    "aliases": {
      "%%ALIAS%%": {}
    }
  }
}


```

CAUTION: This is very important, all fields must be remapped. This must be a complete ready to use Table. 