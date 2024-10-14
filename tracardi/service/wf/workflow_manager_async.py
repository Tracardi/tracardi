from uuid import uuid4
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict

from tracardi.domain import ExtraInfo
from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.rule import Rule

from tracardi.config import tracardi
from tracardi.process_engine.debugger import Debugger
from tracardi.exceptions.log_handler import get_logger
from tracardi.exceptions.exception_service import get_traceback
from tracardi.domain.event import Event
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.process_engine.rules_engine import RulesEngine
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.service.merging.facade_old import merge_profile_by_merging_keys, get_merging_keys_and_values
from tracardi.service.storage.mysql.service.workflow_trigger_service import WorkflowTriggerService
from tracardi.service.utils.getters import get_entity_id
from tracardi.service.wf.domain.flow_response import FlowResponses

logger = get_logger(__name__)

EQUALS = 0
EQUALS_IF_NOT_EXISTS = 1
APPEND = 2


@dataclass
class TrackerResult:
    wf_triggered: bool
    tracker_payload: TrackerPayload
    events: List[Event]
    changed_field_timestamps: Dict[str, List]
    session: Optional[Session] = None
    profile: Optional[Profile] = None
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
                 tracker_payload: TrackerPayload,
                 profile: Optional[Profile] = None,
                 session: Optional[Session] = None
                 ):

        self.field_timestamps: Dict[str, List] = {}
        self.tracker_payload = tracker_payload
        self.profile = profile
        self.session = session
        self.profile_copy = None
        self.has_profile = not tracker_payload.profile_less and isinstance(profile, Profile)

        if tracker_payload.profile_less is True and profile is not None:
            logger.warning("Something is wrong - profile less events should not have profile attached.")

    @staticmethod
    async def merge_profile(profile: Profile) -> Profile:
        merge_key_values = get_merging_keys_and_values(profile)
        merged_profile = await merge_profile_by_merging_keys(
            profile,
            merge_by=merge_key_values)

        if merged_profile is not None:
            # Replace profile with merged_profile
            return merged_profile

        return profile

    async def get_routing_rules(self, events: List[Event]) -> Optional[List[Tuple[List[Rule], Event]]]:

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
                    )
                ],
                event
            ) for event in events if event.metadata.valid]

            logger.debug(
                f"This is scheduled event. Will load flow {self.tracker_payload.scheduled_event_config.flow_id}")
        else:
            # Routing rules are subject to caching
            wts = WorkflowTriggerService()
            event_rules = await wts.load_by_source_and_events(self.tracker_payload.source, events)

        return event_rules

    async def trigger_workflows_for_events(self, events: List[Event], debug: bool = False) -> TrackerResult:

        debugger = None
        wf_triggered = False

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
                    events_rules=event_trigger_rules
                )

                # Invoke rules engine
                try:
                    rule_invoke_result = await rules_engine.invoke(
                        ux,
                        self.tracker_payload,
                        debug
                    )

                    wf_triggered = True
                    debugger = rule_invoke_result.debugger
                    post_invoke_events = rule_invoke_result.post_invoke_events
                    invoked_rules = rule_invoke_result.invoked_rules
                    flow_responses = FlowResponses(rule_invoke_result.flow_responses)
                    self.field_timestamps.update(rule_invoke_result.changes_timestamps)

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
                    logger.error(
                        message,
                        extra=ExtraInfo.build(
                            flow_id=None,
                            node_id=None,
                            event_id=None,
                            profile_id=get_entity_id(self.profile),
                            origin='profile',
                            object=self,
                            traceback=get_traceback(e)
                        )
                    )

                # TODO Does profile need rules to merge?
                # Profile merge
                try:
                    if self.profile is not None and self.profile.needs_merging():
                        # Profile can be None if profile_less event is processed
                        self.profile = await self.merge_profile(self.profile)

                except Exception as e:
                    message = 'Profile merging returned an error `{}`'.format(str(e))
                    logger.error(
                        message,
                        extra=ExtraInfo.build(
                            flow_id=None,
                            node_id=None,
                            event_id=None,
                            profile_id=get_entity_id(self.profile),
                            origin='profile',
                            object=self,
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

            return TrackerResult(
                wf_triggered=wf_triggered,
                session=self.session,
                profile=self.profile,
                events=events,
                tracker_payload=self.tracker_payload,
                response=flow_responses.merge(),
                debugger=debugger,
                ux=ux,
                changed_field_timestamps = self.field_timestamps
            )
