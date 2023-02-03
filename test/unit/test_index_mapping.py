from tracardi.config import tracardi
from tracardi.domain.storage.index_mapping import IndexMapping
from tracardi.service.storage.index import Index

mapping_mock = {
    "tracardi-event-2022-2": {
        "mappings": {
            "dynamic": "false",
            "properties": {
                "aux": {
                    "type": "object",
                    "dynamic": "true"
                },
                "id": {
                    "type": "keyword"
                },
                "metadata": {
                    "properties": {
                        "debugged": {
                            "type": "boolean"
                        },
                        "processed_by": {
                            "properties": {
                                "rules": {
                                    "type": "keyword"
                                },
                                "third_party": {
                                    "type": "keyword"
                                }
                            }
                        },
                        "profile_less": {
                            "type": "boolean"
                        },
                        "status": {
                            "type": "keyword",
                            "null_value": "NULL"
                        },
                        "aux": {
                            "type": "flattened"
                        },
                        "time": {
                            "properties": {
                                "insert": {
                                    "type": "date"
                                }
                            }
                        }
                    }
                },
                "profile": {
                    "properties": {
                        "id": {
                            "type": "keyword"
                        }
                    }
                },
                "properties": {
                    "type": "object",
                    "dynamic": "true"
                },
                "session": {
                    "properties": {
                        "duration": {
                            "type": "float"
                        },
                        "id": {
                            "type": "keyword"
                        },
                        "start": {
                            "type": "date"
                        }
                    }
                },
                "source": {
                    "properties": {
                        "id": {
                            "type": "keyword"
                        }
                    }
                },
                "tags": {
                    "properties": {
                        "count": {
                            "type": "double"
                        },
                        "values": {
                            "type": "keyword"
                        }
                    }
                },
                "type": {
                    "type": "keyword",
                    "null_value": "NULL"
                }
            }
        }
    }
}


def test_index_mapping():
    im = IndexMapping(mapping_mock)

    assert im.get_field_names() == ['aux', 'id', 'metadata.debugged', 'metadata.processed_by.rules',
                                    'metadata.processed_by.third_party', 'metadata.profile_less', 'metadata.status',
                                    'metadata.aux', 'metadata.time.insert', 'profile.id', 'properties',
                                    'session.duration', 'session.id', 'session.start', 'source.id', 'tags.count',
                                    'tags.values', 'type']


def test_index_prefixing():
    index = Index(multi_index=False, index="index-name", mapping=mapping_mock, aliased=True)
    alias = index.get_index_alias()
    assert alias == f"{tracardi.version.name}.{index.index}"

    alias = index.get_index_alias(prefix="prefix")
    assert alias == f"prefix.{index.index}"
