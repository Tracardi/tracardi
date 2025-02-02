from typing import List, Generator, AsyncGenerator

from tracardi.domain import ExtraInfo
from tracardi.domain.event_compute import EventCompute
from tracardi.domain.event_to_profile import EventToProfile
from tracardi.domain.field_change import FieldChange
from tracardi.domain.flat_event import FlatEvent
from tracardi.domain.flat_profile import FlatProfile
from tracardi.domain.geo import Geo
from tracardi.domain.session import Session
from tracardi.common.exception.exception_service import get_traceback
from tracardi.common.logging.log_handler import get_logger
from tracardi.process_engine.tql.condition import Condition
from tracardi.service.events import get_default_mappings_for
from tracardi.common.dot_notation.dot_accessor import DotAccessor
from tracardi.service.tracking.compute.geo_location_computer import get_geo_location
from tracardi.service.tracking.utils.function_call import default_event_call_function
from tracardi.common.time.date import now_in_utc
from tracardi.common.db.domains import free_email_domains
from tracardi.service.events import copy_default_event_to_profile
from tracardi.common.db.languages import language_countries_dict

EQUALS = 0
EQUALS_IF_NOT_EXISTS = 1
APPEND = 2
EQUALS_IF_CHANGE_NEWER = 3
EQUALS_IF_CHANGE_OLDER = 4

logger = get_logger(__name__)


def update_profile_last_geo(flat_profile: FlatProfile, context: dict) -> Generator[FieldChange, None, None]:
    geo = get_geo_location(context)

    if isinstance(geo, Geo) and not geo.is_empty():
        _geo = geo.model_dump(mode="json")
        if not flat_profile.has('data.devices.last.geo', equal=_geo):
            yield FieldChange(
                field='data.devices.last.geo',
                value=_geo
            )


def update_profile_email_type(flat_profile: FlatProfile) -> Generator[FieldChange, None, None]:
    if flat_profile.has_not_empty('data.contact.email.main') and not flat_profile.has('aux.email.free'):
        email_parts = flat_profile['data.contact.email.main'].split('@')
        if len(email_parts) > 1:
            email_domain = email_parts[1]

            yield FieldChange(
                field='aux.email.free',
                value=email_domain in free_email_domains
            )


def update_profile_visits(is_new_session: bool, flat_profile: FlatProfile) -> Generator[FieldChange, None, None]:
    # Calculate only on first click in visit

    if is_new_session:
        flat_profile.set_visit_time()

        if flat_profile.has('metadata.time.visit.current'):
            yield FieldChange(
                field='metadata.time.visit.last',
                value=flat_profile['metadata.time.visit.current']
            )

        yield FieldChange(
            field='metadata.time.visit.current',
            value=now_in_utc()
        )

        if 'metadata.time.visit.count' not in flat_profile:
            yield FieldChange(
                field='metadata.time.visit.count',
                value=0
            )


def update_profile_time(flat_profile: FlatProfile, session_context: dict) -> Generator[FieldChange, None, None]:
    # Set time zone form session
    if session_context:
        try:
            tz = session_context['time']['tz']
            if flat_profile.get('metadata.time.visit.tz', None) != tz:
                yield FieldChange(
                    field='metadata.time.visit.tz',
                    value=session_context['time']['tz']
                )
        except KeyError:
            pass


async def _check_mapping_condition_if_met(if_statement, dot: DotAccessor):
    condition = Condition()
    return await condition.evaluate(if_statement, dot)


