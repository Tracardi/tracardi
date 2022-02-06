from pprint import pprint


class IndexMapping:

    def __init__(self, mapping):
        self.mapping = mapping
        self.field_collection = {}

    def _flatten_dict(self, data, keystring=''):
        if type(data) == dict and len(data) > 0:
            keystring = keystring + '.' if keystring else keystring
            for k in data:
                yield from self._flatten_dict(data[k], keystring + str(k))
        else:
            yield keystring, data

    def get_field_names(self):
        for index, mapping in self.mapping.items():
            self._get_field_names(mapping['mappings'], self.field_collection)
        return [k for k, v in self._flatten_dict(self.field_collection)]

    def _get_field_names(self, mapping, collection):
        for data, fields in mapping.items():
            if data == 'properties':
                for field in fields.keys():
                    collection[field] = {}
                    self._get_field_names(fields[field], collection[field])



if __name__ == "__main__":
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
                            "ip": {
                                "type": "keyword",
                                "null_value": "NULL"
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

    print(im.get_field_names())
    pprint(im.field_collection)


