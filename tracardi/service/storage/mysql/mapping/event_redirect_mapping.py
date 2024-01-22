from tracardi.context import get_context
from tracardi.domain.event_redirect import EventRedirect
from tracardi.domain.named_entity import NamedEntity
from tracardi.service.storage.mysql.mapping.utils import split_list
from tracardi.service.storage.mysql.schema.table import EventRedirectTable

def map_to_event_redirect_table(event_redirect: EventRedirect) -> EventRedirectTable:
    context = get_context()
    return EventRedirectTable(
        id=event_redirect.id,
        tenant=context.tenant,
        production=context.production,
        name=event_redirect.name,
        description=event_redirect.description or "",  # Default value if description is not available
        url=event_redirect.url,
        source_id=event_redirect.source.id,
        source_name=event_redirect.source.name,
        event_type=event_redirect.event_type,
        props=event_redirect.props,
        tags=",".join(event_redirect.tags) if event_redirect.tags else ""  # Convert list of tags to a comma-separated string
    )

def map_to_event_redirect(event_redirect_table: EventRedirectTable) -> EventRedirect:
    return EventRedirect(
        id=event_redirect_table.id,
        name=event_redirect_table.name,
        description=event_redirect_table.description or "",  # Default value if description is not available
        url=event_redirect_table.url,
        source=NamedEntity(id=event_redirect_table.source_id, name=event_redirect_table.source_name),
        event_type=event_redirect_table.event_type,
        props=event_redirect_table.props,
        tags=split_list(event_redirect_table.tags),  # Convert comma-separated string back to list
        production=event_redirect_table.production,
        running=event_redirect_table.running
    )
