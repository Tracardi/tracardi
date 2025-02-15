from typing import Optional

from pydantic import ValidationError

from tracardi.config import tracardi
from tracardi.common.exception.exception import BlockedException
from tracardi.domain.flat_session import FlatSession
from tracardi.service.tracking.bot import _has_google_bot_header
from tracardi.service.tracking.user_agent import _get_user_agent
from tracardi.service.tracking.utils.languages import get_spoken_languages
from tracardi.domain.event_source import EventSource
from tracardi.domain.marketing import UTM
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.domain.geo import Geo
from tracardi.common.logging.log_handler import get_logger
from tracardi.domain.tracker_config import TrackerConfig

logger = get_logger(__name__)


def _compute_session_referer(flat_session: FlatSession, tracker_payload: TrackerPayload) -> FlatSession:
    referer = tracker_payload.context.get('referer', None)
    if referer:
        flat_session['context.referer'] = referer

    # Compute channel
    if isinstance(tracker_payload.source, EventSource):
        flat_session['metadata.channel'] = tracker_payload.source.channel

    # Compute if BOT
    flat_session['app.bot'] = _has_google_bot_header(tracker_payload.request)

    return flat_session

def _or_value(a, b):
    try:
        return a
    except Exception:
        return b

def _compute_data_from_user_agent(flat_session: FlatSession, tracker_payload: TrackerPayload) -> FlatSession:
    user_agent = _get_user_agent(flat_session, tracker_payload)
    if user_agent:

        flat_session['os.name'] = _or_value(user_agent.os.family, flat_session.get('context.os.name', None))
        flat_session['os.version'] = _or_value(user_agent.os.version_string,
                                               flat_session.get('context.os.version', None))

        device_type = 'mobile' if user_agent.is_mobile else \
            'pc' if user_agent.is_pc else \
                'tablet' if user_agent.is_tablet else \
                    'email' if user_agent.is_email_client else None
        flat_session['device.type'] = _or_value(device_type, flat_session.get('context.device.type', None))

        flat_session['device.name'] = _or_value(user_agent.device.family, flat_session.get('context.device.name', None))
        flat_session['device.brand'] = _or_value(user_agent.device.brand,
                                                 flat_session.get('context.device.brand', None))
        flat_session['device.model'] = _or_value(user_agent.device.model,
                                                 flat_session.get('context.device.model', None))


        try:
            flat_session['device.touch'] = user_agent.is_touch_capable
        except Exception:
            pass

        flat_session['app.name'] = _or_value(user_agent.browser.family, flat_session.get('context.app.name', None))
        flat_session['app.version'] = _or_value(user_agent.browser.version_string, flat_session.get('context.app.version', None))
        flat_session['app.bot'] = _or_value(user_agent.is_bot, flat_session.get('context.app.type', "unknown"))

    else:

        flat_session['os.name'] = flat_session.get('context.os.name', None)

        flat_session['device.type'] =flat_session.get('context.device.type', None)
        flat_session['device.name'] =flat_session.get('context.device.name', None)
        flat_session['device.brand'] = flat_session.get('context.device.brand', None)
        flat_session['device.model'] = flat_session.get('context.device.model', None)

        flat_session['app.name'] = flat_session.get('context.app.name', None)
        flat_session['app.version'] = flat_session.get('context.app.version', None)
        flat_session['app.bot'] = flat_session.get('context.app.type', "unknown")

    return flat_session


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


async def update_device_geo(tracker_payload: TrackerPayload, flat_session: FlatSession) -> FlatSession:
    """
    Tries to find out the geolocation of device.
    """

    if flat_session.get('device.geo.country.name', None) is None:

        _geo = _get_tracker_geo(tracker_payload)

        # If client-side location is sent but not available in session - update session
        if _geo:
            flat_session['device.geo'] = _geo.model_dump()
            flat_session.set_updated()
            return flat_session

    return flat_session


def update_session_utm_with_client_data(tracker_payload: TrackerPayload, flat_session: FlatSession) -> FlatSession:
    if flat_session.get('utm.source', None) is None:
        _utm = _get_tracker_utm(tracker_payload)

        # If client-side utm is sent but not available in session - update session
        if _utm:
            flat_session['utm'] = _utm.model_dump()
            flat_session.set_updated()

    return flat_session


def _compute_utm(flat_session: FlatSession, tracker_payload_context: dict) -> FlatSession:
    if 'utm' in tracker_payload_context:
        try:
            flat_session['utm'] = UTM(**tracker_payload_context['utm']).model_dump()  # TODO tracker_payload_context['utm'] should be enough
            del tracker_payload_context['utm']
        except ValidationError:
            pass
    return flat_session


def _compute_screen_size(flat_session: FlatSession, tracker_payload: TrackerPayload) -> FlatSession:
    _value = tracker_payload.get_resolution()
    if _value:
        flat_session['device.resolution'] = _value

    _value = tracker_payload.get_color_depth()
    if _value:
        flat_session['device.color_depth'] = _value

    _value = tracker_payload.get_screen_orientation()
    if _value:
        flat_session['device.orientation'] = _value

    return flat_session


def _compute_languages(flat_session: FlatSession, tracker_payload) -> FlatSession:
    try:
        flat_session['app.language'] = flat_session['context.browser.local.browser.language']
    except Exception:
        pass

    spoken_languages, language_codes = get_spoken_languages(flat_session, tracker_payload.request)
    if spoken_languages:
        flat_session['context.language'] = list(set(spoken_languages))
    if language_codes:
        flat_session['context.language_codes'] = list(set(language_codes))

    return flat_session


def _compute_ip(flat_session: FlatSession, tracker_payload, tracker_config) -> FlatSession:
    _value = tracker_payload.get_ip()
    if _value:
        flat_session['device.ip'] = _value

    flat_session['context.ip'] = tracker_config.ip

    return flat_session


def _compute_bot(session, tracker_payload):
    try:
        header_from = tracker_payload.request['headers']['from']
        if header_from == "googlebot(at)googlebot.com":
            session.app.bot = True
    except Exception:
        pass


async def compute_session(flat_session: Optional[FlatSession],
                          tracker_payload: TrackerPayload,
                          tracker_config: TrackerConfig
                          ) -> FlatSession:
    if flat_session:

        # Is new session
        if flat_session.is_new():
            # Compute session. Session is filled only when new

            # Compute the User Agent data
            flat_session = _compute_data_from_user_agent(flat_session, tracker_payload)

            # Compute UTM
            flat_session = _compute_utm(flat_session, tracker_payload.context)

            # Compute Screen size
            flat_session = _compute_screen_size(flat_session, tracker_payload)

            # Compute session referer, channel and bot
            flat_session = _compute_session_referer(flat_session, tracker_payload)

            # Compute device ip
            flat_session = _compute_ip(flat_session, tracker_payload, tracker_config)

            # Compute languages
            flat_session = _compute_languages(flat_session, tracker_payload)

        # Update missing data
        flat_session = await update_device_geo(tracker_payload, flat_session)
        flat_session = update_session_utm_with_client_data(tracker_payload, flat_session)

        # If agent is a bot stop
        if (flat_session.get('app.bot', False) or _has_google_bot_header(tracker_payload.request)) and tracardi.disallow_bot_traffic:
            raise BlockedException(f"Traffic from bot is not allowed.")

    return flat_session
