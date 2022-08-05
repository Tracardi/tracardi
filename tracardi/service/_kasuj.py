from collections import defaultdict
from pprint import pprint
from typing import Tuple

from dictdiffer import diff

import deepdiff
from deepdiff import Delta

mappings_prev = {
    "dynamic": False,
    "date_detection": False,
    "properties": {
        "id": {
            "type": "keyword"
        },
        "metadata": {
            "dynamic": False,
            "properties": {
                "time": {
                    "properties": {
                        "insert": {
                            "type": "date"
                        },
                        "visit": {
                            "properties": {
                                "last": {
                                    "type": "date"
                                },
                                "current": {
                                    "type": "date"
                                },
                                "count": {
                                    "type": "integer"
                                }
                            }
                        }
                    }
                }
            }
        },
        "stats": {
            "dynamic": True,
            "type": "object"
        },
        "traits": {
            "properties": {
                "private": {
                    "dynamic": True,
                    "type": "object"
                },
                "public": {
                    "dynamic": True,
                    "type": "object"
                }
            }
        },
        "pii": {
            "dynamic": False,
            "properties": {
                "name": {
                    "type": "text"
                },
                "surname": {
                    "type": "text"
                },
                "birthDate": {
                    "type": "date"
                },
                "email": {
                    "type": "keyword"
                },
                "telephone": {
                    "type": "keyword"
                },
                "twitter": {
                    "type": "keyword"
                },
                "facebook": {
                    "type": "keyword"
                },
                "whatsapp": {
                    "type": "keyword"
                },
                "other": {
                    "dynamic": True,
                    "type": "object"
                }
            }
        },
        "segments": {
            "type": "keyword",
            "ignore_above": 64
        },
        "consents": {
            "dynamic": True,
            "type": "object"
        },
        "active": {
            "type": "boolean"
        }
    }
}

mappings_head = {
    "dynamic": False,
    "date_detection": False,
    "properties": {
        "id": {
            "type": "keyword"
        },
        "metadata": {
            "type": "object",
            "dynamic": True,
            "enabled": False,
        },
        "stats": {
            "dynamic": True,
            "type": "int"
        },
        "traits": {
            "properties": {
                "private": {
                    "dynamic": True,
                    "type": "object"
                },
                "public": {
                    "dynamic": True,
                    "type": "object"
                }
            }
        },
        "pii": {
            "dynamic": False,
            "properties": {
                "name": {
                    "type": "keyword"
                },
                "surname": {
                    "type": "text"
                },
                "birthDate": {
                    "type": "date"
                },
                "email": {
                    "type": "keyword"
                },
                "telephone": {
                    "type": "keyword"
                },
                "twitter": {
                    "type": "keyword"
                },
                "facebook": {
                    "type": "keyword"
                },
                "whatsapp": {
                    "type": "keyword"
                },
                "other": {
                    "dynamic": True,
                    "type": "object"
                }
            }
        },
        "segments": {
            "type": "keyword",
            "ignore_above": 64
        },
        "consents": {
            "dynamic": True,
            "type": "object"
        },
    }
}


class FieldMetaData:

    def __init__(self, type, sub_field):
        self.type = type
        self.sub_field = sub_field

    def __repr__(self):
        return f"FieldMetaData(type={self.type}, sub_field={self.sub_field})"

    def __eq__(self, other):
        return self.sub_field == other.sub_field and self.type == other.type


class FieldTypes(dict):

    def has(self, field, meta):
        return field in self and self[field] == meta

    def has_sub_path(self, path):
        pass


class ScriptGenerator:

    def reindex(self, prev_index, head_index, script):
        print({
            "endpoint": f"_reindex/{prev_index}/{head_index}",
            "body": {
                "script": script
            }
        })

    def alias(self, prev_index, head_index):
        pass

    def skip(self):
        print('skip')


class MigrationRuleEngine:

    def __init__(self, prev_index, head_index, head_schema: FieldTypes, prev_schema: FieldTypes, diff):
        self.prev_index = prev_index
        self.head_index = head_index
        self._diff = diff
        self._head_schema = head_schema
        self._prev_schema = prev_schema
        self._generator = ScriptGenerator()

    def add(self, data):
        for field, new_mata in data:  # type: str, FieldMetaData
            if 'remove' not in self._diff:
                # This field was added and no other field was removed.
                # This is an empty field. No migration needed
                self._generator.skip()
            elif new_mata.type == 'object':
                # If some sub path was removed and replaced by object then simple copy is OK.
                if self._prev_schema.has_sub_path(field):
                    pass
            else:
                self._generator.reindex(self.prev_index, self.head_index, f"""
                    ctx.{field} = "SOME_VALUE || FILED"
                """)

    def change(self, data):
        for field, changes in data:  # type: str, Tuple[FieldMetaData, FieldMetaData]
            prev_meta, head_meta = changes
            print(field, prev_meta, head_meta)

    def remove(self, data):
        for field, old_meta in data:  # type: str, FieldMetaData
            print(field, old_meta)


class SchemaChangeManager:

    def __init__(self, prev_index, head_index, prev_schema: FieldTypes, head_schema: FieldTypes):
        self.head_index = head_index
        self.prev_index = prev_index
        self.head_schema = head_schema
        self.prev_schema = prev_schema
        _diff = sorted(self._standardize(diff(self.prev_schema, self.head_schema)), key=lambda item: item[0])
        self._diff = defaultdict(list)
        for _mode, __field, __meta in _diff:
            self._diff[_mode].append((__field, __meta))

    @staticmethod
    def _standardize(source):
        for _mode, _field, _change in source:
            if _mode == 'add' or _mode == 'remove':
                for __field, __meta in _change:
                    yield _mode, __field, __meta
            elif _mode == 'change':
                if isinstance(_field, list):
                    for __field in _field:
                        yield _mode, __field, _change
                else:
                    yield _mode, _field, _change

    def make_change_script(self):
        _rules_engine = MigrationRuleEngine(self.prev_index, self.head_index, head_schema, prev_schema, self._diff)
        for _mode, _list_of_tuples in self._diff.items():
            getattr(_rules_engine, _mode)(_list_of_tuples)


class MappingConverter:

    def __init__(self):
        self.fields = {}

    def schema(self, mappings) -> FieldTypes:
        self.fields = {}
        return FieldTypes(self._loop(mappings))

    def _loop(self, mappings, path=None):
        if path is None:
            path = []

        for _key, _object in mappings.items():
            if 'properties' in _object:
                self._loop(_object['properties'], path=path + [_key])

            if 'type' in _object:
                field_path = path + [_key]

                self.fields[".".join(field_path)] = FieldMetaData(
                    type=_object['type'].lower(),
                    sub_field='field' in _object
                )

        return self.fields


converter = MappingConverter()
prev_schema = converter.schema(mappings_prev['properties'])
head_schema = converter.schema(mappings_head['properties'])
diff_master = SchemaChangeManager("prev_i", "head_i", prev_schema, head_schema)
diff_master.make_change_script()
