import logging
from uuid import uuid4
from dataclasses import dataclass
from typing import List, Optional, Callable
from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.rule import Rule

from tracardi.config import tracardi
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
from tracardi.service.storage.driver.elastic import debug_info as debug_info_db
from tracardi.service.storage.driver.elastic import rule as rule_db
from tracardi.service.storage.driver.elastic import flow as flow_db
from tracardi.service.utils.getters import get_entity_id
from tracardi.service.wf.domain.flow_response import FlowResponses

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)
cache = CacheManager()

EQUALS = 0
EQUALS_IF_NOT_EXISTS = 1
APPEND = 2


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


class WorkflowManagerAsync:

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

    async def get_routing_rules(self, events: List[Event]):

        # If one event is scheduled every event is treated as scheduled. This is TEMPORARY

        if self.tracker_payload.scheduled_event_config.is_scheduled():

            logger.debug("This is scheduled event. ")

            # Set ephemeral if scheduled event

            self.tracker_payload.set_ephemeral(False)

            event_rules = [(
                [
                    Rule(
                        id=str(uuid4()),
                        name="@Internal route",
                        # event type is equal to schedule node id
                        event_type=NamedEntity(id=event.type, name=event.name),
                        flow=NamedEntity(id=self.tracker_payload.scheduled_event_config.flow_id, name="Scheduled"),
                        source=NamedEntity(id=event.source.id, name="Scheduled"),
                        properties={},
                        enabled=True,
                    ).model_dump()
                ],
                event
            ) for event in events if event.metadata.valid]

            logger.debug(
                f"This is scheduled event. Will load flow {self.tracker_payload.scheduled_event_config.flow_id}")
        else:
            # Routing rules are subject to caching
            event_rules = await rule_db.load_rules(self.tracker_payload.source, events)

        return event_rules

    async def _save_debug_data(self, debugger, profile_id):
        try:
            if isinstance(debugger, Debugger) and debugger.has_call_debug_trace():
                # Save debug info in background
                await debug_info_db.save_debug_info(debugger)
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

    async def invoke_workflow(self, events: List[Event], debug: bool = False) -> TrackerResult:

        debugger = None

        # Get routing rules if workflow is not disabled

        event_trigger_rules = await self.get_routing_rules(events) if tracardi.enable_workflow else None

        ux = []
        post_invoke_events = None
        flow_responses = FlowResponses([])

        # Workflow

        try:
            #  If no event_rules for delivered event then no need to run rule invoke
            #  and no need for profile merging
            if tracardi.enable_workflow and event_trigger_rules is not None:

                # Skips INVALID events in invoke method
                rules_engine = RulesEngine(
                    self.session,
                    self.profile,
                    events_rules=event_trigger_rules,
                    console_log=self.console_log
                )

                # Invoke rules engine
                try:
                    rule_invoke_result = await rules_engine.invoke(
                        flow_db.load_production_flow,
                        ux,
                        self.tracker_payload,
                        debug
                    )

                    debugger = rule_invoke_result.debugger
                    post_invoke_events = rule_invoke_result.post_invoke_events
                    invoked_rules = rule_invoke_result.invoked_rules
                    flow_responses = FlowResponses(rule_invoke_result.flow_responses)

                    # Profile and session can change inside workflow
                    # Check if it should not be replaced.

                    if self.profile is not rules_engine.profile:  # Not equal
                        self.profile = rules_engine.profile

                    if self.session is not rules_engine.session:
                        self.session = rules_engine.session

                    # Append invoked rules to event metadata

                    # TODO Event MUTATION - FORBIDDEN - ADD ARTEFACTS

                    for event in events:
                        event.metadata.processed_by.rules = invoked_rules[event.id]
                        event.metadata.processed_by.flows = rule_invoke_result.invoked_flows

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

                # TODO Does profile need rules to merge?
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
                                class_name=str(WorkflowManagerAsync.__class__),
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

            # TODO Event MUTATION - FORBIDDEN - ADD ARTEFACTS

            # This is event discarding

            if post_invoke_events is not None:
                synced_events = []
                for ev in events:

                    # Replace event with event changed by workflow
                    if ev.operation.update is True and ev.id in post_invoke_events:
                        ev = post_invoke_events[ev.id]

                    synced_events.append(ev)

                events = synced_events

            # Debug data
            if tracardi.track_debug or debug:
                await self._save_debug_data(debugger, get_entity_id(self.profile))

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
