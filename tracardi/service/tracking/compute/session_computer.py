from typing import Optional

from pydantic import ValidationError
from user_agents.parsers import UserAgent

from tracardi.config import tracardi
from tracardi.exceptions.exception import BlockedException
from tracardi.service.tracking.bot import _has_google_bot_header
from tracardi.service.tracking.utils.languages import get_spoken_languages
from tracardi.domain.event_source import EventSource
from tracardi.domain.marketing import UTM
from tracardi.domain.session import Session
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.domain.geo import Geo
from tracardi.exceptions.log_handler import get_logger
from tracardi.service.tracker_config import TrackerConfig

logger = get_logger(__name__)


def _get_user_agent(session: Session, tracker_payload: TrackerPayload) -> Optional[UserAgent]:
    _user_agent = tracker_payload.get_user_agent()

    if _user_agent is not None:
        return _user_agent

    # Return user agent from session
    return session.get_user_agent()


def _compute_session_referer(session: Session, tracker_payload: TrackerPayload) -> Session:
    referer = tracker_payload.context.get('referer', None)
    if referer:
        session.context['referer'] = referer

    # Compute channel
    if isinstance(tracker_payload.source, EventSource):
        session.metadata.channel = tracker_payload.source.channel

    # Compute if BOT
    session.app.bot = _has_google_bot_header(tracker_payload.request)

    return session


def _compute_data_from_user_agent(session: Session, tracker_payload: TrackerPayload) -> Session:
    user_agent = _get_user_agent(session, tracker_payload)
    if user_agent:
        try:
            session.os.name = user_agent.os.family
        except Exception:
            if 'os' in session.context:
                session.os.name = session.context['os'].get('name', None)

        try:
            session.os.version = user_agent.os.version_string
        except Exception:
            if 'os' in session.context:
                session.os.version = session.context['os'].get('version', None)

        try:
            device_type = 'mobile' if user_agent.is_mobile else \
                'pc' if user_agent.is_pc else \
                    'tablet' if user_agent.is_tablet else \
                        'email' if user_agent.is_email_client else None
            session.device.type = device_type

        except Exception:
            if 'device' in session.context:
                session.device.type = session.context['device'].get('type', None)

        try:
            session.device.name = user_agent.device.family
        except Exception:
            if 'device' in session.context:
                session.device.name = session.context['device'].get('name', None)

        try:
            session.device.brand = user_agent.device.brand
        except Exception:
            if 'device' in session.context:
                session.device.brand = session.context['device'].get('brand', None)

        try:
            session.device.model = user_agent.device.model
        except Exception:
            if 'device' in session.context:
                session.device.model = session.context['device'].get('model', None)

        try:
            session.device.touch = user_agent.is_touch_capable
        except Exception:
            pass

        try:
            session.app.name = user_agent.browser.family  # returns 'Mobile Safari'
            session.app.version = user_agent.browser.version_string
            session.app.type = "browser"

            session.app.bot = user_agent.is_bot
        except Exception:
            if 'app' in session.context:
                session.app.name = session.context['app'].get('name', None)
                session.app.version = session.context['app'].get('version', None)
                session.app.type = session.context['app'].get('type', "unknown")

    else:

        if 'os' in session.context:
            session.os.name = session.context['os'].get('name', None)

        if 'device' in session.context:
            session.device.name = session.context['device'].get('name', None)
            session.device.brand = session.context['device'].get('brand', None)
            session.device.model = session.context['device'].get('model', None)
            session.device.touch = session.context['device'].get('model', None)
            session.device.type = session.context['device'].get('type', None)

        if 'app' in session.context:
            session.app.name = session.context['app'].get('name', None)
            session.app.version = session.context['app'].get('version', None)
            session.app.type = session.context['app'].get('type', "unknown")

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
            session.set_updated()
            return session

    return session


def update_session_utm_with_client_data(tracker_payload: TrackerPayload, session: Session) -> Session:
    if session.utm.is_empty():
        _utm = _get_tracker_utm(tracker_payload)

        # If client-side utm is sent but not available in session - update session
        if _utm:
            session.utm = _utm
            session.set_updated()

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


def _compute_languages(session, tracker_payload):
    try:
        session.app.language = session.context['browser']['local']['browser']['language']
    except Exception:
        pass

    spoken_languages, language_codes = get_spoken_languages(session, tracker_payload)
    if spoken_languages:
        session.context['language'] = list(set(spoken_languages))
    if language_codes:
        session.context['language_codes'] = list(set(language_codes))

    return session


def _compute_ip(session, tracker_payload, tracker_config):
    _value = tracker_payload.get_ip()
    if _value:
        session.device.ip = _value

    session.context['ip'] = tracker_config.ip

    return session


def _compute_bot(session, tracker_payload):
    try:
        header_from = tracker_payload.request['headers']['from']
        if header_from == "googlebot(at)googlebot.com":
            session.app.bot = True
    except Exception:
        pass


async def compute_session(session: Session,
                          tracker_payload: TrackerPayload,
                          tracker_config: TrackerConfig
                          ) -> Session:
    if session:

        # Is new session
        if session.is_new():
            # Compute session. Session is filled only when new

            # Compute the User Agent data
            session = _compute_data_from_user_agent(session, tracker_payload)

            # Compute UTM
            session = _compute_utm(session, tracker_payload.context)

            # Compute Screen size
            session = _compute_screen_size(session, tracker_payload)

            # Compute session referer, channel and bot
            session = _compute_session_referer(session, tracker_payload)

            # Compute device ip
            session = _compute_ip(session, tracker_payload, tracker_config)

            # Compute languages
            session = _compute_languages(session, tracker_payload)

        # Update missing data
        session = await update_device_geo(tracker_payload, session)
        session = update_session_utm_with_client_data(tracker_payload, session)

        # If agent is a bot stop
        if (session.app.bot or _has_google_bot_header(tracker_payload.request)) and tracardi.disallow_bot_traffic:
            raise BlockedException(f"Traffic from bot is not allowed.")

    return session
