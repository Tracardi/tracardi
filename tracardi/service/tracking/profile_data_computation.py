from typing import Optional

import logging

from dotty_dict import dotty, Dotty
from pydantic import ValidationError

from com_tracardi.service.tracking.field_change_dispatcher import field_change_log_dispatch
from tracardi.config import tracardi
from tracardi.context import get_context
from tracardi.domain.console import Console
from tracardi.domain.event import Event
from tracardi.domain.event_to_profile import EventToProfile
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.domain.storage_record import StorageRecords
from tracardi.exceptions.exception_service import get_traceback
from tracardi.exceptions.log_handler import log_handler
from tracardi.process_engine.tql.condition import Condition
from tracardi.service.cache_manager import CacheManager
from tracardi.service.change_monitoring.field_change_monitor import FieldChangeMonitor
from tracardi.service.console_log import ConsoleLog
from tracardi.service.events import get_default_mappings_for, call_function
from tracardi.service.notation.dot_accessor import DotAccessor
from tracardi.service.utils.domains import free_email_domains
from tracardi.service.utils.getters import get_entity_id
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
        custom_mapping_schemas: StorageRecords,
        flat_event: Dotty,
        profile: Optional[Profile],
        session: Session,
        console_log: ConsoleLog) -> Profile:

    # Default event types mappings

    default_mapping_schema = get_default_mappings_for(flat_event['type'], 'profile')

    profile_updated_flag = False

    flat_profile = dotty(profile.model_dump(mode='json'))
    profile_changes = FieldChangeMonitor(flat_profile,
                                         type="profile",
                                         track_history=tracardi.enable_field_change_log)

    if default_mapping_schema is not None:
        # Copy default
        profile_changes, profile_updated_flag = copy_default_event_to_profile(
            default_mapping_schema,
            profile_changes,
            flat_event)

    # Custom event types mappings, filtered by event type

    if profile is not None and custom_mapping_schemas.total > 0:

        for custom_mapping_schema in custom_mapping_schemas:
            custom_mapping_schema = custom_mapping_schema.to_entity(EventToProfile)

            # Check condition
            if 'condition' in custom_mapping_schema.config:
                if_statement = custom_mapping_schema.config['condition']
                try:
                    dot = DotAccessor(event=Event(**flat_event.to_dict()), profile=profile, session=session)
                    result = await _check_mapping_condition_if_met(if_statement, dot)
                    if result is False:
                        continue
                except Exception as e:
                    console_log.append(Console(
                        flow_id=None,
                        node_id=None,
                        event_id=flat_event['id'],
                        profile_id=get_entity_id(profile),
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
                                event_id=flat_event['id'],
                                profile_id=get_entity_id(profile),
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
                                    event_id=flat_event['id'],
                                    profile_id=get_entity_id(profile),
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
                                profile_id=get_entity_id(profile),
                                origin='event',
                                class_name='map_event_to_profile',
                                module=__name__,
                                type='warning',
                                message=message,
                                traceback=get_traceback(e)
                            )
                        )
                        logger.error(message)

    if profile_updated_flag is True and profile_changes is not None:

        # Compute values

        compute_schema = get_default_mappings_for(flat_event['type'], 'compute')
        if compute_schema:
            for profile_property, compute_string in compute_schema:
                if not compute_string.startswith("call:"):
                    continue

                # todo keep event flat
                profile_changes[profile_property] = call_function(
                    compute_string,
                    event=Event(**flat_event.to_dict()),
                    profile=profile_changes.flat_profile)

        _profile_updated = False
        try:
            metadata = profile.get_meta_data()
            profile = Profile(**profile_changes.flat_profile)
            # New profile was created but not metadata is saved. We need to pass metadata with current index
            profile.set_meta_data(metadata)
            # Mark to update the profile
            profile.operation.update = True

            _profile_updated = True

        except ValidationError as e:
            message = f"It seems that there was an error when trying to add or update some information to " \
                      f"your profile. The error occurred because you tried to add a value that is not " \
                      f"allowed by the type of data that the profile can accept.  For instance, you may " \
                      f"have tried to add a name to a field in your profile that only accepts a single string, " \
                      f"but you provided a list of strings instead. No changes were made to your profile, and " \
                      f"the original data you sent was not copied because it did not meet the " \
                      f"requirements of the profile. " \
                      f"Details: {repr(e)}. See: event to profile copy schema for event `{flat_event['type']}`."
            console_log.append(
                Console(
                    flow_id=None,
                    node_id=None,
                    event_id=flat_event.get('id', None),
                    profile_id=get_entity_id(profile),
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

        # ToDo this should be moved to saving. Otherwise profile may not be saved but changes will

        if _profile_updated:

            # Send changed fields to be saved

            field_change_log_dispatch(
                get_context(),
                profile_changes.get_changed_values()
            )

    return profile