async def _custom_event_to_profile_mapping(custom_mapping_schemas,
                                           flat_profile: FlatProfile,
                                           flat_event: FlatEvent,
                                           session: Session) -> AsyncGenerator[FieldChange, None]:
    if custom_mapping_schemas is not None and len(custom_mapping_schemas) > 0:
        print(1, flat_event['properties'])
        event_create_timestamp = flat_event.metadata_time.create.timestamp()
        for custom_mapping_schema in custom_mapping_schemas:

            # Check condition
            if 'condition' in custom_mapping_schema.config:
                if_statement = custom_mapping_schema.config['condition']
                try:
                    dot = DotAccessor(event=flat_event,
                                      profile=flat_profile,
                                      session=session)
                    result = await _check_mapping_condition_if_met(if_statement, dot)
                    if result is False:
                        continue
                except Exception as e:
                    logger.error(
                        f"Routing error. "
                        f"An error occurred when coping data from event to profile. "
                        f"There is error in the conditional trigger settings for event "
                        f"`{flat_event['type']}`."
                        f"Could not parse or access data for if statement: `{if_statement}`. "
                        f"Data was not copied but the event was routed to the next step. ",
                        extra=ExtraInfo.exact(
                            flow_id=None,
                            node_id=None,
                            event_id=flat_event.get('id', None),
                            profile_id=flat_profile.get('id', None),
                            origin='profile-computation',
                            package=__name__,
                            traceback=get_traceback(e)
                        )
                    )
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

                        logger.warning(
                            message,
                            extra=ExtraInfo.exact(
                                origin='profile-computation',
                                flow_id=None,
                                node_id=None,
                                event_id=flat_event.get('id', None),
                                profile_id=flat_profile.get('id', None),
                                package=__name__
                            )
                        )
                        continue

                    try:
                        if not flat_event[event_ref]:
                            message = f"Value of event@{event_ref} is None or empty. " \
                                      f"No data has been assigned to profile@{profile_ref}"
                            logger.warning(
                                message,
                                extra=ExtraInfo.exact(
                                    flow_id=None,
                                    node_id=None,
                                    event_id=flat_event.get('id', None),
                                    profile_id=flat_profile.get('id', None),
                                    origin='profile-computation',
                                    package=__name__,
                                )
                            )
                            continue

                        if operation == APPEND:
                            if profile_ref not in flat_profile:
                                yield FieldChange(
                                    field=profile_ref,
                                    value=[flat_event[event_ref]],
                                    ts=event_create_timestamp
                                )
                            elif flat_profile.instanceof(profile_ref, list):

                                yield FieldChange(
                                    field=profile_ref,
                                    value=flat_profile[profile_ref] + [flat_event[event_ref]],
                                    ts=event_create_timestamp
                                )

                            elif not flat_profile.instanceof(profile_ref, dict):
                                yield FieldChange(
                                    field=profile_ref,
                                    value=[flat_profile[profile_ref], flat_event[event_ref]],
                                    ts=event_create_timestamp
                                )
                            else:
                                raise KeyError(
                                    f"Can not append data {flat_event[event_ref]} to {flat_profile[profile_ref]} at profile@{profile_ref}")

                        elif operation == EQUALS_IF_NOT_EXISTS:
                            if profile_ref not in flat_profile:
                                yield FieldChange(
                                    field=profile_ref,
                                    value=flat_event[event_ref],
                                    ts=event_create_timestamp
                                )
                            elif flat_profile[profile_ref] is None:
                                yield FieldChange(
                                    field=profile_ref,
                                    value=flat_event[event_ref],
                                    ts=event_create_timestamp
                                )
                            elif flat_profile.instanceof(profile_ref, str):
                                __value = flat_profile[profile_ref].strip()
                                if not __value:
                                    yield FieldChange(
                                        field=profile_ref,
                                        value=flat_event[event_ref],
                                        ts=event_create_timestamp
                                    )
                            elif flat_profile.instanceof(profile_ref, (list, dict)):
                                if not flat_profile[profile_ref]:
                                    yield FieldChange(
                                        field=profile_ref,
                                        value=flat_event[event_ref],
                                        ts=event_create_timestamp
                                    )
                        elif operation == EQUALS_IF_CHANGE_NEWER:
                            # Field in profile is older then event create date
                            if flat_profile.is_field_older_then(profile_ref, timestamp=event_create_timestamp):
                                yield FieldChange(
                                    field=profile_ref,
                                    value=flat_event[event_ref],
                                    ts=event_create_timestamp
                                )

                        elif operation == EQUALS_IF_CHANGE_OLDER:
                            # Field in profile is older then event create date
                            if flat_profile.is_field_newer_then(profile_ref, timestamp=event_create_timestamp):
                                yield FieldChange(
                                    field=profile_ref,
                                    value=flat_event[event_ref],
                                    ts=event_create_timestamp
                                )
                        else:
                            yield FieldChange(
                                field=profile_ref,
                                value=flat_event[event_ref],
                                ts=event_create_timestamp
                            )

                    except KeyError as e:
                        if event_ref.startswith(("properties", "traits")):
                            message = f"Can not copy data from event `{event_ref}` to profile `{profile_ref}`. " \
                                      f"Data was not copied. Error message: {repr(e)} key."
                        else:
                            message = f"Can not copy data from event `{event_ref}` to profile `{profile_ref}`. " \
                                      f"Maybe `properties.{event_ref}` or `traits.{event_ref}` could work. " \
                                      f"Data was not copied. Error message: {repr(e)} key."

                        logger.warning(
                            message,
                            extra=ExtraInfo.exact(
                                flow_id=None,
                                node_id=None,
                                event_id=flat_event.get('id', None),
                                profile_id=flat_profile.get('id', None),
                                origin='event',
                                class_name='map_event_to_profile',
                                package=__name__,
                                traceback=get_traceback(e)
                            )
                        )


