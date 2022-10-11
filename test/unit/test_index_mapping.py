from tracardi.domain.storage.index_mapping import IndexMapping


def test_index_mapping():
    im = IndexMapping({
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
                            "time": {
                                "properties": {
                                    "insert": {
                                        "type": "date"
                                    },
                                    "process_time": {
                                        "type": "float"
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
    })

    assert im.get_field_names() == ['aux', 'id', 'metadata.debugged', 'metadata.processed_by.rules',
                                    'metadata.processed_by.third_party', 'metadata.profile_less', 'metadata.status',
                                    'metadata.time.insert', 'metadata.time.process_time', 'profile.id', 'properties',
                                    'session.duration', 'session.id', 'session.start', 'source.id', 'tags.count',
                                    'tags.values', 'type']
