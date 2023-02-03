import logging
from datetime import datetime
from typing import List, Union, Generator, AsyncGenerator, Any

from tracardi.config import tracardi, memory_cache
from tracardi.domain.entity import Entity
from tracardi.domain.enum.event_status import PROCESSED
from tracardi.domain.event_type_metadata import EventTypeMetadata
from tracardi.domain.value_object.operation import Operation
from tracardi.domain.value_object.save_result import SaveResult
from tracardi.service.cache_manager import CacheManager

from tracardi.service.console_log import ConsoleLog
from tracardi.exceptions.log_handler import log_handler

from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from tracardi.domain.event import Event
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.exceptions.exception import StorageException, FieldTypeConflictException
from tracardi.domain.value_object.collect_result import CollectResult
from tracardi.service.storage.driver import storage
from tracardi.service.tracking_manager import TrackerResult

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)
cache = CacheManager()


class TrackerResultPersister:

    def __init__(self, console_log: ConsoleLog):
        self.console_log = console_log

    @staticmethod
    def get_profiles_to_save(tracker_results: List[TrackerResult]):
        for tracker_result in tracker_results:
            profile = tracker_result.profile
            if isinstance(profile, Profile) and (profile.operation.new or profile.operation.needs_update()):
                # Clean operations
                profile.operation = Operation()
                yield profile

    @staticmethod
    def get_sessions_to_save(tracker_results: List[TrackerResult]) -> Generator[Session, Any, None]:
        for tracker_result in tracker_results:
            if isinstance(tracker_result.session, Session):
                if tracker_result.session.operation.new or tracker_result.session.operation.needs_update():
                    # Session to add. Add new profile id to session if it does not exist,
                    # or profile id in session is different from the real profile id.
                    if tracker_result.session.profile is None or (
                            isinstance(tracker_result.session.profile, Entity)
                            and isinstance(tracker_result.profile, Entity)
                            and tracker_result.session.profile.id != tracker_result.profile.id):
                        # save only profile Entity
                        if tracker_result.profile is not None:
                            tracker_result.session.profile = Entity(id=tracker_result.profile.id)
                    yield tracker_result.session

    async def _save_profile(self, tracker_results: List[TrackerResult]):
        try:
            profiles_to_save = list(self.get_profiles_to_save(tracker_results))
            if profiles_to_save:
                yield await storage.driver.profile.save(profiles_to_save)

        except StorageException as e:
            raise FieldTypeConflictException("Could not save profile. Error: {}".format(str(e)), rows=e.details)

    async def _save_session(self, tracker_results: List[TrackerResult]):
        try:
            for tracker_result in tracker_results:
                persist_session = tracker_result.tracker_payload.is_on('saveSession', default=True)
                if persist_session:
                    sessions_to_add = list(self.get_sessions_to_save(tracker_results))
                    if sessions_to_add:
                        """
                        We remove saved sessions from cache. The cache may keep the information that there was
                        no session. It depends on the cache configuration
                        """
                        session_cache = cache.session_cache()
                        if session_cache.allow_null_values:
                            for session in sessions_to_add:
                                session_cache.delete(session.id)

                        """
                        Remove session new. Add empty operation.
                        """
                        for session in sessions_to_add:
                            session.operation = Operation()

                        result = await storage.driver.session.save(sessions_to_add)
                        # Todo this may cause errors when async, we save multiple sessions at once

                        """
                        Until the session is saved and it is usually within 1s the system can create many profiles 
                        for 1 session.  System checks if the session exists by loading it from ES. If it is a new 
                        session then is does not exist and must be saved before it can be read. So there is a 
                        1s when system thinks that the session does not exist.
            
                        If session is new we will refresh the session in ES.
                        """

                        await storage.driver.session.refresh()
                        yield result

                    # Do not update session duration. It should be calculated on the front end

                    # sessions_to_update = [session for session, save in sessions if save is False]
                    # # Update session duration
                    # for session in sessions_to_update:
                    #     await storage.driver.session.update_session_duration(session)
        except StorageException as e:
            raise FieldTypeConflictException("Could not save session. Error: {}".format(str(e)), rows=e.details)

    @staticmethod
    def __get_persistent_events_without_source(events: List[Event]):
        for event in events:
            if event.is_persistent():
                event.source = Entity(id=event.source.id)
                yield event

    @staticmethod
    async def __tag_events(events: Union[List[Event], Generator[Event, Any, None]]) -> AsyncGenerator[Event, Any]:

        for event in events:
            try:

                event_meta_data = await cache.event_metadata(event.type, ttl=memory_cache.event_metadata_cache_ttl)
                if event_meta_data:
                    event_type_meta_data = event_meta_data.to_entity(EventTypeMetadata)

                    event.tags.values = tuple(tag.lower() for tag in set(
                        tuple(event.tags.values) + tuple(event_type_meta_data.tags)
                    ))

            except ValueError as e:
                logger.error(str(e))

            yield event

    async def __save_events(self, events: Union[List[Event], Generator[Event, Any, None]]) -> Union[SaveResult,
                                                                                                    BulkInsertResult]:

        tagged_events = [event async for event in self.__tag_events(self.__get_persistent_events_without_source(events))]
        event_result = await storage.driver.event.save(tagged_events, exclude={"operation": ...})
        event_result = SaveResult(**event_result.dict())

        # Add event types
        for event in events:
            event_result.types.append(event.type)

        return event_result

    @staticmethod
    async def _modify_events(tracker_result: TrackerResult, log_event_journal) -> List[Event]:
        for event in tracker_result.events:

            event.metadata.aux['process_time'] = datetime.timestamp(datetime.utcnow()) - datetime.timestamp(
                event.metadata.time.insert)

            # Reset operations
            event.operation.new = False
            event.operation.update = False

            # Reset session id if session is not saved

            if tracker_result.tracker_payload.is_on('saveSession', default=True) is False:
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

        return tracker_result.events

    async def _save_events(self, tracker_results: List[TrackerResult]):
        try:
            # Set statuses
            log_event_journal = self.console_log.get_indexed_event_journal()

            bulk_events = []
            for tracker_result in tracker_results:
                persist_events = tracker_result.tracker_payload.is_on('saveEvents', default=True)
                if not persist_events:
                    continue
                events = await self._modify_events(tracker_result, log_event_journal)
                bulk_events += events
            yield await self.__save_events(bulk_events)

        except StorageException as e:
            raise FieldTypeConflictException("Could not save event. Error: {}".format(str(e)), rows=e.details)

    async def persist(self, tracker_results: List[TrackerResult]) -> CollectResult:
        return CollectResult(
            profile=[result async for result in self._save_profile(tracker_results)],
            session=[result async for result in self._save_session(tracker_results)],
            events=[result async for result in self._save_events(tracker_results)]
        )
