from typing import Tuple, List

import logging

from dotty_dict import Dotty

from tracardi.config import tracardi
from tracardi.domain.console import Console
from tracardi.domain.event import Event
from tracardi.domain.event_compute import EventCompute
from tracardi.domain.event_source import EventSource
from tracardi.domain.event_to_profile import EventToProfile
from tracardi.domain.profile import Profile, FlatProfile
from tracardi.domain.session import Session
from tracardi.exceptions.exception_service import get_traceback
from tracardi.exceptions.log_handler import log_handler
from tracardi.process_engine.tql.condition import Condition
from tracardi.service.cache_manager import CacheManager
from tracardi.service.change_monitoring.field_change_monitor import FieldTimestampMonitor
from tracardi.service.console_log import ConsoleLog
from tracardi.service.events import get_default_mappings_for
from tracardi.service.notation.dot_accessor import DotAccessor
from tracardi.service.tracking.utils.function_call import default_event_call_function
from tracardi.service.utils.domains import free_email_domains
from tracardi.service.events import copy_default_event_to_profile

cache = CacheManager()

EQUALS = 0
EQUALS_IF_NOT_EXISTS = 1
APPEND = 2

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


def update_profile_last_geo(session: Session, profile: Profile) -> Profile:
    if not session.device.geo.is_empty():
        _geo = session.device.geo
        if profile.data.devices.last.geo.is_empty() or _geo != profile.data.devices.last.geo:
            profile.data.devices.last.geo = _geo
            profile.operation.update = True
    return profile


def update_profile_email_type(profile: Profile) -> Profile:
    if profile.data.contact.email.main and ('email' not in profile.aux or 'free' not in profile.aux['email']):
        email_parts = profile.data.contact.email.main.split('@')
        if len(email_parts) > 1:
            email_domain = email_parts[1]

            if 'email' not in profile.aux:
                profile.aux['email'] = {}

            profile.aux['email']['free'] = email_domain in free_email_domains
            profile.operation.update = True
    return profile


def update_profile_visits(session: Session, profile: Profile) -> Profile:
    # Calculate only on first click in visit

    if session.operation.new:
        profile.metadata.time.visit.set_visits_times()
        profile.metadata.time.visit.count += 1
        profile.operation.update = True

    return profile


def update_profile_time(session: Session, profile: Profile) -> Profile:
    # Set time zone form session
    if session.context:
        try:
            profile.metadata.time.visit.tz = session.context['time']['tz']
        except KeyError:
            pass
    return profile


async def _check_mapping_condition_if_met(if_statement, dot: DotAccessor):
    condition = Condition()
    return await condition.evaluate(if_statement, dot)


