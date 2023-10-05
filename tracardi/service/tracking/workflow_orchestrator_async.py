from typing import List
import logging
from tracardi.config import tracardi
from tracardi.domain.event import Event
from tracardi.domain.event_source import EventSource
from tracardi.service.cache_manager import CacheManager
from tracardi.service.console_log import ConsoleLog
from tracardi.exceptions.log_handler import log_handler
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.service.tracker_config import TrackerConfig
from tracardi.service.tracking.workflow_manager_async import WorkflowManagerAsync, TrackerResult


logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)
cache = CacheManager()


class WorkflowOrchestratorAsync:

    def __init__(self,
                 source: EventSource,
                 tracker_config: TrackerConfig,
                 console_log
                 ):

        self.tracker_config = tracker_config
        self.source = source
        self.console_log = console_log
        self.locked = []

    async def lock_and_invoke(self,
                              tracker_payload: TrackerPayload,
                              events: List[Event],
                              profile: Profile,
                              session: Session,
                              debug: bool = False
                              ) -> TrackerResult:

        """
        Controls the synchronization of profiles and invokes the process.
        """

        # Session and Profile is loaded and attached to tracker payload

        has_profile = not tracker_payload.profile_less and isinstance(profile, Profile)

        if has_profile and self.source.synchronize_profiles:
            # ToDO profile locking
            pass

        # Workflow starts here

        tracking_manager = WorkflowManagerAsync(
            self.console_log,
            tracker_payload,
            profile,
            session,
            on_profile_merge=None
        )

        tracker_result = await tracking_manager.invoke_workflow(events, debug)

        return tracker_result
