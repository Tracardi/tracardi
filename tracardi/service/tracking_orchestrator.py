import logging
from datetime import datetime
from uuid import uuid4
import redis
from tracardi.config import tracardi, memory_cache
from tracardi.domain.entity import Entity
from tracardi.domain.event_source import EventSource
from tracardi.domain.value_object.operation import Operation
from tracardi.process_engine.debugger import Debugger
from tracardi.service.cache_manager import CacheManager
from tracardi.service.console_log import ConsoleLog
from tracardi.exceptions.log_handler import log_handler
from tracardi.domain.console import Console
from tracardi.exceptions.exception_service import get_traceback
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session, SessionMetadata, SessionTime
from tracardi.exceptions.exception import TracardiException, DuplicatedRecordException
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.service.consistency.session_corrector import correct_session
from tracardi.service.destination_orchestrator import DestinationOrchestrator
from tracardi.service.storage.driver import storage
from tracardi.service.synchronizer import ProfileTracksSynchronizer
from tracardi.service.tracking_manager import TrackingManager, TrackerResult
from tracardi.service.utils.getters import get_entity_id

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)
cache = CacheManager()


class TrackingOrchestrator:

    def __init__(self,
                 source: EventSource,
                 ip: str,
                 console_log: ConsoleLog,
                 run_async: bool = False,
                 static_profile_id: bool = False):

        self.static_profile_id = static_profile_id
        self.run_async = run_async
        self.ip = ip
        self.source = source
        self.console_log = console_log

    # todo pass tracker_payload
    async def invoke(self, tracker_payload: TrackerPayload) -> TrackerResult:

        """
        Controls the synchronization of profiles and invokes the process.
        """

        try:

            if self.source.synchronize_profiles:
                async with ProfileTracksSynchronizer(tracker_payload.profile,
                                                     wait=tracardi.sync_profile_tracks_wait,
                                                     max_repeats=tracardi.sync_profile_tracks_max_repeats):
                    return await self._invoke_track_process(tracker_payload)
            else:
                return await self._invoke_track_process(tracker_payload)

        except redis.exceptions.ConnectionError as e:
            raise TracardiException(f"Could not connect to Redis server. Connection returned error {str(e)}")

    async def _invoke_track_process(self, tracker_payload: TrackerPayload) -> TrackerResult:

        tracker_payload.set_transitional(self.source)
        tracker_payload.set_return_profile(self.source)

        # Load session from storage
        try:
            if tracker_payload.session is not None:
                session = await cache.session(
                    session_id=tracker_payload.session.id,
                    ttl=memory_cache.session_cache_ttl
                )
            else:
                session = Session(id=str(uuid4()), metadata=SessionMetadata())
                tracker_payload.force_session(session)

        except DuplicatedRecordException as e:

            # There may be a case when we have 2 sessions with the same id.
            logger.error(str(e))

            # Try to recover sessions
            list_of_profile_ids_referenced_by_session = await correct_session(tracker_payload.session.id)

            # If there is duplicated session create new random session.
            # As a consequence of this a new profile is created.
            session = Session(
                id=tracker_payload.session.id,
                metadata=SessionMetadata(
                    time=SessionTime(
                        insert=datetime.utcnow()
                    )
                ),
                operation=Operation(
                    new=True
                )
            )

            # If duplicated sessions referenced the same profile then keep it.
            if len(list_of_profile_ids_referenced_by_session) == 1:
                session.profile = Entity(id=list_of_profile_ids_referenced_by_session[0])

        if self.static_profile_id is True:
            # Get static profile - This is dangerous
            profile, session = await tracker_payload.get_static_profile_and_session(
                session,
                storage.driver.profile.load_merged_profile,
                tracker_payload.profile_less
            )
        else:
            # Get profile
            profile, session = await tracker_payload.get_profile_and_session(
                session,
                storage.driver.profile.load_merged_profile,
                tracker_payload.profile_less
            )

        # Make profile copy
        has_profile = not tracker_payload.profile_less and isinstance(profile, Profile)
        profile_copy = profile.dict(exclude={"operation": ...}) if has_profile else None

        tracking_manager = TrackingManager(
            self.console_log,
            tracker_payload,
            profile,
            session
        )

        tracker_result = await tracking_manager.invoke_track_process(
            self.source,
            self.ip
        )

        # From now on do not use profile or session, use tracker_result.profile, tracker_result.session
        # For security we override old values
        profile = tracker_result.profile
        session = tracker_result.session

        # todo do not know is makes sense - async
        if self.run_async:
            pass

        debug = tracker_payload.is_on('debugger', default=False)
        await self.save_debug_data(tracker_result.debugger, debug, get_entity_id(tracker_result.profile))

        # Send to destination
        do = DestinationOrchestrator(
            tracker_result.profile,
            tracker_result.session,
            tracker_result.events,
            self.console_log
        )
        await do.sync_destination(
            tracking_manager.has_profile,
            profile_copy,
        )

        # Save console log
        await self.save_console_log()

        # # Debugging
        # # todo save result to different index
        # if tracker_payload.is_debugging_on():
        #     debug_result = TrackerPayloadResult(**collect_result.dict())
        #     debug_result = debug_result.dict()
        #     debug_result['execution'] = debugger
        #     debug_result['segmentation'] = segmentation_result
        #     debug_result['logs'] = console_log
        #     result['debugging'] = debug_result

        # Add profile to response
        if tracker_payload.return_profile():
            raise NotImplementedError("Returning profile was removed from the system for security reasons.")

        return tracker_result

    async def save_debug_data(self, debugger, debug: bool, profile_id):
        try:
            if tracardi.track_debug or debug:
                if isinstance(debugger, Debugger) and debugger.has_call_debug_trace():
                    # Save debug info
                    await storage.driver.debug_info.save_debug_info(debugger)

        except Exception as e:
            message = "Error during saving debug info: `{}`".format(str(e))
            logger.error(message)
            self.console_log.append(
                Console(
                    flow_id=None,
                    node_id=None,
                    event_id=None,
                    profile_id=profile_id,
                    origin='profile',
                    class_name='invoke_track_process_step_2',
                    module=__name__,
                    type='error',
                    message=message,
                    traceback=get_traceback(e)
                )
            )

    # @staticmethod
    # async def _send_to_destination(profile: Profile, session: Session, events: List[Event], profile_delta):
    #     logger.info("Profile changed. Destination scheduled to run.")
    #
    #     destination_manager = DestinationManager(profile_delta,
    #                                              profile,
    #                                              session,
    #                                              payload=None,
    #                                              event=None,
    #                                              flow=None,
    #                                              memory=None)
    #     # todo performance - could be not awaited  - add to save_task
    #     await destination_manager.send_data(profile.id, events, debug=False)
    #
    # async def sync_destination(self, has_profile, profile_copy, profile: Profile, session: Session, events: List[Event]):
    #     if has_profile and profile_copy is not None:
    #         new_profile = profile.dict(exclude={"operation": ...})
    #
    #         if profile_copy != new_profile:
    #             profile_delta = DeepDiff(profile_copy, new_profile, ignore_order=True)
    #             if profile_delta:
    #                 logger.info("Profile changed. Destination scheduled to run.")
    #                 try:
    #                     await self._send_to_destination(profile, session, events, profile_delta)
    #                 except Exception as e:
    #                     # todo - this appends error to the same profile - it rather should be en event error
    #                     self.console_log.append(Console(
    #                         flow_id=None,
    #                         node_id=None,
    #                         event_id=None,
    #                         profile_id=get_entity_id(profile),
    #                         origin='destination',
    #                         class_name='DestinationManager',
    #                         module=__name__,
    #                         type='error',
    #                         message=str(e),
    #                         traceback=get_traceback(e)
    #                     ))
    #                     logger.error(str(e))

    async def save_console_log(self):
        if self.console_log:
            encoded_console_log = list(self.console_log.get_encoded())
            await storage.driver.console_log.save_all(encoded_console_log)
