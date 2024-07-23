from typing import Optional

from tracardi.config import tracardi
from tracardi.domain.event_source import EventSource
from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.exceptions.exception import BlockedException
from tracardi.exceptions.log_handler import get_logger
from tracardi.service.cache.event_source import load_event_source_via_cache
from tracardi.service.setup.setup_bridges import open_rest_source_bridge
from tracardi.service.tracker_config import TrackerConfig
from tracardi.service.utils.date import now_in_utc

logger = get_logger(__name__)


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

    source: Optional[EventSource] = await load_event_source_via_cache(source_id=source_id)

    if source is not None:

        if not source.enabled:
            raise BlockedException("Event source disabled.")

        if not source.is_allowed(allowed_bridges):
            raise BlockedException(f"This endpoint allows only bridges of "
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
            timestamp=now_in_utc(),
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
        raise BlockedException(f"Invalid event source `{source_id}`. Request came from IP: `{ip}` "
                               f"width payload: {tracker_payload}")

    if source.has_restricted_domain():
        origin = tracker_payload.get_origin_or_referer()

        if not origin:
            raise BlockedException(f"Event source `{source_id}` requires origin header.")

        if not source.is_allowed_domain_origin(origin):
            raise BlockedException(f"Event source `{source_id}`. Disallows url: {origin.geturl()}")

    return source


def _get_internal_source(tracker_config: TrackerConfig, tracker_payload: TrackerPayload):
    if tracker_config.internal_source.id != tracker_payload.source.id:
        msg = f"Invalid event source `{tracker_payload.source.id}`"
        raise BlockedException(msg)
    return tracker_config.internal_source


async def validate_source(tracker_config: TrackerConfig, tracker_payload: TrackerPayload) -> EventSource:
    if tracker_config.internal_source is not None:
        source = _get_internal_source(tracker_config, tracker_payload)
    else:
        source = await _validate_source(tracker_payload, tracker_config.allowed_bridges)

    return source
