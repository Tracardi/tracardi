from typing import Optional

from tracardi.domain.event_source import EventSource
from tracardi.exceptions.log_handler import get_logger
from tracardi.service.cache.event_source import load_event_source

logger = get_logger(__name__)


async def validate_source(source_id: str, allowed_bridges: list) -> EventSource:
    source:Optional[EventSource] = await load_event_source(event_source_id=source_id,)

    if source is None:
        raise ValueError(f"Invalid event source `{source_id}`")

    if not source.enabled:
        raise ValueError("Event source disabled.")

    if not source.is_allowed(allowed_bridges):
        raise ValueError(f"Event source `{source_id}` is not within allowed bridge types {allowed_bridges}.")

    return source
