from typing import List

from tracardi.service.storage.elastic.interface import raw as raw_db


def _find_time_fields(mapping, field_types: List[str], prefix=''):
    time_fields = []
    for field, properties in mapping.items():
        if 'type' in properties and properties['type'] in field_types:
            time_fields.append(f"{prefix}.{field}" if prefix else field)
        if 'properties' in properties:
            subfields = _find_time_fields(properties['properties'],
                                          field_types,
                                          prefix=f"{prefix}.{field}" if prefix else field)
            time_fields.extend(subfields)
    return time_fields


async def get_mappings_by_field_type(index: str, types: List[str]):
    mapping = await raw_db.get_mapping(index)
    time_fields = []
    if filter is not None:
        time_fields = _find_time_fields(mapping['mappings']['properties'], types)
    return time_fields