async def map_event_to_profile(
        custom_mapping_schemas: List[EventToProfile],
        flat_event: Dotty,
        flat_profile: FlatProfile,
        session: Session,
        source: EventSource,
        console_log: ConsoleLog) -> Tuple[FlatProfile, FieldTimestampMonitor]:

    # Default event types mappings

    default_mapping_schema = get_default_mappings_for(flat_event['type'], 'profile')

    profile_updated_flag = False

    profile_changes = FieldTimestampMonitor(flat_profile,
                                            type="profile",
                                            profile_id=flat_profile.get('id', None),
                                            event_id=flat_event.get('id', None),
                                            session=session,
                                            source=source)

    if default_mapping_schema is not None:
        # Copy default
        profile_changes, profile_updated_flag = copy_default_event_to_profile(
            default_mapping_schema,
            profile_changes,
            flat_event)

    # Custom event types mappings, filtered by event type

    if len(custom_mapping_schemas) > 0:

        for custom_mapping_schema in custom_mapping_schemas:

            # Check condition
            if 'condition' in custom_mapping_schema.config:
                if_statement = custom_mapping_schema.config['condition']
                try:
                    # Todo converting to Profile and event may be not performant, maybe extend dot accessor to take dotty
                    dot = DotAccessor(event=Event(**flat_event.to_dict()), profile=Profile(**flat_profile.to_dict()), session=session)
                    result = await _check_mapping_condition_if_met(if_statement, dot)
                    if result is False:
                        continue
                except Exception as e:
                    console_log.append(Console(
                        flow_id=None,
                        node_id=None,
                        event_id=flat_event.get('id', None),
                        profile_id=flat_profile.get('id', None),
                        origin='event',
                        class_name='map_event_to_profile',
                        module=__name__,
                        type='error',
                        message=f"Routing error. "
                                f"An error occurred when coping data from event to profile. "
                                f"There is error in the conditional trigger settings for event "
                                f"`{flat_event['type']}`."
                                f"Could not parse or access data for if statement: `{if_statement}`. "
                                f"Data was not copied but the event was routed to the next step. ",
                        traceback=get_traceback(e)
                    ))
                    continue

            # Custom Copy

            if custom_mapping_schema.event_to_profile:
                allowed_profile_fields = (
                    "data",
                    "traits",
                    "ids",
                    "stats",
                    "segments",
                    "interests",
                    "consents",
                    "aux",
                    "misc",
                    "trash")
                for event_ref, profile_ref, operation in custom_mapping_schema.items():
                    if not profile_ref.startswith(allowed_profile_fields):
                        message = f"You are trying to copy the data to unknown field in profile. " \
                                  f"Your profile reference `{profile_ref}` does not start with typical " \
                                  f"fields that are {allowed_profile_fields}. Please check if there isn't " \
                                  f"an error in your copy schema. Data will not be copied if it does not " \
                                  f"match Profile schema."
                        console_log.append(
                            Console(
                                flow_id=None,
                                node_id=None,
                                event_id=flat_event.get('id', None),
                                profile_id=flat_profile.get('id', None),
                                origin='event',
                                class_name='map_event_to_profile',
                                module=__name__,
                                type='warning',
                                message=message,
                                traceback=[]
                            )
                        )
                        logger.warning(message)
                        continue

                    try:
                        if not flat_event[event_ref]:
                            message = f"Value of event@{event_ref} is None or empty. " \
                                      f"No data has been assigned to profile@{profile_ref}"
                            console_log.append(
                                Console(
                                    flow_id=None,
                                    node_id=None,
                                    event_id=flat_event.get('id', None),
                                    profile_id=flat_profile.get('id', None),
                                    origin='event',
                                    class_name='map_event_to_profile',
                                    module=__name__,
                                    type='warning',
                                    message=message
                                )
                            )
                            logger.warning(message)
                            continue

                        if operation == APPEND:
                            if profile_ref not in profile_changes:
                                profile_changes[profile_ref] = [flat_event[event_ref]]
                            elif isinstance(profile_changes[profile_ref], list):
                                profile_changes[profile_ref].append(flat_event[event_ref])
                            elif not isinstance(profile_changes[profile_ref], dict):
                                profile_changes[profile_ref] = [profile_changes[profile_ref], flat_event[event_ref]]
                            else:
                                raise KeyError(
                                    f"Can not append data {flat_event[event_ref]} to {profile_changes[profile_ref]} at profile@{profile_ref}")

                        elif operation == EQUALS_IF_NOT_EXISTS:
                            if profile_ref not in profile_changes:
                                profile_changes[profile_ref] = flat_event[event_ref]
                            elif profile_changes[profile_ref] is None:
                                profile_changes[profile_ref] = flat_event[event_ref]
                            elif isinstance(profile_changes[profile_ref], str) :
                                __value = profile_changes[profile_ref].strip()
                                if not __value:
                                    profile_changes[profile_ref] = flat_event[event_ref]
                            elif isinstance(profile_changes[profile_ref], (list, dict)):
                                if not profile_changes[profile_ref]:
                                    profile_changes[profile_ref] = flat_event[event_ref]
                        else:
                            profile_changes[profile_ref] = flat_event[event_ref]

                        profile_updated_flag = True

                    except KeyError as e:
                        if event_ref.startswith(("properties", "traits")):
                            message = f"Can not copy data from event `{event_ref}` to profile `{profile_ref}`. " \
                                      f"Data was not copied. Error message: {repr(e)} key."
                        else:
                            message = f"Can not copy data from event `{event_ref}` to profile `{profile_ref}`. " \
                                      f"Maybe `properties.{event_ref}` or `traits.{event_ref}` could work. " \
                                      f"Data was not copied. Error message: {repr(e)} key."
                        console_log.append(
                            Console(
                                flow_id=None,
                                node_id=None,
                                event_id=flat_event.get('id', None),
                                profile_id=flat_profile.get('id', None),
                                origin='event',
                                class_name='map_event_to_profile',
                                module=__name__,
                                type='warning',
                                message=message,
                                traceback=get_traceback(e)
                            )
                        )
                        logger.error(message)

    compute_schema = get_default_mappings_for(flat_event['type'], "compute")
    if compute_schema:
        compute_schema = EventCompute(**compute_schema)

        # Run only on change but no change
        if compute_schema.run_on_profile_change() and profile_updated_flag is False:
            return flat_profile, profile_changes

        # Compute values

        for profile_property, compute_string in compute_schema.yield_functions():

            # Compute value
            computation_result = default_event_call_function(
                compute_string,
                event=flat_event,
                profile=profile_changes.flat_profile)

            # Set property if defined
            if isinstance(profile_property, str):
                profile_changes[profile_property] = computation_result

        flat_profile['operation.update'] = True


    return flat_profile, profile_changes
