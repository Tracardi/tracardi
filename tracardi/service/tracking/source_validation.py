from typing import Optional

import logging

from tracardi.config import tracardi, memory_cache
from tracardi.domain.event_source import EventSource
from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.cache_manager import CacheManager
from tracardi.exceptions.exception import UnauthorizedException
from tracardi.service.storage.mysql.bootstrap.bridge import open_rest_source_bridge
from tracardi.service.tracker_config import TrackerConfig

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)
cache = CacheManager()


async def _check_source_id(allowed_bridges, source_id) -> Optional[EventSource]:
    if not tracardi.enable_event_source_check:
        return EventSource(
            id=source_id,
            type=['rest'],
            bridge=NamedEntity(id=open_rest_source_bridge.id, name=open_rest_source_bridge.name),
            name="Static event source",
            description="This event source is prepared because of ENABLE_EVENT_SOURCE_CHECK==no.",
            channel="Web",
            transitional=False  # ephemeral
        )

    source = await cache.event_source(event_source_id=source_id, ttl=memory_cache.source_ttl)

    if source is not None:

        if not source.enabled:
            raise ValueError("Event source disabled.")

        if not source.is_allowed(allowed_bridges):
            raise ValueError(f"This endpoint allows only bridges of "
                             f"types {allowed_bridges}, but the even source "
                             f"`{source.name}`.`{source_id}` has types `{source.type}`. "
                             f"Change bridge type in event source `{source.name}` to one that has endpoint type "
                             f"{allowed_bridges} or call any `{source.type}` endpoint.")

    return source


async def _validate_source(tracker_payload: TrackerPayload, allowed_bridges) -> EventSource:
    source_id = tracker_payload.source.id
    ip = tracker_payload.metadata.ip

    if source_id == tracardi.internal_source:
        return EventSource(
            id=source_id,
            type=['internal'],
            bridge=NamedEntity(id=open_rest_source_bridge.id, name=open_rest_source_bridge.name),
            name="Internal event source",
            description="This is event source for internal events.",
            channel="Internal",
            transitional=False,  # ephemeral
            tags=['internal']
        )

    source = await _check_source_id(allowed_bridges, source_id)

    if source is None:
        raise ValueError(f"Invalid event source `{source_id}`. Request came from IP: `{ip}` "
                         f"width payload: {tracker_payload}")

    return source


def _get_internal_source(tracker_config: TrackerConfig, tracker_payload: TrackerPayload):
    if tracker_config.internal_source.id != tracker_payload.source.id:
        msg = f"Invalid event source `{tracker_payload.source.id}`"
        raise ValueError(msg)
    return tracker_config.internal_source


async def validate_source(tracker_config: TrackerConfig, tracker_payload: TrackerPayload) -> EventSource:
    try:
        if tracker_config.internal_source is not None:
            source = _get_internal_source(tracker_config, tracker_payload)
        else:
            source = await _validate_source(tracker_payload, tracker_config.allowed_bridges)

        return source

    except ValueError as e:
        raise UnauthorizedException(e)
