from tracardi.domain.named_entity import NamedEntity
from tracardi.service.storage.mysql.mapping.utils import split_list
from tracardi.service.storage.mysql.schema.table import EventToProfileMappingTable
from tracardi.domain.event_to_profile import EventToProfile, EventToProfileMap
from tracardi.context import get_context
from tracardi.service.storage.mysql.utils.serilizer import to_model, from_model


def map_to_event_to_profile_table(event_to_profile: EventToProfile) -> EventToProfileMappingTable:
    context = get_context()

    return EventToProfileMappingTable(
        id=event_to_profile.id,
        name=event_to_profile.name,
        description=event_to_profile.description or "No description provided",
        event_type_id=event_to_profile.event_type.id,
        event_type_name=event_to_profile.event_type.name,
        tags=','.join(event_to_profile.tags),  # Convert list of tags to a comma-separated string
        enabled=event_to_profile.enabled if event_to_profile.enabled is not None else False,
        config=event_to_profile.config,
        event_to_profile=from_model(event_to_profile.event_to_profile),
        tenant=context.tenant,
        production=context.production
    )

def map_to_event_to_profile(event_to_profile_table: EventToProfileMappingTable) -> EventToProfile:
    return EventToProfile(
        id=event_to_profile_table.id,
        name=event_to_profile_table.name,
        description=event_to_profile_table.description,
        event_type=NamedEntity(id=event_to_profile_table.event_type_id, name=event_to_profile_table.event_type_name),
        tags=split_list(event_to_profile_table.tags),
        enabled=event_to_profile_table.enabled if event_to_profile_table.enabled is not None else False,
        config=event_to_profile_table.config,
        event_to_profile=to_model(event_to_profile_table.event_to_profile, EventToProfileMap),

        production=event_to_profile_table.production,
        running=event_to_profile_table.running
    )
