import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Callable
from uuid import uuid4
from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.rule import Rule
from tracardi.domain.type import Type
from tracardi.service.license import License, INDEXER

from tracardi.service.destinations.dispatchers import event_destination_dispatch
from tracardi.config import tracardi
from tracardi.domain.enum.event_status import COLLECTED
from tracardi.domain.payload.event_payload import EventPayload
from tracardi.process_engine.debugger import Debugger
from tracardi.service.cache_manager import CacheManager
from tracardi.service.console_log import ConsoleLog
from tracardi.exceptions.log_handler import log_handler
from tracardi.domain.console import Console
from tracardi.exceptions.exception_service import get_traceback
from tracardi.domain.event import Event
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.process_engine.rules_engine import RulesEngine
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.service.profile_merger import ProfileMerger
from tracardi.service.segmentation import segment
from tracardi.service.storage.driver import storage
from tracardi.service.utils.getters import get_entity_id
from tracardi.service.wf.domain.flow_response import FlowResponses

if License.has_service(INDEXER):
    from com_tracardi.service.event_indexer import index_event_traits

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)
cache = CacheManager()


@dataclass
class TrackerResult:
    tracker_payload: TrackerPayload
    events: List[Event]
    session: Optional[Session] = None
    profile: Optional[Profile] = None
    console_log: Optional[ConsoleLog] = None
    response: Optional[dict] = None
    debugger: Optional[Debugger] = None
    ux: Optional[list] = None

    def get_response_body(self, tracker_payload_id: str):
        body = {
            'task': tracker_payload_id,
            'ux': self.ux if self.ux else [],
            'response': self.response if self.response else {}

        }
        if self.profile:
            body["profile"] = {
                "id": self.profile.id
            }

        return body


class TrackingManagerBase(ABC):

    @abstractmethod
    def __init__(self,
                 console_log: ConsoleLog,
                 tracker_payload: TrackerPayload,
                 profile: Optional[Profile] = None,
                 session: Optional[Session] = None,
                 on_profile_merge: Callable[[Profile], Profile] = None
                 ):
        pass

    @abstractmethod
    async def invoke_track_process(self) -> TrackerResult:
        pass


