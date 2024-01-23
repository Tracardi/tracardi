from tracardi.context import get_context
from tracardi.domain.event_validator import EventValidator, ValidationSchema
from tracardi.service.storage.mysql.mapping.utils import split_list
from tracardi.service.storage.mysql.schema.table import EventValidationTable
from tracardi.service.storage.mysql.utils.serilizer import to_model, from_model


def map_to_event_validation_table(event_validator: EventValidator) -> EventValidationTable:

    context = get_context()
    return EventValidationTable(
        id=event_validator.id,
        tenant=context.tenant,
        production=context.production,
        name=event_validator.name,
        description=event_validator.description,
        validation=from_model(event_validator.validation),
        tags=",".join(event_validator.tags),
        event_type=event_validator.event_type,
        enabled=event_validator.enabled
    )

def map_to_event_validation(table: EventValidationTable) -> EventValidator:
    return EventValidator(
        id=table.id,
        name=table.name,
        description=table.description,
        event_type=table.event_type,
        tags=split_list(table.tags),  # Convert string back to list
        validation=to_model(table.validation, ValidationSchema) if table.validation else None,
        enabled=table.enabled,

        production=table.production,
        running=table.running
    )
