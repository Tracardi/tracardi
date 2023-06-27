import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Callable
from uuid import uuid4
from dotty_dict import dotty
from pydantic.error_wrappers import ValidationError
from tracardi.service.events import auto_index_default_event_type, copy_default_event_to_profile, \
    get_default_event_type_mapping, call_function

from tracardi.service.notation.dot_accessor import DotAccessor

from tracardi.domain.event_to_profile import EventToProfile
from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.rule import Rule
from tracardi.process_engine.tql.condition import Condition
from tracardi.service.license import License, INDEXER

from tracardi.service.destinations.dispatchers import event_destination_dispatch
from tracardi.config import tracardi, memory_cache
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
from tracardi.service.storage.driver.elastic import segment as segment_db
from tracardi.service.storage.driver.elastic import rule as rule_db
from tracardi.service.storage.driver.elastic import flow as flow_db
from tracardi.service.utils.getters import get_entity_id
from tracardi.service.wf.domain.flow_response import FlowResponses

if License.has_service(INDEXER):
    from com_tracardi.service.event_indexer import index_event_traits

if License.has_license():
    from com_tracardi.service.data_compliance import DataComplianceHandler

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

                # Auto index event
                _event = auto_index_default_event_type(_event, self.profile)
                if License.has_service(INDEXER):
                    _event = await index_event_traits(_event, self.console_log)

                event_list.append(_event)
        return event_list

    async def invoke_track_process(self) -> TrackerResult:

        # Get events
        events = await self.get_events()
        flat_events = {event.id: dotty(event.dict()) for event in events}

        # Anonymize, data compliance
        if License.has_license():
            if self.profile is not None:
                events = await DataComplianceHandler(self.profile, self.console_log).comply(events, flat_events)

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
                        name="@Internal route",
                        # event type is equal to schedule node id
                        event_type=NamedEntity(id=event.type, name=event.name),
                        flow=NamedEntity(id=self.tracker_payload.scheduled_event_config.flow_id, name="Scheduled"),
                        source=NamedEntity(id=event.source.id, name="Scheduled"),
                        properties={},
                        enabled=True,
                    ).dict()
                ],
                event
            ) for event in events]

            logger.debug(
                f"This is scheduled event. Will load flow {self.tracker_payload.scheduled_event_config.flow_id}")
        else:
            # Routing rules are subject to caching
            event_rules = await rule_db.load_rules(self.tracker_payload.source, events)

        # Copy data from event to profile. This must be run just before processing.

        for event in events:

            # Default event types coping

            copy_schema = get_default_event_type_mapping(event.type, 'profile')

            profile_updated_flag = False
            flat_profile = None
            flat_event = None

            if copy_schema is not None:
                flat_profile = dotty(self.profile.dict())
                flat_event = flat_events[event.id]

                # Copy default
                flat_profile, profile_updated_flag = copy_default_event_to_profile(copy_schema, flat_profile,
                                                                                   flat_event)

            # Custom event types coping, filtered by event type

            coping_schemas = await cache.event_to_profile_coping(
                event_type=event.type,
                ttl=memory_cache.event_to_profile_coping_ttl)

            if self.profile is not None and coping_schemas.total > 0:

                # Flat data can be already prepared in default coping

                if flat_event is None:
                    flat_event = flat_events[event.id]
                if flat_profile is None:
                    flat_profile = dotty(self.profile.dict())

                for coping_schema in coping_schemas:
                    coping_schema = coping_schema.to_entity(EventToProfile)

                    # Check condition
                    if 'condition' in coping_schema.config:
                        if_statement = coping_schema.config['condition']
                        try:
                            dot = DotAccessor(event=event, profile=self.profile, session=self.session)
                            condition = Condition()
                            result = await condition.evaluate(if_statement, dot)
                            if result is False:
                                continue
                        except Exception as e:
                            self.console_log.append(Console(
                                flow_id=None,
                                node_id=None,
                                event_id=event.id,
                                profile_id=get_entity_id(self.profile),
                                origin='event',
                                class_name=TrackingManager.__name__,
                                module=__name__,
                                type='error',
                                message=f"Routing error. "
                                        f"An error occurred when coping data from event to profile. "
                                        f"There is error in the conditional trigger settings for event "
                                        f"`{event.type}`."
                                        f"Could not parse or access data for if statement: `{if_statement}`. "
                                        f"Data was not copied but the event was routed to the next step. ",
                                traceback=get_traceback(e)
                            ))
                            continue

                    # Custom Copy

                    if coping_schema.event_to_profile:
                        allowed_profile_fields = (
                            "data", "traits", "pii", "ids", "stats", "segments", "interests", "consents", "aux")
                        for event_ref, profile_ref, operation in coping_schema.items():
                            if not profile_ref.startswith(allowed_profile_fields):
                                self.console_log.append(
                                    Console(
                                        flow_id=None,
                                        node_id=None,
                                        event_id=event.id,
                                        profile_id=get_entity_id(self.profile),
                                        origin='event',
                                        class_name=TrackingManager.__name__,
                                        module=__name__,
                                        type='warning',
                                        message=f"You are trying to copy the data to unknown field in profile. "
                                                f"Your profile reference `{profile_ref}` does not start with typical "
                                                f"fields that are {allowed_profile_fields}. Please check if there isn't "
                                                f"an error in your copy schema. Data will not be copied if it does not "
                                                f"match Profile schema.",
                                        traceback=[]
                                    )
                                )

                            try:
                                if operation == APPEND:
                                    if profile_ref not in flat_profile:
                                        flat_profile[profile_ref] = [flat_event[event_ref]]
                                    elif isinstance(flat_profile[profile_ref], list):
                                        flat_profile[profile_ref].append(flat_event[event_ref])
                                    elif not isinstance(flat_profile[profile_ref], dict):
                                        flat_profile[profile_ref] = [flat_profile[profile_ref]]
                                        flat_profile[profile_ref].append(flat_event[event_ref])
                                    else:
                                        raise KeyError(
                                            f"Can not append data {flat_event[event_ref]} to {flat_profile[profile_ref]} at profile@{profile_ref}")

                                elif operation == EQUALS_IF_NOT_EXISTS:
                                    if profile_ref not in flat_profile:
                                        flat_profile[profile_ref] = flat_event[event_ref]
                                else:
                                    flat_profile[profile_ref] = flat_event[event_ref]

                                profile_updated_flag = True

                            except KeyError as e:
                                if event_ref.startswith(("properties", "traits")):
                                    message = f"Can not copy data from event `{event_ref}` to profile `{profile_ref}`. " \
                                              f"Original data send to processing. Error message: {repr(e)} key."
                                else:
                                    message = f"Can not copy data from event `{event_ref}` to profile `{profile_ref}`. " \
                                              f"Maybe `properties.{event_ref}` or `traits.{event_ref}` could work. " \
                                              f"Original data send to processing. Error message: {repr(e)} key."
                                self.console_log.append(
                                    Console(
                                        flow_id=None,
                                        node_id=None,
                                        event_id=event.id,
                                        profile_id=get_entity_id(self.profile),
                                        origin='event',
                                        class_name=TrackingManager.__name__,
                                        module=__name__,
                                        type='warning',
                                        message=message,
                                        traceback=get_traceback(e)
                                    )
                                )
                                logger.error(message)

            if profile_updated_flag is True and flat_profile is not None:

                # Compute values

                compute_schema = get_default_event_type_mapping(event.type, 'compute')
                if compute_schema:
                    for profile_property, compute_string in compute_schema:
                        if not compute_string.startswith("call:"):
                            continue
                        flat_profile[profile_property] = call_function(compute_string, event=event, profile=flat_profile)

                try:
                    self.profile = Profile(**flat_profile)
                    self.profile.operation.update = True
                except ValidationError as e:
                    message = f"It seems that there was an error when trying to add or update some information to " \
                              f"your profile. The error occurred because you tried to add a value that is not " \
                              f"allowed by the type of data that the profile can accept.  For instance, you may " \
                              f"have tried to add a name to a field in your profile that only accepts a single string, " \
                              f"but you provided a list of strings instead. No changes were made to your profile, and " \
                              f"the original data you sent was not copied because it did not meet the " \
                              f"requirements of the profile. " \
                              f"Details: {repr(e)}. See: event to profile copy schema for event `{event.type}`."
                    self.console_log.append(
                        Console(
                            flow_id=None,
                            node_id=None,
                            event_id=event.id,
                            profile_id=get_entity_id(self.profile),
                            origin='event',
                            class_name=TrackingManager.__name__,
                            module=__name__,
                            type='error',
                            message=message,
                            traceback=get_traceback(e)
                        )
                    )
                    logger.error(message)



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
                        flow_db.load_production_flow,
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
                                                            segment_db.load_segments)

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
