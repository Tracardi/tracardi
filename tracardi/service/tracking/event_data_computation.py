import asyncio
from dotty_dict import dotty, Dotty

from typing import List, Tuple, Optional, Set

from tracardi.domain import ExtraInfo
from tracardi.exceptions.exception_service import get_traceback
from tracardi.exceptions.log_handler import get_logger
from tracardi.service.cache.event_mapping import load_event_mapping
from tracardi.service.cache.event_to_profile_mapping import load_event_to_profile
from tracardi.service.change_monitoring.field_change_logger import FieldChangeLogger
from tracardi.service.license import License
from tracardi.service.tracking.profile_data_computation import map_event_to_profile
from tracardi.config import tracardi
from tracardi.domain.event_source import EventSource
from tracardi.domain.payload.event_payload import EventPayload
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.domain.profile import Profile, FlatProfile
from tracardi.domain.session import Session
from tracardi.domain.event import Event
from tracardi.service.events import get_default_mappings_for
from tracardi.service.tracking.utils.function_call import default_event_call_function
from tracardi.service.utils.getters import get_entity_id

if License.has_license():
    from com_tracardi.service.event_mapper import map_event_props_to_traits, map_events_tags_and_journey
    from com_tracardi.service.tracking.consistency_check import check_profile_consistency

logger = get_logger(__name__)


def _remove_empty_dicts(dictionary):
    keys_to_remove = []
    for key, value in dictionary.items():
        if isinstance(value, dict):
            _remove_empty_dicts(value)  # Recursively check nested dictionaries
            if not value:  # Empty dictionary after recursive check
                keys_to_remove.append(key)
    for key in keys_to_remove:
        del dictionary[key]


def _auto_index_default_event_type(flat_event: Dotty, flat_profile: Optional[FlatProfile]) -> Dotty:
    event_mapping_schema = get_default_mappings_for(flat_event['type'], 'copy')

    if event_mapping_schema is not None:

        for destination, source in event_mapping_schema.items():  # type: str, str
            try:
                # Skip none existing event properties.
                if source in flat_event:
                    flat_event[destination] = flat_event[source]

            except KeyError:
                pass

    state = get_default_mappings_for(flat_event['type'], 'state')

    if state:
        if isinstance(state, str):
            if state.startswith("call:"):
                state = default_event_call_function(call_string=state, event=flat_event, profile=flat_profile)
            if state:
                flat_event['journey.state'] = state

    tags = get_default_mappings_for(flat_event['type'], 'tags')
    if tags:
        flat_event['tags.values'] = tuple(tags)
        flat_event['tags.count'] = len(tags)

    return flat_event


async def event_to_profile_mapping(flat_event: Dotty,
                                   flat_profile: Optional[FlatProfile],
                                   session: Session,
                                   field_change_logger: FieldChangeLogger
                                   ) -> Tuple[
    Dotty, Optional[FlatProfile], Set[str], FieldChangeLogger]:

    auto_merge_ids = set()

    # Default event mapping
    flat_event = _auto_index_default_event_type(flat_event, flat_profile)

    custom_event_mapping_coroutine = load_event_mapping(event_type_id=flat_event['type'])

    custom_event_to_profile_mapping_coroutine = load_event_to_profile(event_type_id=flat_event['type'])

    # Run in parallel
    custom_event_mapping, custom_event_to_profile_mapping_schemas = await asyncio.gather(
        custom_event_mapping_coroutine,
        custom_event_to_profile_mapping_coroutine
    )

    # Custom event mapping
    if License.has_license():

        # Map event properties to traits (Event Mapping)
        flat_event = map_event_props_to_traits(flat_event,
                                               custom_event_mapping)

        # Add event tags and add journey tag
        flat_event = map_events_tags_and_journey(flat_event,
                                                 custom_event_mapping)

    # Map event data to profile
    if flat_profile:
        flat_profile, field_change_logger = await map_event_to_profile(
            custom_event_to_profile_mapping_schemas,
            flat_event,
            flat_profile,
            session,
            field_change_logger
        )

        # Add fields timestamps
        if not isinstance(flat_profile['metadata.fields'], dict):
            flat_profile['metadata.fields'] = {}

        field_change_logger = field_change_logger.merge(flat_profile.log)

        # Append field changes fo metadata.fields
        auto_merge_ids = flat_profile.set_metadata_fields_timestamps(field_change_logger)

    return flat_event, flat_profile, auto_merge_ids, field_change_logger


