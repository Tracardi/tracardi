from pprint import pprint

from tracardi.domain.entity_index_mapping import EntityIndexMapping

x = {
    "mappings": {
        "_meta": {
            "version": "1.0",
            "name": "train",
            "part_of": [{
                "index": "Fleet",
                "alias": None
            }],
            "description": "Train entity",
            "index": {
                "name": "Trains",
                "description": "Autonomous",
                "pk": "id"
            },
            "properties": {
                "id": {
                    "name": "identifier",
                    "rel": [
                        {
                            "index": "Fleet",
                            "pk": "fleet_id"
                        }
                    ],
                },
                "car_id": {
                    "name": "Car ID",
                    "rel": [
                        {
                            "index": "Car",
                            "pk": "id"
                        }
                    ]
                }
            }

        },
        "properties": {
            "id": {
                "type": "keyword"
            },
            "name": {
                "type": "text"
            },
            "description": {
                "type": "text"
            },
            "type": {
                "type": "keyword",
                "null_value": "collection"
            },
            "car_id": {
                "type": "keyword",
                "index": False
            },
            "debug": {
                "properties": {
                    "enabled": {
                        "type": "boolean"
                    },
                    "logging_level": {
                        "type": "keyword"
                    }
                }
            }
        }
    }
}

e = EntityIndexMapping(**x)
pprint(e.dict(by_alias=True))
