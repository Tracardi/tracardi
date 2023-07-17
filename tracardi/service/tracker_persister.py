import logging
from datetime import datetime
from typing import List, Union, Generator, AsyncGenerator, Any, Dict

from tracardi.config import tracardi, memory_cache
from tracardi.domain.console import Console
from tracardi.domain.entity import Entity
from tracardi.domain.enum.event_status import PROCESSED
from tracardi.domain.event_type_metadata import EventTypeMetadata
from tracardi.domain.value_object.operation import Operation
from tracardi.domain.value_object.save_result import SaveResult
from tracardi.service.cache_manager import CacheManager

from tracardi.service.console_log import ConsoleLog, StatusLog
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.driver.elastic import event as event_db
from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from tracardi.domain.event import Event
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.exceptions.exception import StorageException, FieldTypeConflictException
from tracardi.domain.value_object.collect_result import CollectResult
from tracardi.service.field_mappings_cache import FieldMapper
from tracardi.service.storage.driver.elastic import profile as profile_db
from tracardi.service.storage.driver.elastic import session as session_db
from tracardi.service.tracking_manager import TrackerResult
from tracardi.service.license import License
if License.has_license():
    from com_tracardi.service import event_pool
    from com_tracardi.config import com_tracardi_settings

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)
cache = CacheManager()


class TrackerResultPersister:

    def __init__(self, console_log: ConsoleLog):
        self.console_log = console_log
        self.profile_errors: Dict[str, str] = {}  # Keeps errors from profiles
        self.session_errors: Dict[str, str] = {}  # Keeps errors from session

    @staticmethod
    def get_profiles_to_save(tracker_results: List[TrackerResult]):
        for tracker_result in tracker_results:

            persist_profile = tracker_result.tracker_payload.is_on('saveProfile', default=True)
            if not persist_profile:
                continue

            profile = tracker_result.profile

            if isinstance(profile, Profile) and (profile.operation.new or profile.operation.needs_update()):
                # Clean operations
                profile.operation = Operation()
                yield profile

    @staticmethod
    def get_sessions_to_save(tracker_results: List[TrackerResult]) -> Generator[Session, Any, None]:
        for tracker_result in tracker_results:
            if isinstance(tracker_result.session, Session):
                if tracker_result.session.is_new() or tracker_result.session.operation.needs_update():
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
        profiles_to_save = list(self.get_profiles_to_save(tracker_results))
        FieldMapper().add_field_mappings('profile', profiles_to_save)

        results = []
        try:
            if profiles_to_save:
                result = await profile_db.save(profiles_to_save)
                if result.has_errors():
                    for id in result.ids:
                        self.profile_errors[id] = f"Error while storing profile id: {id}. Details: {result.errors}"
                results.append(result)

        except StorageException as e:
            message = "Could not save profile. Error: {}".format(str(e))
            raise FieldTypeConflictException(message, rows=e.details)

        return results

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

                        result = await session_db.save(sessions_to_add)

                        if result.has_errors():
                            for id in result.ids:
                                self.session_errors[id] = f"Error while storing session id: {id}. Details: {result.errors}"

                        # Todo this may cause errors when async, we save multiple sessions at once

                        """
                        Until the session is saved and it is usually within 1s the system can create many profiles 
                        for 1 session.  System checks if the session exists by loading it from ES. If it is a new 
                        session then is does not exist and must be saved before it can be read. So there is a 
                        1s when system thinks that the session does not exist.
            
                        If session is new we will refresh the session in ES.
                        """

                        await session_db.refresh()
                        yield result

                    # Do not update session duration. It should be calculated on the front end

                    # sessions_to_update = [session for session, save in sessions if save is False]
                    # # Update session duration
                    # for session in sessions_to_update:
                    #     await session_db.update_session_duration(session)
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

    async def __standard_event_save(self, events):
        tagged_events = [event async for event in
                         self.__tag_events(self.__get_persistent_events_without_source(events))]
        event_result = await event_db.save(tagged_events, exclude={"operation": ...})
        event_result = SaveResult(**event_result.dict())

        # Add event types
        for event in events:
            event_result.types.append(event.type)

        return event_result

    async def __save_events(self, events: Union[List[Event], Generator[Event, Any, None]]) -> Union[SaveResult,
                                                                                                    BulkInsertResult]:
        if License.has_license():
            if com_tracardi_settings.event_pool > 0:
                # Watcher runs only once.
                event_pool.watcher()
                # Add event to the pool
                async for event in self.__tag_events(self.__get_persistent_events_without_source(events)):
                    await event_pool.add(event)
                return SaveResult()
        # Standard
        return await self.__standard_event_save(events)

    async def _modify_events(self, tracker_result: TrackerResult, log_event_journal: Dict[str, StatusLog]) -> List[Event]:
        for event in tracker_result.events:

            event.metadata.time.process_time = datetime.timestamp(datetime.utcnow()) - datetime.timestamp(
                event.metadata.time.insert)

            # Reset operations
            event.operation.new = False
            event.operation.update = False

            # Reset session id if session is not saved
            # TODO ERROR - here
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

            if self.profile_errors:
                event.metadata.error = True

                for profile_id, error_message in self.profile_errors.items():
                    self.console_log.append(
                        Console(
                            flow_id=None,
                            node_id=None,
                            event_id=event.id,
                            profile_id=profile_id,
                            origin='profile',
                            class_name=TrackerResultPersister.__name__,
                            module=__name__,
                            type='error',
                            message=error_message
                        )
                    )

            if self.session_errors:
                event.metadata.error = True

                for session_id, error_message in self.session_errors.items():
                    self.console_log.append(
                        Console(
                            flow_id=None,
                            node_id=None,
                            event_id=event.id,
                            profile_id=None,
                            origin='session',
                            class_name=TrackerResultPersister.__name__,
                            module=__name__,
                            type='error',
                            message=error_message
                        )
                    )

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

            FieldMapper().add_field_mappings('event', bulk_events)
            yield await self.__save_events(bulk_events)

        except StorageException as e:
            raise FieldTypeConflictException("Could not save event. Error: {}".format(str(e)), rows=e.details)

    async def persist(self, tracker_results: List[TrackerResult]) -> CollectResult:
        return CollectResult(
            profile=await self._save_profile(tracker_results),
            session=[result async for result in self._save_session(tracker_results)],
            events=[result async for result in self._save_events(tracker_results)]
        )
