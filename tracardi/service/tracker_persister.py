import asyncio
import logging
from datetime import datetime
from typing import List, Optional, Union, Generator, AsyncGenerator, Any

from tracardi.config import tracardi, memory_cache
from tracardi.domain.entity import Entity
from tracardi.domain.event_type_metadata import EventTypeMetadata
from tracardi.domain.value_object.save_result import SaveResult
from tracardi.service.cache_manager import CacheManager

from tracardi.service.console_log import ConsoleLog
from tracardi.exceptions.log_handler import log_handler

from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from tracardi.domain.event import Event, PROCESSED
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.exceptions.exception import StorageException, FieldTypeConflictException
from tracardi.domain.value_object.collect_result import CollectResult
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.service.storage.driver import storage

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)
cache = CacheManager()


async def _save_profile(profile):
    try:
        if isinstance(profile, Profile) and (profile.operation.new or profile.operation.needs_update()):
            profile.operation.new = False
            return await storage.driver.profile.save(profile)
        else:
            return BulkInsertResult()

    except StorageException as e:
        raise FieldTypeConflictException("Could not save profile. Error: {}".format(str(e)), rows=e.details)


async def _save_session(tracker_payload, session, profile):
    try:
        persist_session = tracker_payload.is_on('saveSession', default=True)
        # TODO rethink if session must be saved all the time. It only saves the duration.
        result = await storage.driver.session.save_session(session, profile, persist_session)
        if session and session.operation.new:
            """
            Until the session is saved and it is usually within 1s the system can create many profiles for 1 session. 
            System checks if the session exists by loading it from ES. If it is a new session then is does not exist 
            and must be saved before it can be read. So there is a 1s when system thinks that the session does not 
            exist.

            If session is new we will refresh the session in ES.
            """

            await storage.driver.session.refresh()
        return result
    except StorageException as e:
        raise FieldTypeConflictException("Could not save session. Error: {}".format(str(e)), rows=e.details)


def __get_persistent_events(events: List[Event]):
    for event in events:
        if event.is_persistent():
            yield event


async def __tag_events(events: Union[List[Event], Generator[Event, Any, None]]) -> AsyncGenerator[Event, Any]:

    for event in events:
        try:

            event_meta_data = await cache.event_tag(event.type, ttl=memory_cache.event_tag_cache_ttl)
            if event_meta_data:
                event_type_meta_data = event_meta_data.to_entity(EventTypeMetadata)

                event.tags.values = tuple(tag.lower() for tag in set(
                    tuple(event.tags.values) + tuple(event_type_meta_data.tags)
                ))

        except ValueError as e:
            logger.error(str(e))

        yield event


async def __save_events(events: Union[List[Event], Generator[Event, Any, None]],
                        persist_events: bool = True) -> Union[SaveResult, BulkInsertResult]:

    if not persist_events:
        return BulkInsertResult()

    tagged_events = [event async for event in __tag_events(__get_persistent_events(events))]
    event_result = await storage.driver.event.save(tagged_events, exclude={"update": ...})
    event_result = SaveResult(**event_result.dict())

    # Add event types
    for event in events:
        event_result.types.append(event.type)

    return event_result


async def _save_events(tracker_payload, console_log, events):
    try:
        persist_events = tracker_payload.is_on('saveEvents', default=True)

        # Set statuses
        log_event_journal = console_log.get_indexed_event_journal()

        for event in events:

            event.metadata.time.process_time = datetime.timestamp(datetime.utcnow()) - datetime.timestamp(
                event.metadata.time.insert)

            # Reset session id if session is not saved

            if tracker_payload.is_on('saveSession', default=True) is False:
                # DO NOT remove session if it already exists in db
                if not isinstance(event.session, Entity) or not await storage.driver.session.exist(event.session.id):
                    event.session = None

            if event.id in log_event_journal:
                log = log_event_journal[event.id]
                if log.is_error():
                    event.metadata.error = True
                    continue
                elif log.is_warning():
                    event.metadata.warning = True
                    continue
                else:
                    event.metadata.status = PROCESSED

        return await __save_events(events, persist_events)

    except StorageException as e:
        raise FieldTypeConflictException("Could not save event. Error: {}".format(str(e)), rows=e.details)


async def persist(console_log: ConsoleLog, session: Session, events: List[Event],
                   tracker_payload: TrackerPayload, profile: Optional[Profile] = None) -> CollectResult:
    results = await asyncio.gather(
        _save_profile(profile),
        _save_session(tracker_payload, session, profile),
        _save_events(tracker_payload, console_log, events)
    )

    return CollectResult(
        profile=results[0],
        session=results[1],
        events=results[2]
    )

