from tracardi.context import get_context
from tracardi.domain.event_reshaping_schema import EventReshapingSchema, ReshapeSchema
from tracardi.domain.named_entity import NamedEntity
from tracardi.service.storage.mysql.schema.table import EventReshapingTable
from tracardi.service.storage.mysql.utils.serilizer import to_json, from_json


def map_to_event_reshaping_table(event_reshaping: EventReshapingSchema) -> EventReshapingTable:
    context = get_context()

    return EventReshapingTable(
        id=event_reshaping.id,
        name=event_reshaping.name,
        description=event_reshaping.description or "No description provided",
        reshaping=to_json(event_reshaping.reshaping),
        tags=','.join(event_reshaping.tags),  # Convert list of tags to a comma-separated string
        event_type=event_reshaping.event_type,
        event_source_id=event_reshaping.event_source.id,
        event_source_name=event_reshaping.event_source.name,
        enabled=event_reshaping.enabled if event_reshaping.enabled is not None else False,  # Set default value for bool

        tenant = context.tenant,
        production = context.production
    )

def map_to_event_reshaping(event_reshaping_table: EventReshapingTable) -> EventReshapingSchema:
    return EventReshapingSchema(
        id=event_reshaping_table.id,
        name=event_reshaping_table.name,
        description=event_reshaping_table.description,
        reshaping=from_json(event_reshaping_table.reshaping, ReshapeSchema),
        tags=event_reshaping_table.tags.split(',') if event_reshaping_table.tags else [],
        event_type=event_reshaping_table.event_type,
        event_source=NamedEntity(id=event_reshaping_table.event_source_id, name=event_reshaping_table.event_source_name),
        enabled=event_reshaping_table.enabled if event_reshaping_table.enabled is not None else False  # Set default value for bool
    )