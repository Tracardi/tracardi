from typing import List

from tracardi.domain import ExtraInfo
from tracardi.domain.event_compute import EventCompute
from tracardi.domain.event_to_profile import EventToProfile
from tracardi.domain.flat_event import FlatEvent
from tracardi.domain.flat_profile import FlatProfile
from tracardi.domain.session import Session
from tracardi.exceptions.exception_service import get_traceback
from tracardi.exceptions.log_handler import get_logger
from tracardi.process_engine.tql.condition import Condition
from tracardi.service.events import get_default_mappings_for
from tracardi.service.notation.dot_accessor import DotAccessor
from tracardi.service.tracking.utils.function_call import default_event_call_function
from tracardi.service.tracking.utils.languages import get_continent
from tracardi.service.utils.domains import free_email_domains
from tracardi.service.events import copy_default_event_to_profile
from tracardi.service.utils.languages import language_countries_dict

EQUALS = 0
EQUALS_IF_NOT_EXISTS = 1
APPEND = 2

logger = get_logger(__name__)


def update_profile_last_geo(session: Session, flat_profile: FlatProfile) -> FlatProfile:
    if not session.device.geo.is_empty():
        _geo = session.device.geo.model_dump(mode="json")
        if not flat_profile.has('data.devices.last.geo', equal=_geo):
            flat_profile['data.devices.last.geo'] = _geo
            flat_profile.set_updated()
    return flat_profile


def update_profile_email_type(flat_profile: FlatProfile) -> FlatProfile:
    if flat_profile.has_not_empty('data.contact.email.main') and not flat_profile.has('aux.email.free'):
        email_parts = flat_profile['data.contact.email.main'].split('@')
        if len(email_parts) > 1:
            email_domain = email_parts[1]

            flat_profile['aux.email.free'] = email_domain in free_email_domains
            flat_profile.set_updated()
    return flat_profile


def update_profile_visits(session: Session, flat_profile: FlatProfile) -> FlatProfile:
    # Calculate only on first click in visit

    if session.is_new():
        flat_profile.set_visit_time()
        flat_profile.set_if_none('metadata.time.visit.count', 0)
        flat_profile['metadata.time.visit.count'] += 1
        flat_profile.set_updated()

    return flat_profile


def update_profile_time(session: Session, flat_profile: FlatProfile) -> FlatProfile:
    # Set time zone form session
    if session.context:
        try:
            flat_profile['metadata.time.visit.tz'] = session.context['time']['tz']
        except KeyError:
            pass
    return flat_profile


async def _check_mapping_condition_if_met(if_statement, dot: DotAccessor):
    condition = Condition()
    return await condition.evaluate(if_statement, dot)


async def map_event_to_profile(
        custom_mapping_schemas: List[EventToProfile],
        flat_event: FlatEvent,
        flat_profile: FlatProfile,
        session: Session,
) -> FlatProfile:
    # Default event types mappings

    default_mapping_schema = get_default_mappings_for(flat_event['type'], 'profile')

    if default_mapping_schema is not None:
        # Copy default
        flat_profile = copy_default_event_to_profile(
            default_mapping_schema,
            flat_profile,
            flat_event
        )

    # Custom event types mappings, filtered by event type

    if len(custom_mapping_schemas) > 0:

        for custom_mapping_schema in custom_mapping_schemas:

            # Check condition
            if 'condition' in custom_mapping_schema.config:
                if_statement = custom_mapping_schema.config['condition']
                try:
                    # Todo converting to Profile and event may be not performant, maybe extend dot accessor to take dotty
                    dot = DotAccessor(event=flat_event, profile=flat_profile,
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
                                flat_profile[profile_ref] = [flat_event[event_ref]]
                            elif isinstance(flat_profile[profile_ref], list):
                                flat_profile[profile_ref].append(flat_event[event_ref])
                            elif not isinstance(flat_profile[profile_ref], dict):
                                flat_profile[profile_ref] = [flat_profile[profile_ref], flat_event[event_ref]]
                            else:
                                raise KeyError(
                                    f"Can not append data {flat_event[event_ref]} to {flat_profile[profile_ref]} at profile@{profile_ref}")

                        elif operation == EQUALS_IF_NOT_EXISTS:
                            if profile_ref not in flat_profile:
                                flat_profile[profile_ref] = flat_event[event_ref]
                            elif flat_profile[profile_ref] is None:
                                flat_profile[profile_ref] = flat_event[event_ref]
                            elif isinstance(flat_profile[profile_ref], str):
                                __value = flat_profile[profile_ref].strip()
                                if not __value:
                                    flat_profile[profile_ref] = flat_event[event_ref]
                            elif isinstance(flat_profile[profile_ref], (list, dict)):
                                if not flat_profile[profile_ref]:
                                    flat_profile[profile_ref] = flat_event[event_ref]
                        else:
                            flat_profile[profile_ref] = flat_event[event_ref]

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

    profile_updated_flag = flat_profile.has_changes()
    print(3, profile_updated_flag)
    compute_schema = get_default_mappings_for(flat_event['type'], "compute")
    if compute_schema:
        compute_schema = EventCompute(**compute_schema)

        # Run only on change but there was no change
        if compute_schema.run_on_profile_change() and profile_updated_flag is False:
            # Terminate earlier
            return flat_profile

        # Compute values

        for profile_property, compute_string in compute_schema.yield_functions():

            # Compute value
            computation_result = default_event_call_function(
                compute_string,
                event=flat_event,
                profile=flat_profile)

            # Set property if defined
            if isinstance(profile_property, str):
                flat_profile[profile_property] = computation_result
                profile_updated_flag = True

    if profile_updated_flag is True:
        flat_profile.mark_for_update()

    return flat_profile


def compute_profile_aux_geo_markets(flat_profile: FlatProfile, session, tracker_payload) -> FlatProfile:
    if 'language' in session.context:
        if flat_profile.instanceof('data.pii.language.spoken', list) and isinstance(session.context['language'],
                                                                                    list):

            unique_values = set(flat_profile['data.pii.language.spoken'] + session.context['language'])
            flat_profile['data.pii.language.spoken'] = list(unique_values)
        else:
            flat_profile['data.pii.language.spoken'] = list(set(session.context['language']))

    if not flat_profile.has('aux.geo'):
        flat_profile['aux.geo'] = {}

    # Aux markets

    markets = []
    if 'language_codes' in session.context:
        for lang_code in session.context['language_codes']:
            if lang_code in language_countries_dict:
                markets += language_countries_dict[lang_code]

    if markets:
        flat_profile['aux.geo.markets'] = markets

    # Continent

    continent = get_continent(tracker_payload)
    if continent:
        flat_profile['aux.geo.continent'] = continent

    return flat_profile
