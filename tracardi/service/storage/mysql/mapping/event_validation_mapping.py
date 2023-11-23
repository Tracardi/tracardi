from tracardi.context import get_context
from tracardi.domain.event_validator import EventValidator, ValidationSchema
from tracardi.service.storage.mysql.schema.table import EventValidationTable
from tracardi.service.storage.mysql.utils.serilizer import to_json, from_json

def map_to_event_validation_table(event_validator: EventValidator) -> EventValidationTable:

    context = get_context()
    return EventValidationTable(
        id=event_validator.id,
        tenant=context.tenant,
        production=context.production,
        name=event_validator.name,
        description=event_validator.description,
        validation=to_json(event_validator.validation),  # Serialization of the ValidationSchema object
        tags=",".join(event_validator.tags),  # Tags list converted to a comma-separated string
        event_type=event_validator.event_type,
        enabled=event_validator.enabled or False
    )

def map_to_event_validation(table: EventValidationTable) -> EventValidator:
    return EventValidator(
        id=table.id,
        name=table.name,
        description=table.description,
        event_type=table.event_type,
        tags=table.tags.split(",") if table.tags else [],  # Convert string back to list
        validation=from_json(table.validation, ValidationSchema) if table.validation else None,
        enabled=table.enabled or False
    )