class TrackingManager(TrackingManagerBase):

    def __init__(self,
                 console_log: ConsoleLog,
                 tracker_payload: TrackerPayload,
                 profile: Optional[Profile] = None,
                 session: Optional[Session] = None,
                 on_profile_merge: Callable[[Profile], Profile] = None
                 ):

        self.on_profile_merge = on_profile_merge
        self.tracker_payload = tracker_payload
        self.profile = profile
        self.session = session
        self.console_log = console_log
        self.profile_copy = None
        self.has_profile = not tracker_payload.profile_less and isinstance(profile, Profile)

        if self.has_profile:
            # Calculate only on first click in visit
            if session.operation.new:
                logger.info("Profile visits metadata changed.")
                profile.metadata.time.visit.set_visits_times()
                profile.metadata.time.visit.count += 1
                profile.operation.update = True
                # Set time zone form session
                if session.context:
                    try:
                        profile.metadata.time.visit.tz = session.context['time']['tz']
                    except KeyError:
                        pass

        if tracker_payload.profile_less is True and profile is not None:
            logger.warning("Something is wrong - profile less events should not have profile attached.")

    @staticmethod
    async def merge_profile(profile: Profile) -> Profile:
        merge_key_values = ProfileMerger.get_merging_keys_and_values(profile)
        merged_profile = await ProfileMerger.invoke_merge_profile(
            profile,
            merge_by=merge_key_values,
            limit=1000)

        if merged_profile is not None:
            # Replace profile with merged_profile
            return merged_profile

        return profile

    async def get_events(self) -> List[Event]:
        event_list = []
        if self.tracker_payload.events:
            debugging = self.tracker_payload.is_debugging_on()
            for event in self.tracker_payload.events:  # type: EventPayload
                _event = event.to_event(
                    self.tracker_payload.metadata,
                    self.tracker_payload.source,
                    self.session,
                    self.profile,
                    self.has_profile)

                _event.metadata.status = COLLECTED
                _event.metadata.debug = debugging
                _event.metadata.channel = self.tracker_payload.source.channel

                # Append session data
                if isinstance(self.session, Session):
                    _event.session.start = self.session.metadata.time.insert
                    _event.session.duration = self.session.metadata.time.duration

                # Add tracker payload properties as event request values

                if isinstance(_event.request, dict):
                    _event.request.update(self.tracker_payload.request)
                else:
                    _event.request = self.tracker_payload.request

                # Index event
                if License.has_service(INDEXER):
                    _event = await index_event_traits(_event, self.console_log)

                event_list.append(_event)
        return event_list

    async def invoke_track_process(self) -> TrackerResult:

        # Get events
        events = await self.get_events()

        debugger = None
        segmentation_result = None

        # If one event is scheduled every event is treated as scheduled. This is TEMPORARY

        if self.tracker_payload.scheduled_event_config.is_scheduled():
            logger.debug("This is scheduled event. ")
            # Set ephemeral if scheduled event

            self.tracker_payload.set_ephemeral(False)

            event_rules = [(
                [
                    Rule(
                        id=str(uuid4()),
                        name="Schedule route rule",
                        event=Type(type=event.type),  # event type is equal to schedule node id
                        flow=NamedEntity(id=self.tracker_payload.scheduled_event_config.flow_id, name="Scheduled"),
                        source=NamedEntity(id=event.source.id, name="Scheduled"),
                        enabled=True,
                    ).dict()
                ],
                event
            ) for event in events]

            logger.debug(f"This is scheduled event. Will load flow {self.tracker_payload.scheduled_event_config.flow_id}")
        else:
            # Routing rules are subject to caching
            event_rules = await storage.driver.rule.load_rules(self.tracker_payload.source, events)

        ux = []
        post_invoke_events = None
        flow_responses = FlowResponses([])

        try:
            #  If no event_rules for delivered event then no need to run rule invoke
            #  and no need for profile merging
            if event_rules is not None:

                # Skips INVALID events in invoke method
                rules_engine = RulesEngine(
                    self.session,
                    self.profile,
                    events_rules=event_rules,
                    console_log=self.console_log
                )

                # Invoke rules engine
                try:
                    rule_invoke_result = await rules_engine.invoke(
                        storage.driver.flow.load_production_flow,
                        ux,
                        self.tracker_payload
                    )

                    debugger = rule_invoke_result.debugger
                    post_invoke_events = rule_invoke_result.post_invoke_events
                    invoked_rules = rule_invoke_result.invoked_rules
                    flow_responses = FlowResponses(rule_invoke_result.flow_responses)

                    # Profile and session can change inside workflow
                    # Check if it should not be replaced.

                    if self.profile is not rules_engine.profile:
                        self.profile = rules_engine.profile

                    if self.session is not rules_engine.session:
                        self.session = rules_engine.session

                    # Append invoked rules to event metadata

                    for event in events:
                        event.metadata.processed_by.rules = invoked_rules[event.id]
                        event.metadata.processed_by.flows = rule_invoke_result.invoked_flows

                    # Segment only if there is profile

                    if isinstance(self.profile, Profile):
                        # Segment
                        segmentation_result = await segment(self.profile,
                                                            rule_invoke_result.ran_event_types,
                                                            storage.driver.segment.load_segments)

                except Exception as e:
                    message = 'Rules engine or segmentation returned an error `{}`'.format(str(e))
                    self.console_log.append(
                        Console(
                            flow_id=None,
                            node_id=None,
                            event_id=None,
                            profile_id=get_entity_id(self.profile),
                            origin='profile',
                            class_name='invoke_track_process_step_2',
                            module=__name__,
                            type='error',
                            message=message,
                            traceback=get_traceback(e)
                        )
                    )
                    logger.error(message)

                # Profile merge
                try:
                    if self.profile is not None:  # Profile can be None if profile_less event is processed
                        if self.profile.operation.needs_merging():
                            if self.on_profile_merge:
                                self.profile = await self.on_profile_merge(self.profile)
                            else:
                                self.profile = await self.merge_profile(self.profile)
                    else:
                        self.console_log.append(
                            Console(
                                flow_id=None,
                                node_id=None,
                                event_id=None,
                                profile_id=get_entity_id(self.profile),
                                origin='profile',
                                class_name=TrackingManager.__class__,
                                module=__name__,
                                type='warning',
                                message="Can not merge profile-less event."
                            )
                        )

                except Exception as e:
                    message = 'Profile merging returned an error `{}`'.format(str(e))
                    logger.error(message)
                    self.console_log.append(
                        Console(
                            flow_id=None,
                            node_id=None,
                            event_id=None,
                            profile_id=get_entity_id(self.profile),
                            origin='profile',
                            class_name='invoke_track_process_step_2',
                            module=__name__,
                            type='error',
                            message=message,
                            traceback=get_traceback(e)
                        )
                    )
            else:
                logger.debug(f"No routing rules found for workflow.")

        finally:
            # Synchronize post invoke events. Replace events with events changed by WF.
            # Events are saved only if marked in event.operation.update==true
            if post_invoke_events is not None:
                synced_events = []
                for ev in events:
                    if ev.operation.update is True and ev.id in post_invoke_events:
                        ev = post_invoke_events[ev.id]

                    synced_events.append(ev)

                events = synced_events

            # Run event destination
            load_destination_task = cache.event_destination
            await event_destination_dispatch(load_destination_task,
                                             self.profile,
                                             self.session,
                                             events,
                                             self.tracker_payload.debug)

            return TrackerResult(
                session=self.session,
                profile=self.profile,
                events=events,
                tracker_payload=self.tracker_payload,
                console_log=self.console_log,
                response=flow_responses.merge(),
                debugger=debugger,
                ux=ux
            )
