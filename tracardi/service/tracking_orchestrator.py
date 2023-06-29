import asyncio
import logging
from collections.abc import Callable
from datetime import datetime
from typing import Type
from uuid import uuid4
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
from tracardi.exceptions.exception import DuplicatedRecordException
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.service.consistency.session_corrector import correct_session
from tracardi.service.destination_orchestrator import DestinationOrchestrator
from tracardi.service.storage.driver.elastic import debug_info as debug_info_db
from tracardi.service.storage.loaders import get_profile_loader
from tracardi.service.synchronizer import profile_synchronizer
from tracardi.service.tracker_config import TrackerConfig
from tracardi.service.tracking_manager import TrackingManager, TrackerResult, TrackingManagerBase
from tracardi.service.utils.getters import get_entity_id

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)
cache = CacheManager()


class TrackingOrchestrator:

    def __init__(self,
                 source: EventSource,
                 tracker_config: TrackerConfig,
                 on_profile_merge: Callable[[Profile], Profile] = None,
                 on_profile_ready: Type[TrackingManagerBase] = None
                 ):

        self.on_profile_ready: Type[TrackingManagerBase] = on_profile_ready
        self.on_profile_merge = on_profile_merge
        self.tracker_config = tracker_config
        self.source = source
        self.console_log = None
        self.locked = []

    async def invoke(self, tracker_payload: TrackerPayload, console_log: ConsoleLog) -> TrackerResult:

        """
        Controls the synchronization of profiles and invokes the process.
        """

        self.console_log = console_log
        return await self._invoke_track_process(tracker_payload)

    async def _invoke_track_process(self, tracker_payload: TrackerPayload) -> TrackerResult:

        # Is source ephemeral
        if self.source.transitional is True:
            tracker_payload.set_ephemeral()

        # Load session from storage
        try:
            if tracker_payload.session is None:

                # If no session in tracker payload this means that we do not need session.
                # But we may need an artificial session for workflow handling. We create
                # one but will not save it.

                session = Session(id=str(uuid4()), metadata=SessionMetadata())
                tracker_payload.force_session(session)
                tracker_payload.options.update({
                    "saveSession": False
                })

            # Loads session from ES if necessary

            # TODO Possible error

            session = await cache.session(
                session_id=tracker_payload.session.id,
                ttl=memory_cache.session_cache_ttl
            )

            # Session can be none if not found in db. User defined a session this means he wanted it.
            # At this point it is null. We handle it later.

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

        # Load profile
        profile_loader = get_profile_loader()

        # Force static profile id

        if self.tracker_config.static_profile_id is True or tracker_payload.has_static_profile_id():
            # Get static profile - This is dangerous
            profile, session = await tracker_payload.get_static_profile_and_session(
                session,
                profile_loader,
                tracker_payload.profile_less
            )
        else:

            profile, session = await tracker_payload.get_profile_and_session(
                session,
                profile_loader,
                tracker_payload.profile_less
            )

        session.context['ip'] = self.tracker_config.ip

        # Make profile copy
        has_profile = not tracker_payload.profile_less and isinstance(profile, Profile)
        profile_copy = profile.dict(exclude={"operation": ...}) if has_profile else None

        # Lock
        if has_profile and self.source.synchronize_profiles:
            key = f"profile:{profile.id}"
            await profile_synchronizer.wait_for_unlock(key, seq=tracker_payload.get_id())
            profile_synchronizer.lock_entity(key)
            self.locked.append(key)

        if self.on_profile_ready is None:
            tracking_manager = TrackingManager(
                self.console_log,
                tracker_payload,
                profile,
                session,
                self.on_profile_merge
            )

            tracker_result = await tracking_manager.invoke_track_process()
        else:
            if not issubclass(self.on_profile_ready, TrackingManagerBase):
                raise AssertionError("Callable self.on_profile_ready should be a subtype of TrackingManagerBase.")

            tracking_manager = self.on_profile_ready(
                    self.console_log,
                    tracker_payload,
                    profile,
                    session,
                    self.on_profile_merge
                )

            tracker_result = await tracking_manager.invoke_track_process()

        # From now on do not use profile or session, use tracker_result.profile, tracker_result.session
        # For security we override old values
        profile = tracker_result.profile
        session = tracker_result.session

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
            has_profile,
            profile_copy,
        )

        return tracker_result

    async def save_debug_data(self, debugger, debug: bool, profile_id):
        try:
            if tracardi.track_debug or debug:
                if isinstance(debugger, Debugger) and debugger.has_call_debug_trace():
                    # Save debug info in background
                    asyncio.create_task(debug_info_db.save_debug_info(debugger))

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
