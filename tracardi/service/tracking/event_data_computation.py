import logging

import asyncio
from dotty_dict import dotty, Dotty

from typing import List, Tuple, Optional

from tracardi.exceptions.exception_service import get_traceback
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.change_monitoring.field_change_monitor import FieldTimestampMonitor
from tracardi.service.license import License
from tracardi.service.tracking.profile_data_computation import map_event_to_profile
from tracardi.config import memory_cache, tracardi
from tracardi.domain.console import Console
from tracardi.domain.event_source import EventSource
from tracardi.domain.payload.event_payload import EventPayload
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.domain.profile import Profile, FlatProfile
from tracardi.domain.session import Session
from tracardi.domain.event import Event
from tracardi.service.cache_manager import CacheManager
from tracardi.service.console_log import ConsoleLog
from tracardi.service.events import get_default_mappings_for
from tracardi.service.tracking.utils.function_call import default_event_call_function
from tracardi.service.utils.getters import get_entity_id

if License.has_license():
    from com_tracardi.service.event_mapper import map_event_props_to_traits, map_events_tags_and_journey

cache = CacheManager()
logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


def _remove_empty_dicts(dictionary):
    keys_to_remove = []
    for key, value in dictionary.items():
        if isinstance(value, dict):
            _remove_empty_dicts(value)  # Recursively check nested dictionaries
            if not value:  # Empty dictionary after recursive check
                keys_to_remove.append(key)
    for key in keys_to_remove:
        del dictionary[key]


def _auto_index_default_event_type(flat_event: Dotty, flat_profile: FlatProfile) -> Dotty:
    event_mapping_schema = get_default_mappings_for(flat_event['type'], 'copy')

    if event_mapping_schema is not None:

        for destination, source in event_mapping_schema.items():  # type: str, str
            try:

                # if destination not in dot_event:
                #     logger.warning(f"While indexing type {event.type}. "
                #                    f"Property destination {destination} could not be found in event schema.")

                # Skip none existing event properties.
                if source in flat_event:
                    flat_event[destination] = flat_event[source]
                    del flat_event[source]
            except KeyError:
                pass

    state = get_default_mappings_for(flat_event['type'], 'state')

    if state:
        if isinstance(state, str):
            if state.startswith("call:"):
                state = default_event_call_function(call_string=state, event=flat_event, profile=flat_profile)

            flat_event['journey.state'] = state

    tags = get_default_mappings_for(flat_event['type'], 'tags')
    if tags:
        flat_event['tags.values'] = tuple(tags)
        flat_event['tags.count'] = len(tags)

    return flat_event


async def event_to_profile_mapping(flat_event: Dotty,
                                            flat_profile: FlatProfile,
                                            session:Session,
                                            source: EventSource,
                                            console_log: ConsoleLog) -> Tuple[
    Dotty, FlatProfile, Optional[FieldTimestampMonitor]]:

    # Default event mapping
    flat_event = _auto_index_default_event_type(flat_event, flat_profile)

    custom_event_mapping_coroutine = cache.event_mapping(
        event_type=flat_event['type'],
        ttl=memory_cache.event_metadata_cache_ttl)

    custom_event_to_profile_mapping_coroutine = cache.event_to_profile_coping(
        event_type=flat_event['type'],
        ttl=memory_cache.event_to_profile_coping_ttl)

    # Run in parallel
    custom_event_mapping, custom_event_to_profile_mapping_schemas = await asyncio.gather(
        custom_event_mapping_coroutine,
        custom_event_to_profile_mapping_coroutine
    )

    # Custom event mapping
    if License.has_license():

        # Map event properties to traits
        flat_event = map_event_props_to_traits(flat_event,
                                               custom_event_mapping,
                                               console_log)

        # Add event tags and add journey tag
        flat_event = map_events_tags_and_journey(flat_event,
                                                 custom_event_mapping)

    # Map event data to profile
    profile_changes = None
    if flat_profile:
        flat_profile, profile_changes = await map_event_to_profile(
            custom_event_to_profile_mapping_schemas,
            flat_event,
            flat_profile,
            session,
            source,
            console_log)

        # Add fields timestamps

        if not isinstance(flat_profile['metadata.fields'], dict):
            flat_profile['metadata.fields'] = {}

        # Append field changes fo metadata.fields
        flat_profile.set_metadata_fields_timestamps(profile_changes)

    return flat_event, flat_profile, profile_changes


