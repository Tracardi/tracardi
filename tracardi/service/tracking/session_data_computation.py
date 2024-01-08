import os

import logging

from typing import Tuple, Optional

from pydantic import ValidationError
from user_agents import parse

from tracardi.service.tracking.utils.languages import get_spoken_languages, get_continent
from tracardi.config import tracardi
from tracardi.domain.event_source import EventSource
from tracardi.domain.marketing import UTM
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.domain.geo import Geo
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.tracker_config import TrackerConfig
from tracardi.service.utils.languages import language_countries_dict
from tracardi.service.maxmind_geo import get_geo_maxmind_location
from tracardi.process_engine.action.v1.connectors.maxmind.geoip.model.maxmind_geolite2_client import GeoLiteCredentials

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


def _compute_data_from_user_agent(session: Session) -> Session:
    try:
        ua_string = session.context['browser']['local']['browser']['userAgent']
        user_agent = parse(ua_string)

        session.os.version = user_agent.os.version_string
        session.os.name = user_agent.os.family

        device_type = 'mobile' if user_agent.is_mobile else \
            'pc' if user_agent.is_pc else \
                'tablet' if user_agent.is_tablet else \
                    'email' if user_agent.is_email_client else None

        if 'device' in session.context:
            session.device.name = session.context['device'].get('name', user_agent.device.family)
            session.device.brand = session.context['device'].get('brand', user_agent.device.brand)
            session.device.model = session.context['device'].get('model', user_agent.device.model)
            session.device.touch = session.context['device'].get('model', user_agent.device.is_touch_capable)
            session.device.type = session.context['device'].get('type', device_type)
        else:
            session.device.name = user_agent.device.family
            session.device.brand = user_agent.device.brand
            session.device.model = user_agent.device.model
            session.device.touch = user_agent.is_touch_capable
            session.device.type = device_type

        session.app.bot = user_agent.is_bot
        session.app.name = user_agent.browser.family  # returns 'Mobile Safari'
        session.app.version = user_agent.browser.version_string
        session.app.type = "browser"

    except Exception as e:
        pass

    return session


def _get_tracker_geo(tracker_payload) -> Optional[Geo]:
    if 'location' in tracker_payload.context:

        try:
            return Geo(**tracker_payload.context['location'])

        except ValidationError as e:
            logger.error(str(e))

    return None


def _get_tracker_utm(tracker_payload) -> Optional[UTM]:
    if 'utm' in tracker_payload.context:
        try:
            return UTM(**tracker_payload.context['utm'])
        except ValidationError as e:
            logger.error(str(e))
    return None


async def update_device_geo(tracker_payload: TrackerPayload, session: Session) -> Session:
    """
    Tries to find out the geolocation of device.
    """

    if session.device.geo.is_empty():

        _geo = _get_tracker_geo(tracker_payload)

        # If client-side location is sent but not available in session - update session
        if _geo:
            session.device.geo = _geo
            session.operation.update = True
            return session

    # Still no geolocation. That means there was no 'location' sent in tracker context or
    # it failed parsing the data. But we have device IP. If the sessions geo is empty
    # then we need to make another try.
    if session.device.ip and session.device.ip != '0.0.0.0':

        # Check if max mind configured
        maxmind_license_key = os.environ.get('MAXMIND_LICENSE_KEY', None)
        maxmind_account_id = int(os.environ.get('MAXMIND_ACCOUNT_ID', 0))

        if maxmind_license_key and maxmind_account_id > 0:
            # The code checks if the session's geolocation has been assigned. If it hasn't been
            # assigned yet, it means that the profile does not have a geolocation, which could be
            # because the session is not new. In this case, regardless of whether the session is
            # new or not, the code checks if the profile's geolocation is empty.
            # If it is empty, the code proceeds to fetch the geolocation and assigns
            # it to the profile.
            _geo = await get_geo_maxmind_location(
                GeoLiteCredentials(
                    license=maxmind_license_key,
                    accountId=maxmind_account_id),
                ip=session.device.ip)

            if _geo:

                if session.device.geo.is_empty():
                    session.device.geo = _geo
                    session.operation.update = True

    return session


def update_session_utm_with_client_data(tracker_payload: TrackerPayload, session: Session) -> Session:
    if session.utm.is_empty():
        _utm = _get_tracker_utm(tracker_payload)

        # If client-side utm is sent but not available in session - update session
        if _utm:
            session.utm = _utm
            session.operation.update = True

    return session


def _compute_utm(session, tracker_payload_context: dict) -> Session:
    if 'utm' in tracker_payload_context:
        try:
            session.utm = UTM(**tracker_payload_context['utm'])
            del tracker_payload_context['utm']
        except ValidationError:
            pass
    return session


def _compute_screen_size(session: Session, tracker_payload: TrackerPayload):
    _value = tracker_payload.get_resolution()
    if _value:
        session.device.resolution = _value

    _value = tracker_payload.get_color_depth()
    if _value:
        session.device.color_depth = _value

    _value = tracker_payload.get_screen_orientation()
    if _value:
        session.device.orientation = _value

    return session


def _compute_profile_geo(profile, session, tracker_payload, spoken_languages, language_codes):
    if spoken_languages:
        if profile:
            profile.data.pii.language.spoken = session.context['language']

    if profile and 'geo' not in profile.aux:
        profile.aux['geo'] = {}

    # Aux markets

    markets = []
    for lang_code in language_codes:
        if lang_code in language_countries_dict:
            markets += language_countries_dict[lang_code]

    if markets:
        profile.aux['geo']['markets'] = markets

    # Continent

    continent = get_continent(tracker_payload)
    if continent:
        profile.aux['geo']['continent'] = continent

    return profile


def compute_session(session: Session,
                    profile: Profile,
                    tracker_payload: TrackerPayload,
                    tracker_config: TrackerConfig
                    ) -> Tuple[Session, Profile]:

    # Compute the User Agent data
    session = _compute_data_from_user_agent(session)

    # Compute UTM
    session = _compute_utm(session, tracker_payload.context)

    # Compute Screen size
    session = _compute_screen_size(session, tracker_payload)

    # Compute channel
    if isinstance(tracker_payload.source, EventSource):
        session.metadata.channel = tracker_payload.source.channel

    # Compute device ip
    _value = tracker_payload.get_ip()
    if _value:
        session.device.ip = _value

    session.context['ip'] = tracker_config.ip

    # Compute languages

    spoken_languages, language_codes = get_spoken_languages(session, tracker_payload)
    if spoken_languages:
        session.context['language'] = list(set(spoken_languages))

    try:
        session.app.language = session.context['browser']['local']['browser']['language']
    except Exception:
        pass

    # Compute Profile
    profile = _compute_profile_geo(profile, session, tracker_payload, spoken_languages, language_codes)

    return session, profile