def _computed_event_props_to_profile(flat_profile: FlatProfile, flat_event: FlatEvent) -> Generator[
    FieldChange, None, None]:
    # TODO may not be needed as flat_profile.has_changes() delivers it.
    profile_updated_flag = flat_profile.has_changes()
    event_create_timestamp = flat_event.metadata_time.create.timestamp()

    compute_schema = get_default_mappings_for(flat_event.type, "compute")
    if compute_schema:
        compute_schema = EventCompute(**compute_schema)

        # Run only on change but there was no change
        if compute_schema.run_on_profile_change() and profile_updated_flag is False:
            # Terminate earlier
            return

        # Compute values

        for profile_property, compute_string in compute_schema.yield_functions():

            # Compute value
            computation_result = default_event_call_function(
                compute_string,
                event=flat_event,
                profile=flat_profile)

            # Set property if defined
            if isinstance(profile_property, str):
                yield FieldChange(
                    field=profile_property,
                    value=computation_result,
                    ts=event_create_timestamp
                )


async def map_event_to_profile(
        custom_mapping_schemas: List[EventToProfile],
        flat_event: FlatEvent,
        flat_profile: FlatProfile,
        session: Session,
) -> AsyncGenerator[FieldChange, None]:
    # Default event types mappings

    default_mapping_schema = get_default_mappings_for(flat_event['type'], 'profile')

    if default_mapping_schema is not None:
        # Copy default
        for item in copy_default_event_to_profile(
                default_mapping_schema,
                flat_profile,
                flat_event
        ):
            yield item

    # Custom event types mappings, filtered by event type
    async for item in _custom_event_to_profile_mapping(
            custom_mapping_schemas,
            flat_profile,
            flat_event,
            session):
        yield item

    for item in _computed_event_props_to_profile(flat_profile, flat_event):
        yield item


def compute_profile_aux_geo_markets(flat_profile: FlatProfile, session_context: dict) -> Generator[
    FieldChange, None, None]:
    if 'language' in session_context:
        if flat_profile.instanceof('data.pii.language.spoken', list) and isinstance(session_context['language'],
                                                                                    list):
            old_values = set(flat_profile.get('data.pii.language.spoken', []))
            new_values = old_values | set(session_context['language'])
            if new_values != old_values:
                yield FieldChange(
                    field='data.pii.language.spoken',
                    value=list(new_values)
                )
        else:
            yield FieldChange(
                field='data.pii.language.spoken',
                value=list(set(session_context['language']))
            )

    # Aux markets

    markets = []
    if 'language_codes' in session_context:
        for lang_code in session_context['language_codes']:
            if lang_code in language_countries_dict:
                markets += language_countries_dict[lang_code]

    if markets and markets != flat_profile.get('aux.geo.markets', None):
        yield FieldChange(
            field='aux.geo.markets',
            value=markets
        )
