from tracardi.domain.entity import Entity
from tracardi.domain.destination import Destination, DestinationConfig
from tracardi.domain.named_entity import NamedEntity
from tracardi.service.storage.mysql.mapping.utils import split_list
from tracardi.service.storage.mysql.schema.table import DestinationTable
from tracardi.service.storage.mysql.utils.serilizer import to_model, from_model
from tracardi.context import get_context

def map_to_destination_table(destination: Destination) -> DestinationTable:
    context = get_context()
    return DestinationTable(
        id=destination.id,
        name=destination.name,

        tenant=context.tenant,
        production=context.production,

        description=destination.description or "",
        destination=from_model(destination.destination),
        condition=destination.condition or "",
        mapping=destination.mapping,
        enabled=destination.enabled,
        on_profile_change_only=destination.on_profile_change_only,
        event_type_id=destination.event_type.id if destination.event_type else None,
        event_type_name=destination.event_type.name if destination.event_type else None,
        source_id=destination.source.id,
        source_name=destination.source.name,
        resource_id=destination.resource.id,
        tags=','.join(destination.tags) if destination.tags else None
    )


def map_to_destination(destination_table: DestinationTable) -> Destination:
    return Destination(
        id=destination_table.id,
        name=destination_table.name,
        description=destination_table.description or "",
        destination=to_model(destination_table.destination, DestinationConfig),
        condition=destination_table.condition or "",
        mapping=destination_table.mapping,
        enabled=destination_table.enabled if destination_table.enabled is not None else False,
        on_profile_change_only=destination_table.on_profile_change_only if destination_table.on_profile_change_only is not None else True,
        event_type=NamedEntity(
            id=destination_table.event_type_id,
            name=destination_table.event_type_name
        ) if destination_table.event_type_id and destination_table.event_type_name else None,
        source=NamedEntity(
            id=destination_table.source_id or "",
            name=destination_table.source_name or ""
        ),
        resource=Entity(
            id=destination_table.resource_id or ""
        ),
        tags=split_list(destination_table.tags),
        production=destination_table.production,
        running=destination_table.running
    )
