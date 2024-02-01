from tracardi.config import memory_cache
from tracardi.domain.event_source import EventSource
from tracardi.exceptions.log_handler import get_logger
from tracardi.service.cache_manager import CacheManager

logger = get_logger(__name__)
cache = CacheManager()


async def validate_source(source_id: str, allowed_bridges: list) -> EventSource:
    source = await cache.event_source(event_source_id=source_id, ttl=memory_cache.source_ttl)

    if source is None:
        raise ValueError(f"Invalid event source `{source_id}`")

    if not source.enabled:
        raise ValueError("Event source disabled.")

    if not source.is_allowed(allowed_bridges):
        raise ValueError(f"Event source `{source_id}` is not within allowed bridge types {allowed_bridges}.")

    return source
