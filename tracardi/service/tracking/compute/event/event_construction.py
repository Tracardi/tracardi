from tracardi.domain.event_source import EventSource
from tracardi.domain.payload.event_payload import EventPayload

from tracardi.service.utils.date import now_in_utc

from typing import Optional, Union
from uuid import uuid4

from tracardi.domain.api_instance import ApiInstance
from tracardi.domain.entity import Entity, PrimaryEntity
from tracardi.domain.enum.event_status import COLLECTED
from tracardi.domain.event import Event, Tags, EventSession
from tracardi.domain.event_metadata import EventMetadata
from tracardi.domain.event_metadata import EventPayloadMetadata
from tracardi.domain.metadata import Hit
from tracardi.domain.session import Session, SessionContext
from tracardi.domain.value_object.operation import RecordFlag
from tracardi.service.string_manager import capitalize_event_type_id
from tracardi.service.utils.getters import get_primary_entity


def _get_event_session(session: Union[Session, Entity]) -> Optional[EventSession]:
    if session is None:
        return None

    if isinstance(session, Session) and isinstance(session.context, dict):
        session.context = SessionContext(session.context)

        tz = session.context.get_time_zone()
        event_session = EventSession(
            id=session.id,
            tz=tz
        )

    else:
        event_session = EventSession(
            id=session.id
        )

    return event_session


def _get_metadata(event_payload: EventPayload, metadata: EventPayloadMetadata, source: Entity, profile_less) -> EventMetadata:
    meta = EventMetadata(**metadata.model_dump())
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

    if event_payload.merging is not None:
        metadata.error = event_payload.merging.error
        # Mark as merged if not error
        metadata.merge = not event_payload.merging.error

    if event_payload.validation is not None and event_payload.validation.error is True:
        metadata.valid = False

    return meta


def _get_hit(event_payload: EventPayload) -> Hit:
    hit = Hit()

    if isinstance(event_payload.context, dict) and 'page' in event_payload.context:

        try:
            hit.name = event_payload.context['page']['title']
        except (KeyError, TypeError):
            pass

        try:
            hit.url = event_payload.context['page']['url']
        except (KeyError, TypeError):
            pass

        try:
            hit.referer = event_payload.context['page']['referer']['host']
        except (KeyError, TypeError):
            pass

    return hit


def event_payload_to_event(event_payload: EventPayload,
                           metadata: EventPayloadMetadata,
                           source: EventSource,
                           session: Union[Optional[Entity], Optional[Session]],
                           profile: Optional[PrimaryEntity],
                           profile_less: bool) -> Event:

    meta = _get_metadata(event_payload, metadata, source, profile_less)
    source = source if not event_payload.has_source_id() else Entity(id=event_payload.get_source_id())
    profile_entity = get_primary_entity(profile)

    if isinstance(session, Session):

        hit = _get_hit(event_payload)

        event_type = event_payload.type.strip()
        event = Event(id=str(uuid4()) if not event_payload.id else event_payload.id,
                      name=capitalize_event_type_id(event_type),
                      metadata=meta,
                      session=_get_event_session(session),
                      profile=profile_entity,  # profile can be None when profile_less event.
                      type=event_type,

                      os=session.os.model_dump(exclude_unset=True),
                      app=session.app.model_dump(exclude_unset=True),
                      device=session.device.model_dump(exclude_unset=True),
                      hit=hit.model_dump(exclude_unset=True),

                      utm=session.utm,

                      properties=event_payload.properties,
                      source=source,  # Entity
                      config=event_payload.options,
                      context=event_payload.context,
                      operation=RecordFlag(new=True),
                      tags=Tags(values=tuple(event_payload.tags), count=len(event_payload.tags))
                      )

    else:
        event_type = event_payload.type.strip()
        event = Event(id=str(uuid4()) if not event_payload.id else event_payload.id,
                      name=capitalize_event_type_id(event_type),
                      metadata=meta,
                      session=None,
                      profile=profile_entity,  # profile can be None when profile_less event.
                      type=event_type,
                      properties=event_payload.properties,
                      source=source,  # Entity
                      config=event_payload.options,
                      context=event_payload.context,
                      operation=RecordFlag(new=True),
                      tags=Tags(values=tuple(event_payload.tags), count=len(event_payload.tags))
                      )

    return event
