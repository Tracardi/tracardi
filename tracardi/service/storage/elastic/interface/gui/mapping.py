from typing import List

from tracardi.domain.storage.index_mapping import IndexMapping
from tracardi.service.storage.elastic.interface.gui.storage import load_mapping


def _find_time_fields(mapping, field_types: List[str], prefix='') -> List[str]:
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


async def load_mappings_by_field_type(index: str, types: List[str]) -> list:
    mapping = await load_mapping(index)
    time_fields = []
    if filter is not None:
        time_fields = _find_time_fields(mapping['mappings']['properties'], types)
    return time_fields


async def load_index_field_names(index: str) -> List[str]:
    """
    This one returns raw data as it is elastic specific.
    """

    mapping: IndexMapping = await load_mapping(index)
    return mapping.get_field_names()
