from tracardi.service.storage.mysql.schema.table import EventSourceTable
from tracardi.domain.event_source import EventSource
from tracardi.context import get_context
from tracardi.domain.named_entity import NamedEntity

from datetime import datetime

def map_to_event_source_table(event_source: EventSource) -> EventSourceTable:

    context = get_context()

    return EventSourceTable(
        id=event_source.id,
        type=','.join(event_source.type),
        bridge_id=event_source.bridge.id,
        bridge_name=event_source.bridge.name,
        timestamp=event_source.timestamp if event_source.timestamp else datetime.utcnow(),
        name=event_source.name or "No name provided",
        description=event_source.description or "No description provided",
        channel=event_source.channel or "",
        enabled=event_source.enabled or True,
        transitional=event_source.transitional or False,
        tags=','.join(event_source.tags) if isinstance(event_source.tags, list) else event_source.tags,
        groups=','.join(event_source.groups) if isinstance(event_source.groups, list) else event_source.groups,
        permanent_profile_id=event_source.permanent_profile_id or False,
        requires_consent=event_source.requires_consent or False,
        manual=event_source.manual,
        locked=event_source.locked or False,
        synchronize_profiles=event_source.synchronize_profiles or True,
        config=event_source.config,

        tenant = context.tenant,
        production = context.production,

        update=datetime.now(),  # Assuming update timestamp is set to current time
        url=None,  # Assuming 'url' is not in EventSource, needs to be handled if present
        icon=None,  # Assuming 'icon' is not in EventSource, needs to be handled if present
        hash=None,  # Assuming 'hash' is not in EventSource, needs to be handled if present
        endpoints_get_url=None,  # Assuming 'endpoints_get_url' is not in EventSource, needs to be handled if present
        endpoints_get_method=None,
        endpoints_post_url=None,  # Assuming 'endpoints_post_url' is not in EventSource, needs to be handled if present
        endpoints_post_method=None,
        configurable=None,  # Assuming 'configurable' is not in EventSource, needs to be handled if present

    )



def map_to_event_source(event_source_table: EventSourceTable) -> EventSource:
    return EventSource(
        id=event_source_table.id,
        type=event_source_table.type.split(',') if event_source_table.type else [],
        bridge=NamedEntity(
            id=event_source_table.bridge_id,
            name=event_source_table.bridge_name
        ),
        timestamp=event_source_table.timestamp,
        name=event_source_table.name,
        description=event_source_table.description,
        channel=event_source_table.channel,
        enabled=event_source_table.enabled or True,
        transitional=event_source_table.transitional or False,
        tags=event_source_table.tags.split(',') if event_source_table.tags else [],
        groups=event_source_table.groups.split(',') if event_source_table.groups else [],
        permanent_profile_id=event_source_table.permanent_profile_id or False,
        requires_consent=event_source_table.requires_consent or False,
        manual=event_source_table.manual,
        locked=event_source_table.locked or False,
        synchronize_profiles=event_source_table.synchronize_profiles or True,
        config=event_source_table.config
    )

