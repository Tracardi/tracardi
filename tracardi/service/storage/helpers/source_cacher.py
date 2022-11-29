import logging
from typing import Optional
from tracardi.config import memory_cache, tracardi
from tracardi.domain.event_source import EventSource
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.cache_manager import CacheManager

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)
cache = CacheManager()


async def validate_source(source_id: str, allowed_bridges: list) -> Optional[EventSource]:
    source = await cache.event_source(event_source_id=source_id, ttl=memory_cache.source_ttl)

    if source is None:
        raise ValueError(f"Invalid event source `{source_id}`")

    if not source.enabled:
        raise ValueError("Event source disabled.")

    if source.type not in allowed_bridges:
        raise ValueError(f"Event source `{source_id}` is not within allowed bridge types {allowed_bridges}.")

    return source