async def make_event_from_event_payload(event_payload,
                                        profile,
                                        session,
                                        source,
                                        metadata,
                                        profile_less) -> Event:

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
        logger.error(
            event_payload.validation.message,
            extra=ExtraInfo.exact(
                flow_id=None,
                node_id=None,
                event_id=event.id,
                profile_id=get_entity_id(profile),
                origin='event-computation',
                package=__name__,
                traceback=event_payload.validation.trace
            )
        )

    return event


def update_event_from_request(tracker_payload: TrackerPayload, event: Event):
    if tracker_payload.request:
        if isinstance(event.request, dict):
            event.request.update(tracker_payload.request)
        else:
            event.request = tracker_payload.request

    return event


async def compute_events(events: List[EventPayload],
                         metadata,
                         source: EventSource,
                         session: Session,
                         profile: Optional[Profile],
                         profile_less: bool,
                         tracker_payload: TrackerPayload,
                         field_change_logger: FieldChangeLogger
                         ) -> Tuple[List[Event], Session, Optional[Profile], FieldChangeLogger]:


    event_objects = []

    if profile:
        flat_profile: Optional[FlatProfile] = FlatProfile(profile.model_dump())
        profile_metadata = profile.get_meta_data()
    else:
        flat_profile = None
        profile_metadata = None

    auto_merge_ids = set()

    for event_payload in events:

        # For performance reasons we return flat_event and after mappings convert to event.
        event = await make_event_from_event_payload(
            event_payload,
            profile,
            session,
            source,
            metadata,
            profile_less
        )

        flat_event = dotty(event.model_dump(exclude_unset=True))

        if flat_event.get('metadata.valid', True) is True:
            # Run mappings for valid event. Maps properties to traits, and adds traits
            flat_event, flat_profile, _auto_merge_ids, field_change_logger = await event_to_profile_mapping(
                flat_event,
                flat_profile,
                session,
                field_change_logger
            )

            # Combine all auto merge ids

            if _auto_merge_ids:
                auto_merge_ids = auto_merge_ids.union(_auto_merge_ids)

        # Convert to event
        event_dict = flat_event.to_dict()
        _remove_empty_dicts(event_dict)
        event = Event(**event_dict)

        # Data that is not needed for any mapping or compliance

        event = update_event_from_request(tracker_payload, event)

        debugging = tracker_payload.is_debugging_on()
        event.metadata.debug = debugging

        # todo Maybe check not needed
        if isinstance(session, Session):

            if session.metadata.status != 'active':
                session.metadata.status = 'active'
                session.set_updated()

            # Add session status
            if event.type == 'visit-started':
                session.metadata.status = 'started'
                session.set_updated()

            if event.type == 'visit-ended':
                session.metadata.status = 'ended'
                session.set_updated()

            event.session.start = session.metadata.time.insert
            event.session.duration = session.metadata.time.duration

        # Collect event objects

        event_objects.append(event)

    # Recreate Profile from flat_profile, that was changed

    if profile:
        try:

            if License.has_license():
                flat_profile = check_profile_consistency(flat_profile)

            profile = Profile(**flat_profile.to_dict())
            profile.set_meta_data(profile_metadata)
            if auto_merge_ids:
                profile.metadata.system.set_auto_merge_fields(auto_merge_ids)
        except Exception as e:
            message = f"It seems that there was an error when trying to add or update some information to " \
                      f"your profile. The error occurred because you tried to add a value that is not " \
                      f"allowed by the type of data that the profile can accept.  For instance, you may " \
                      f"have tried to add a name to a field in your profile that only accepts a single string, " \
                      f"but you provided a list of strings instead. No changes were made to your profile, and " \
                      f"the original data you sent was not copied because it did not meet the " \
                      f"requirements of the profile. " \
                      f"Details: {repr(e)}."
            logger.error(
                message,
                extra=ExtraInfo.exact(
                    flow_id=None,
                    node_id=None,
                    event_id=None,
                    profile_id=flat_profile.get('id', None),
                    origin='event-computation',
                    traceback=get_traceback(e)
                )
            )

            if not tracardi.skip_errors_on_profile_mapping:
                raise e

    return event_objects, session, profile, field_change_logger
