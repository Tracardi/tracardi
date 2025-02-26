from tracardi.domain.event_source import EventSource
from tracardi.domain.flat_session import FlatSession
from tracardi.domain.payload.event_payload import EventPayload

from tracardi.common.time.date import now_in_utc

from typing import Optional, Union, Tuple
from uuid import uuid4

from tracardi.domain.api_instance import ApiInstance
from tracardi.domain.entity import Entity
from tracardi.domain.enum.event_status import COLLECTED
from tracardi.domain.event_session import EventSession
from tracardi.domain.flat_event import EventDict

from tracardi.domain.event_metadata import EventMetadata
from tracardi.domain.event_metadata import EventPayloadMetadata
from tracardi.common.tools.string_manager import capitalize_event_type_id


def _get_event_session(flat_session: Union[FlatSession, Entity]) -> Optional[EventSession]:
    if flat_session is None:
        return None

    tz = flat_session.get_time_zone()
    event_session = EventSession(
        id=flat_session.id,
        tz=tz
    )

    return event_session


def _get_metadata(event_payload: EventPayload, tracker_payload_metadata: EventPayloadMetadata, source: EventSource,
                  profile_less) -> EventMetadata:
    meta = EventMetadata(**tracker_payload_metadata.model_dump())
    meta.status = COLLECTED
    meta.profile_less = profile_less
    meta.instance = Entity(id=ApiInstance().id)

    if event_payload.time.insert:
        meta.time.insert = event_payload.time.insert
    else:
        meta.time.insert = now_in_utc()

    if event_payload.time.create:
        meta.time.create = event_payload.time.create

    meta.channel = source.channel
    meta.valid = event_payload.is_valid()

    return meta


def _get_hit(event_payload: EventPayload) -> dict:
    hit = {}

    if isinstance(event_payload.context, dict) and 'page' in event_payload.context:

        try:
            hit['name'] = event_payload.context['page']['title']
        except (KeyError, TypeError):
            pass

        try:
            hit['url'] = event_payload.context['page']['url']
        except (KeyError, TypeError):
            pass

        try:
            hit['referer'] = event_payload.context['page']['referer']['host']
        except (KeyError, TypeError):
            pass

    return hit


def _update_event_from_request(request: dict, event: EventDict):
    if request:
        if 'request' not in event or not isinstance(event['request'], dict):
            event['request'] = {}

        event['request'].update(request)

    return event


def event_payload_to_event(
        request: dict,
        event_payload: EventPayload,
        tracker_payload_metadata: EventPayloadMetadata,
        source: EventSource,
        flat_session: Union[Optional[Entity], Optional[FlatSession]],
        profile_id: Optional[str],
        profile_less: bool) -> Tuple[EventDict, bool]:
    id = str(uuid4()) if not event_payload.id else event_payload.id
    event_type = event_payload.type.strip()
    event_name = capitalize_event_type_id(event_type)
    # TODO Create Dict not Object
    meta = _get_metadata(event_payload, tracker_payload_metadata, source, profile_less)
    meta_dict = meta.model_dump(mode="json")
    source_dict = {"id": source.id} if not event_payload.has_source_id() else dict(id=event_payload.get_source_id())
    profile_entity_dict = {"id": profile_id} if profile_id else None

    if isinstance(flat_session, FlatSession):

        hit_dict = _get_hit(event_payload)

        event_dict = EventDict(
            id=id,
            name=event_name,
            metadata=meta_dict,
            session=_get_event_session(flat_session).model_dump(mode="json"),
            profile=profile_entity_dict,  # profile can be None when profile_less event.
            type=event_type,

            os=flat_session.get('os', {}),
            app=flat_session.get('app', {}),
            device=flat_session.get('device', {}),
            hit=hit_dict,

            utm=flat_session.get('utm', {}),

            properties=event_payload.properties,
            source=source_dict,  # Entity
            config=event_payload.options,
            context=event_payload.context,
            tags=dict(values=tuple(event_payload.tags), count=len(event_payload.tags))
        )

    else:

        event_dict = EventDict(
            id=id,
            name=event_name,
            metadata=meta_dict,
            profile=profile_entity_dict,  # profile can be None when profile_less event.
            type=event_type,
            properties=event_payload.properties,
            source=source_dict,  # Entity
            config=event_payload.options,
            context=event_payload.context,
            tags=dict(values=tuple(event_payload.tags), count=len(event_payload.tags))
        )

    event_dict = _update_event_from_request(request, event_dict)

    return event_dict, meta.valid
