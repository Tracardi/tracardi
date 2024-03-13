from tracardi.context import get_context
from tracardi.domain.event_type_metadata import EventTypeMetadata
from tracardi.service.storage.mysql.mapping.utils import split_list
from tracardi.service.storage.mysql.schema.table import EventMappingTable


def map_to_event_mapping_table(event_type_metadata: EventTypeMetadata) -> EventMappingTable:
    context = get_context()

    return EventMappingTable(
        id=event_type_metadata.id,
        name=event_type_metadata.name,
        description=event_type_metadata.description or "",
        event_type=event_type_metadata.event_type,
        tags=",".join(event_type_metadata.tags),
        journey=event_type_metadata.journey,
        enabled=event_type_metadata.enabled if event_type_metadata.enabled is not None else False,
        index_schema=event_type_metadata.index_schema,

        tenant=context.tenant,
        production=context.production,
    )


def map_to_event_mapping(event_mapping_table: EventMappingTable) -> EventTypeMetadata:
    return EventTypeMetadata(
        id=event_mapping_table.id,
        name=event_mapping_table.name,
        description=event_mapping_table.description or "",
        event_type=event_mapping_table.event_type,
        tags=split_list(event_mapping_table.tags),
        journey=event_mapping_table.journey,
        enabled=event_mapping_table.enabled if event_mapping_table.enabled is not None else False,
        index_schema=event_mapping_table.index_schema,

        production=event_mapping_table.production,
        running=event_mapping_table.running
    )
