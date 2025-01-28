from contextlib import asynccontextmanager
from uuid import uuid4
from typing import List, Optional, Tuple, Dict, Set

from defer.model.transport_context import TransportContext
from tracardi.context import ServerContext, Context
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.domain.rule_invoke_result import RuleInvokeResult
from tracardi.service.dependency.adapters.big_data_adapter import *
from tracardi.service.wf.field_mappings_cache import add_new_field_mappings
from tracardi.service.collector.mutation.profile import save_profile_in_db_and_cache
from tracardi.service.storage.redis.collections import Collection
from tracardi.service.tracking.locking import Lock, async_mutex
from tracardi.domain.event import flat_events_to_event
from tracardi.domain.flat_event import FlatEvent
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.service.wf.domain.tracker_result import TrackerResult
from tracardi.domain import ExtraInfo
from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.rule import Rule
from tracardi.common.logging.log_handler import get_logger
from tracardi.common.exception.exception_service import get_traceback
from tracardi.domain.event import Event
from tracardi.process_engine.rules_engine import RulesEngine
from tracardi.service.merging.facade_old import merge_profile_by_merging_keys, get_merging_keys_and_values
from tracardi.common.tools.getters import get_entity_id
from tracardi.service.wf.domain.flow_response import FlowResponses
from tracardi.service.storage.mysql.interface import workflow_trigger_dao
from tracardi.service.collector.load.profile import load_profile

logger = get_logger(__name__)

async def _get_rules_for_source_and_event_type(source_id: str, event_types: Set[str]) -> Tuple[
    Dict[str, List[Rule]], bool]:
    # Cache rules per event types

    event_type_rules = {}
    has_routes = False
    for event_type in event_types:

        routes = await workflow_trigger_dao.load_rule(event_type, source_id)

        if not has_routes and routes:
            has_routes = True

        event_type_rules[event_type] = routes

    return event_type_rules, has_routes


def _read_rule(event_type_id: str, rules: Dict[str, List[Rule]]) -> List[Rule]:
    if event_type_id not in rules:
        return []

    return rules[event_type_id]


async def _load_by_source_and_events(source_id: str, events: List[Event]) -> Optional[
    List[Tuple[List[Rule], Event]]]:
    # Get event types for valid events
    event_types = {event.type for event in events if event.metadata.valid}

    rules, has_routing_rules = await _get_rules_for_source_and_event_type(source_id, event_types)

    if not has_routing_rules:
        return None

    return [(_read_rule(event.type, rules), event) for event in events]


async def _merge_profile(profile: Profile) -> Profile:
    merge_key_values = get_merging_keys_and_values(profile)
    merged_profile = await merge_profile_by_merging_keys(
        profile,
        merge_by=merge_key_values)

    if merged_profile is not None:
        # Replace profile with merged_profile
        return merged_profile

    return profile


async def _get_routing_rules(tracker_payload: TrackerPayload, events: List[Event]) -> Optional[
    List[Tuple[List[Rule], Event]]]:
    # If one event is scheduled every event is treated as scheduled. This is TEMPORARY

    if tracker_payload.scheduled_event_config.is_scheduled():

        logger.debug("This is scheduled event. ")

        # Set ephemeral if scheduled event

        tracker_payload.set_ephemeral(False)

        event_rules = [(
            [
                Rule(
                    id=str(uuid4()),
                    name="@Internal route",
                    # event type is equal to schedule node id
                    event_type=NamedEntity(id=event.type, name=event.name),
                    flow=NamedEntity(id=tracker_payload.scheduled_event_config.flow_id, name="Scheduled"),
                    source=NamedEntity(id=event.source.id, name="Scheduled"),
                    properties={},
                    enabled=True,
                )
            ],
            event
        ) for event in events if event.metadata.valid]

        logger.debug(
            f"This is scheduled event. Will load flow {tracker_payload.scheduled_event_config.flow_id}")
    else:
        # Routing rules are subject to caching
        event_rules = await _load_by_source_and_events(tracker_payload.source.id, events)

    return event_rules


async def _get_rules_engine(tracker_payload: TrackerPayload, profile, session, events: List[Event]) -> Optional[
    RulesEngine]:
    # Get routing rules if workflow is not disabled

    event_trigger_rules = await _get_routing_rules(tracker_payload, events)

    #  If no event_rules for delivered event then no need to run rule invoke
    #  and no need for profile merging
    if event_trigger_rules is not None:
        # Skips INVALID events in invoke method
        return RulesEngine(
            session,
            profile,
            events_rules=event_trigger_rules
        )
    return None


@asynccontextmanager
async def _invoked_wf_engine(rules_engine: RulesEngine, tracker_payload, debug) -> RuleInvokeResult:
    # Invoke rules engine
    try:

        yield await rules_engine.invoke(
            tracker_payload,
            debug
        )

    except Exception as e:
        message = 'Rules engine returned an error `{}`'.format(str(e))
        logger.error(
            message,
            extra=ExtraInfo.exact(
                flow_id=None,
                node_id=None,
                event_id=None,
                profile_id=get_entity_id(rules_engine.profile),
                origin='profile',
                package=__name__,
                traceback=get_traceback(e)
            )
        )


async def _merge(profile):
    # TODO Does profile need rules to merge?
    # Profile merge
    try:
        if profile is not None and profile.needs_merging():
            # Profile can be None if profile_less event is processed
            profile = await _merge_profile(profile)

    except Exception as e:
        message = 'Profile merging returned an error `{}`'.format(str(e))
        logger.error(
            message,
            extra=ExtraInfo.exact(
                flow_id=None,
                node_id=None,
                event_id=None,
                profile_id=get_entity_id(profile),
                origin='profile',
                package=__name__,
                traceback=get_traceback(e)
            )
        )


