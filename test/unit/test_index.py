from tracardi.context import ServerContext, Context, get_context

with ServerContext(Context(production=False, tenant="namespace")):
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


    def test_index_set_prefix():
        with ServerContext(Context(production=False, tenant="namespace")):
            index = Index(multi_index=False, index="index-name", mapping=mapping_mock)
            index.set_version("8.8.8")
            assert index._version_prefix == '888'
            assert index._tenant_prefix == f"{get_context().tenant}."