async def make_event_from_event_payload(event_payload,
                                        profile,
                                        session,
                                        source,
                                        metadata,
                                        profile_less,
                                        console_log) -> Event:

    # Get event
    event = event_payload.to_event(
        metadata,
        source,
        session,
        profile,
        profile_less)

    event.metadata.channel = source.channel

    if event_payload.merging is not None:
        event.metadata.error = event_payload.merging.error
        # Mark as merged if not error
        event.metadata.merge = not event_payload.merging.error

    if event_payload.validation is not None and event_payload.validation.error is True:
        event.metadata.valid = False

        console_log.append(
            Console(
                flow_id=None,
                node_id=None,
                event_id=event.id,
                profile_id=get_entity_id(profile),
                origin='event',
                class_name='compute_events',
                module=__name__,
                type='error',
                message=event_payload.validation.message,
                traceback=event_payload.validation.trace
            )
        )

    return event


async def compute_events(events: List[EventPayload],
                         metadata,
                         source: EventSource,
                         session: Session,
                         profile: Profile,
                         profile_less: bool,
                         console_log: ConsoleLog,
                         tracker_payload: TrackerPayload
                         ) -> Tuple[List[Event], Session, Profile, Optional[FieldTimestampMonitor]]:

    field_timestamp_monitor = None
    event_objects = []

    if profile:
        flat_profile = FlatProfile(profile.model_dump())
        profile_metadata = profile.get_meta_data()
    else:
        flat_profile = None
        profile_metadata = None

    for event_payload in events:

        # For performance reasons we return flat_event and after mappings convert to event.
        event = await make_event_from_event_payload(
            event_payload,
            profile,
            session,
            source,
            metadata,
            profile_less,
            console_log
        )

        flat_event = dotty(event.model_dump(exclude_unset=True))

        if flat_event.get('metadata.valid', True) is True:
            # Run mappings for valid event. Maps properties to traits, and adds traits
            flat_event, flat_profile, field_timestamp_monitor = await event_to_profile_mapping(
                flat_event,
                flat_profile,
                session,
                source,
                console_log)

        # Convert to event
        event_dict = flat_event.to_dict()
        _remove_empty_dicts(event_dict)
        event = Event(**event_dict)

        # Data that is not needed for any mapping or compliance

        if tracker_payload.request:
            if isinstance(event.request, dict):
                event.request.update(tracker_payload.request)
            else:
                event.request = tracker_payload.request

        debugging = tracker_payload.is_debugging_on()
        event.metadata.debug = debugging

        # todo Maybe check not needed
        if isinstance(session, Session):

            if session.metadata.status != 'active':
                session.metadata.status = 'active'
                session.operation.update = True

            # Add session status
            if event.type == 'visit-started':
                session.metadata.status = 'started'
                session.operation.update = True

            if event.type == 'visit-ended':
                session.metadata.status = 'ended'
                session.operation.update = True

            event.session.start = session.metadata.time.insert
            event.session.duration = session.metadata.time.duration

        # Collect event objects

        event_objects.append(event)

    # Recreate Profile from flat_profile, that was changed

    if profile:
        try:
            profile = Profile(**flat_profile.to_dict())
            profile.set_meta_data(profile_metadata)
        except Exception as e:
            message = f"It seems that there was an error when trying to add or update some information to " \
                      f"your profile. The error occurred because you tried to add a value that is not " \
                      f"allowed by the type of data that the profile can accept.  For instance, you may " \
                      f"have tried to add a name to a field in your profile that only accepts a single string, " \
                      f"but you provided a list of strings instead. No changes were made to your profile, and " \
                      f"the original data you sent was not copied because it did not meet the " \
                      f"requirements of the profile. " \
                      f"Details: {repr(e)}."
            console_log.append(
                Console(
                    flow_id=None,
                    node_id=None,
                    event_id=None,
                    profile_id=flat_profile.get('id', None),
                    origin='event',
                    class_name='map_event_to_profile',
                    module=__name__,
                    type='error',
                    message=message,
                    traceback=get_traceback(e)
                )
            )
            logger.error(message)
            if not tracardi.skip_errors_on_profile_mapping:
                raise e

    return event_objects, session, profile, field_timestamp_monitor