async def _run_workflows(tracker_payload: TrackerPayload, profile: Profile, session: Session, events: List[Event],
                         debug: bool = False) -> TrackerResult:
    debugger = None
    wf_triggered = False

    ux = []
    flow_responses = FlowResponses([])
    field_timestamps: Dict[str, List] = {}

    # Workflow

    try:
        rules_engine = await _get_rules_engine(tracker_payload, profile, session, events)

        #  If no event_rules for delivered event then no need to run rule invoke
        #  and no need for profile merging
        if rules_engine is not None:

            async with _invoked_wf_engine(rules_engine, tracker_payload, debug) as wf_result:
                wf_triggered = True
                debugger = wf_result.debugger
                ux = wf_result.ux
                flow_responses = FlowResponses(wf_result.flow_responses)
                field_timestamps.update(wf_result.changed_fields)

                # Profile and session can change inside workflow
                # Check if it should not be replaced.

                if profile is not rules_engine.profile:  # Not equal
                    profile = rules_engine.profile

                if session is not rules_engine.session:
                    session = rules_engine.session

            await _merge(profile)

        else:
            logger.debug(f"No routing rules found for workflow.")

    finally:

        return TrackerResult(
            wf_triggered=wf_triggered,
            session=session,
            profile=profile,
            events=events,
            tracker_payload=tracker_payload,
            response=flow_responses.merge(),
            debugger=debugger,
            ux=ux,
            changed_field_timestamps=field_timestamps
        )


async def _trigger_workflows(profile: Profile,
                             session: Session,
                             events: List[Event],
                             tracker_payload: TrackerPayload,
                             debug: bool) -> Tuple[
    Profile, Session, List[Event], Optional[list], Optional[dict], Dict[str, List], bool]:
    # Checks rules and trigger workflows for given events

    tracker_result = await _run_workflows(tracker_payload, profile, session, events, debug)

    # Reassign results

    profile = tracker_result.profile
    session = tracker_result.session
    events = tracker_result.events
    ux = tracker_result.ux
    response = tracker_result.response

    is_wf_triggered = isinstance(tracker_result, TrackerResult) and tracker_result.wf_triggered

    if is_wf_triggered:
        # Add new fields to field mapping. New fields can be created in workflow.
        add_new_field_mappings(profile, session)

    return profile, session, events, ux, response, tracker_result.changed_field_timestamps, is_wf_triggered


async def _exec_workflow(profile_id: Optional[str], session: Session, events: List[Event],
                         tracker_payload: TrackerPayload) -> Tuple[
    Profile, Session, List[Event], Optional[list], Optional[dict], Dict[str, list], bool]:
    # Loads profile form cache
    # Profile needs to be loaded from cache. It may have changed during it was dispatched by event trigger

    # TODO EOFP - End of FlatProfile

    profile: Profile = await load_profile(profile_id)

    # Triggers workflow

    profile, session, events, ux, response, changed_fields, is_wf_triggered = await (
        # Triggers all workflows for given events
        _trigger_workflows(profile,
                           session,
                           events,
                           tracker_payload,
                           debug=False)
    )

    # Saves if changed

    if is_wf_triggered:

        # Save to cache after processing. This is needed when both async and sync workers are working
        # The state should always be in cache.

        if profile and profile.is_updated_in_workflow():
            logger.debug(f"Profile {profile.id} needs update after workflow.")

            # Apply change log to flat_profile
            auto_merge_ids = profile.set_metadata_fields_timestamps(changed_fields)
            profile.metadata.system.set_auto_merge_fields(auto_merge_ids)

            # Profile is in mutex, no profile loading from cache necessary; Save it in db and cache
            # Synchronous save
            await save_profile_in_db_and_cache(profile)

        if session and session.is_updated_in_workflow():
            logger.debug(f"Session {session.id} needs update after workflow.")

            # Profile is in mutex, that means no session for the profile should be modified.
            # No session loading from cache necessary; Save it in db and cache
            # Synchronous save
            await bd_session_adapter.save_session_to_db_and_cache(session)

    return profile, session, events, ux, response, changed_fields, is_wf_triggered


async def exec_workflow(profile_id: Optional[str], session: Session, flat_events: List[FlatEvent],
                        tracker_payload: TrackerPayload) -> Optional[Tuple[
    Profile, Session, List[Event], Optional[list], Optional[dict], Dict[str, list], bool]]:

    if not tracardi.enable_workflow:
        return None

    # Convert to events. Workflow needs Events
    # TODO EOFE - End of FlatEvent
    events = flat_events_to_event(flat_events)

    if profile_id is None:
        # Profile less execution
        return await _exec_workflow(
            profile_id, session, events, tracker_payload
        )

    profile_key = Lock.get_key(Collection.lock_tracker, "profile", profile_id)
    profile_lock = Lock(profile_key, default_lock_ttl=5)

    # Load profile - it could be changed since last loaded
    async with async_mutex(profile_lock, name='workflow-worker'):
        profile, session, events, ux, response, changed_fields, is_wf_triggered = await _exec_workflow(
            profile_id, session, events, tracker_payload
        )

    return profile, session, events, ux, response, changed_fields, is_wf_triggered


async def exec_workflow_in_queue(context: TransportContext,
                                 profile_id: Optional[str],
                                 session: Session,
                                 flat_events: List[FlatEvent],
                                 tracker_payload: TrackerPayload) -> Optional[Tuple[
    Profile, Session, List[Event], Optional[list], Optional[dict], Dict[str, list], bool]]:
    with ServerContext(Context(**context.as_context())) as c:
        return await exec_workflow(profile_id, session, flat_events, tracker_payload)
