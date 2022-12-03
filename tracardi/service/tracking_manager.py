import logging
from dataclasses import dataclass
from typing import List, Optional
from tracardi.config import tracardi
from tracardi.process_engine.debugger import Debugger
from tracardi.service.console_log import ConsoleLog
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.notation.dot_accessor import DotAccessor
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
from tracardi.service.tracker_config import TrackerConfig
from tracardi.service.tracker_event_validator import EventsValidationHandler
from tracardi.service.utils.getters import get_entity_id
from tracardi.service.wf.domain.flow_response import FlowResponses

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


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

    def get_response_body(self):
        body = {
            'ux': self.ux if self.ux else [],
            'response': self.response if self.response else {}

        }
        if self.profile:
            body["profile"] = {
                "id": self.profile.id
            }

        return body


class TrackingManager:

    def __init__(self,
                 console_log: ConsoleLog,
                 tracker_config: TrackerConfig,
                 tracker_payload: TrackerPayload,
                 profile: Optional[Profile] = None,
                 session: Optional[Session] = None):

        self.tracker_config = tracker_config
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
            override_old_data=True,
            limit=1000)

        if merged_profile is not None:
            # Replace profile with merged_profile
            return merged_profile

        return profile

    async def invoke_track_process(self) -> TrackerResult:

        # Get events
        events = self.tracker_payload.get_events(
            self.session,
            self.profile,
            self.has_profile)

        # Validates json schemas of events and reshapes properties

        dot = DotAccessor(
            profile=self.profile,
            session=self.session,
            payload=None,
            event=None,
            flow=None,
            memory=None
        )

        evh = EventsValidationHandler(dot, self.console_log)
        events = await evh.validate_and_reshape_events(events)

        debugger = None
        segmentation_result = None

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
                        if event.type in invoked_rules:
                            event.metadata.processed_by.rules = invoked_rules[event.type]

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
                            if self.tracker_config.on_profile_merge:
                                self.profile = await self.tracker_config.on_profile_merge(self.profile)
                            else:
                                self.profile = await self.merge_profile(self.profile)

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

        finally:
            # Synchronize post invoke events. Replace events with events changed by WF.
            # Events are saved only if marked in event.update==true
            if post_invoke_events is not None:
                synced_events = []
                for ev in events:
                    if ev.update is True and ev.id in post_invoke_events:
                        synced_events.append(post_invoke_events[ev.id])
                    else:
                        synced_events.append(ev)

                events = synced_events

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


