import asyncio
import logging
import os
from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Type
from uuid import uuid4

from pydantic import ValidationError

from tracardi.config import tracardi, memory_cache
from tracardi.domain.entity import Entity
from tracardi.domain.event_source import EventSource
from tracardi.domain.marketing import UTM
from tracardi.domain.payload.event_payload import EventPayload
from tracardi.domain.value_object.operation import Operation
from tracardi.process_engine.debugger import Debugger
from tracardi.service.cache_manager import CacheManager
from tracardi.service.console_log import ConsoleLog
from tracardi.exceptions.log_handler import log_handler
from tracardi.domain.console import Console
from tracardi.exceptions.exception_service import get_traceback
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session, SessionMetadata, SessionTime
from tracardi.exceptions.exception import DuplicatedRecordException
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.service.consistency.session_corrector import correct_session
from tracardi.service.destination_orchestrator import DestinationOrchestrator
from tracardi.service.storage.driver.elastic import debug_info as debug_info_db
from tracardi.service.storage.loaders import get_profile_loader
from tracardi.service.synchronizer import profile_synchronizer
from tracardi.service.tracker_config import TrackerConfig
from tracardi.service.tracking_manager import TrackingManager, TrackerResult, TrackingManagerBase
from tracardi.service.utils.getters import get_entity_id
from user_agents import parse

from .maxmind_geo import get_geo_location
from .utils.domains import free_email_domains
from .utils.languages import language_codes_dict, language_countries_dict
from .utils.parser import parse_accept_language
from ..domain.geo import Geo
from ..domain.time import Time
from ..process_engine.action.v1.connectors.maxmind.geoip.model.maxmind_geolite2_client import MaxMindGeoLite2Client, \
    GeoLiteCredentials

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)
cache = CacheManager()


class TrackingOrchestrator:

    def __init__(self,
                 source: EventSource,
                 tracker_config: TrackerConfig,
                 on_profile_merge: Callable[[Profile], Profile] = None,
                 on_profile_ready: Type[TrackingManagerBase] = None
                 ):

        self.on_profile_ready: Type[TrackingManagerBase] = on_profile_ready
        self.on_profile_merge = on_profile_merge
        self.tracker_config = tracker_config
        self.source = source
        self.console_log = None
        self.locked = []

    async def invoke(self, tracker_payload: TrackerPayload, console_log: ConsoleLog) -> TrackerResult:

        """
        Controls the synchronization of profiles and invokes the process.
        """

        self.console_log = console_log
        return await self._invoke_track_process(tracker_payload)

    async def _invoke_track_process(self, tracker_payload: TrackerPayload) -> TrackerResult:

        # Is source ephemeral
        if self.source.transitional is True:
            tracker_payload.set_ephemeral()

        # Load session from storage
        try:
            if tracker_payload.session is None:
                # If no session in tracker payload this means that we do not need session.
                # But we may need an artificial session for workflow handling. We create
                # one but will not save it.

                session = Session(id=str(uuid4()), metadata=SessionMetadata())
                tracker_payload.force_session(session)
                tracker_payload.options.update({
                    "saveSession": False
                })

            # Loads session from ES if necessary

            # TODO Possible error

            session = await cache.session(
                session_id=tracker_payload.session.id,
                ttl=memory_cache.session_cache_ttl
            )

            # Session can be none if not found in db. User defined a session this means he wanted it.
            # At this point it is null. We handle it later.

        except DuplicatedRecordException as e:

            # There may be a case when we have 2 sessions with the same id.
            logger.error(str(e))

            # Try to recover sessions
            list_of_profile_ids_referenced_by_session = await correct_session(tracker_payload.session.id)

            # If there is duplicated session create new random session.
            # As a consequence of this a new profile is created.
            session = Session(
                id=tracker_payload.session.id,
                metadata=SessionMetadata(
                    time=SessionTime(
                        insert=datetime.utcnow()
                    )
                ),
                operation=Operation(
                    new=True
                )
            )

            # If duplicated sessions referenced the same profile then keep it.
            if len(list_of_profile_ids_referenced_by_session) == 1:
                session.profile = Entity(id=list_of_profile_ids_referenced_by_session[0])

        # Load profile
        profile_loader = get_profile_loader()

        # Force static profile id

        if self.tracker_config.static_profile_id is True or tracker_payload.has_static_profile_id():
            # Get static profile - This is dangerous
            profile, session = await tracker_payload.get_static_profile_and_session(
                session,
                profile_loader,
                tracker_payload.profile_less
            )

            # Profile exists but was merged
            if profile is not None and profile.is_merged(tracker_payload.profile.id):
                _forced_events = [ev.type for ev in tracker_payload.events]
                err_msg = f"Profile ID {tracker_payload.profile.id} was merged with {profile.id}, " \
                          f"but the old ID {tracker_payload.profile.id} was forced to be used. " \
                          f" As a result, events of type {_forced_events} will continue to be saved using the old " \
                          "profile ID. This is acceptable for the 'visit-ended' event type since it ensures the " \
                          "closure of the previous profile visit. However, for other event types, it may suggest " \
                          "that the client failed to switch or update the profile ID appropriately."
                if 'visit-ended' in _forced_events:
                    logger.info(err_msg)
                else:
                    logger.warning(err_msg)
                profile.id = tracker_payload.profile.id
        else:
            profile, session = await tracker_payload.get_profile_and_session(
                session,
                profile_loader,
                tracker_payload.profile_less
            )

        if isinstance(tracker_payload.source, EventSource):
            session.metadata.channel = tracker_payload.source.channel

        # Append context data

        if tracardi.system_events:

            if profile and profile.operation.new:
                # Add session created
                tracker_payload.events.append(
                    EventPayload(
                        type='profile-created',
                        time=Time(insert=datetime.utcnow() - timedelta(seconds=3)),
                        properties={},
                        options={"source_id": tracardi.internal_source}
                    )
                )

            if session.is_reopened():
                tracker_payload.events.append(
                    EventPayload(
                        type='visit-started',
                        time=Time(insert=datetime.utcnow() - timedelta(seconds=1)),
                        properties={},
                        options={"source_id": tracardi.internal_source}
                    )
                )

            if session.is_new():
                # Add session created event to the registered events
                tracker_payload.events.append(
                    EventPayload(
                        type='session-opened',
                        time=Time(insert=datetime.utcnow() - timedelta(seconds=2)),
                        properties={},
                        options={"source_id": tracardi.internal_source}
                    )
                )

        # Is new session
        if session.is_new():

            # Compute the User Agent data
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

                # Get Language from request and geo

                spoken_languages = []
                language_codes = []
                if 'headers' in tracker_payload.request and 'accept-language' in tracker_payload.request['headers']:
                    languages = parse_accept_language(tracker_payload.request['headers']['accept-language'])
                    if languages:
                        spoken_lang_codes = [language for (language, _) in languages if len(language) == 2]
                        for lang_code in spoken_lang_codes:
                            if lang_code in language_codes_dict:
                                spoken_languages += language_codes_dict[lang_code]
                                language_codes.append(lang_code)

                if session.device.geo.country.code:
                    lang_code = session.device.geo.country.code.lower()
                    if lang_code in language_codes_dict:
                        spoken_languages += language_codes_dict[lang_code]
                        language_codes.append(lang_code)

                if spoken_languages:
                    session.context['language'] = list(set(spoken_languages))
                    profile.data.pii.language.spoken = session.context['language']

                if 'geo' not in profile.aux:
                    profile.aux['geo'] = {}

                # Continent

                if 'time' in tracker_payload.context:
                    tz = tracker_payload.context['time'].get('tz', 'utc')

                    if tz.lower() != 'utc':
                        continent = tz.split('/')[0]
                    else:
                        continent = 'n/a'

                    profile.aux['geo']['continent'] = continent

                # Aux markets

                markets = []
                for lang_code in language_codes:
                    if lang_code in language_countries_dict:
                        markets += language_countries_dict[lang_code]

                if markets:
                    profile.aux['geo']['markets'] = markets

                # Screen

                try:
                    session.device.resolution = f"{tracker_payload.context['screen']['local']['width']}x{tracker_payload.context['screen']['local']['height']}"
                except KeyError:
                    pass

                try:
                    session.device.color_depth = int(tracker_payload.context['screen']['local']['colorDepth'])
                except KeyError:
                    pass

                try:
                    session.device.orientation = tracker_payload.context['screen']['local']['orientation']
                except KeyError:
                    pass

                session.app.bot = user_agent.is_bot
                session.app.name = user_agent.browser.family  # returns 'Mobile Safari'
                session.app.version = user_agent.browser.version_string
                session.app.type = "browser"

                if 'utm' in tracker_payload.context:
                    try:
                        session.utm = UTM(**tracker_payload.context['utm'])
                        del tracker_payload.context['utm']
                    except ValidationError:
                        pass

                # session.app.resolution = session.context['screen']

            except Exception as e:
                pass

            try:
                session.device.ip = tracker_payload.request['headers']['x-forwarded-for']
            except Exception:
                pass

            try:
                session.app.language = session.context['browser']['local']['browser']['language']
            except Exception:
                pass

        # Try to get location from tracker context.

        if 'location' in tracker_payload.context and \
                (session.device.geo.is_empty() or profile.data.devices.last.geo.is_empty()):

            try:
                _geo = Geo(**tracker_payload.context['location'])

                del tracker_payload.context['location']

                # If location is sent but not available in session - update session

                if session.device.geo.is_empty():
                    session.device.geo = _geo
                    session.operation.update = True

                # Add last geo to profile
                if profile.data.devices.last.geo.is_empty() or _geo != profile.data.devices.last.geo:
                    profile.data.devices.last.geo = _geo
                    profile.operation.update = True

            except ValidationError as e:
                logger.error(str(e))

        # Still no geo location. That means there was no 'location' sent in tracker context or it failed parsing the
        # data. But we have device IP. If the profile geo is empty the we need to make another try.
        if session.device.ip and (session.device.geo.is_empty() or profile.data.devices.last.geo.is_empty()):

            # Check if max mind configured
            maxmind_license_key = os.environ.get('MAXMIND_LICENSE_KEY', None)
            maxmind_account_id = int(os.environ.get('MAXMIND_ACCOUNT_ID', 0))
            if maxmind_license_key and maxmind_account_id > 0:

                # The code checks if the profile's geo location has been assigned. If it hasn't been assigned yet,
                # it means that the profile does not have a geo location, which could be because the session is not
                # new. In this case, regardless of whether the session is new or not, the code checks if the profile's
                # geo location is empty. If it is empty, the code proceeds to fetch the geo location and assigns
                # it to the profile.
                _geo = await get_geo_location(GeoLiteCredentials(
                        license=maxmind_license_key,
                        accountId=maxmind_account_id), ip=session.device.ip)

                if _geo:

                    if profile.data.devices.last.geo.is_empty():
                        profile.data.devices.last.geo = _geo
                        profile.operation.update = True

                    if session.device.geo.is_empty():
                        session.device.geo = _geo
                        session.operation.update = True

        # Add email type
        if profile.data.contact.email and ('email' not in profile.aux or 'free' not in profile.aux['email']):
            email_parts = profile.data.contact.email.split('@')
            if len(email_parts) > 1:
                email_domain = email_parts[1]

                if 'email' not in profile.aux:
                    profile.aux['email'] = {}

                profile.aux['email']['free'] = email_domain in free_email_domains
                profile.operation.update = True

        # If UTM is sent but not available in session - update session
        if 'utm' in tracker_payload.context and session.utm.is_empty():
            try:
                session.utm = UTM(**tracker_payload.context['utm'])
                session.operation.update = True
                del tracker_payload.context['utm']
            except ValidationError:
                pass

        session.context['ip'] = self.tracker_config.ip

        # ------------------------------

        # Make profile copy
        has_profile = not tracker_payload.profile_less and isinstance(profile, Profile)
        profile_copy = profile.dict(exclude={"operation": ...}) if has_profile else None

        # Lock
        if has_profile and self.source.synchronize_profiles:
            key = f"profile:{profile.id}"
            await profile_synchronizer.wait_for_unlock(key, seq=tracker_payload.get_id())
            profile_synchronizer.lock_entity(key)
            self.locked.append(key)

        if self.on_profile_ready is None:
            tracking_manager = TrackingManager(
                self.console_log,
                tracker_payload,
                profile,
                session,
                self.on_profile_merge
            )

            tracker_result = await tracking_manager.invoke_track_process()
        else:
            if not issubclass(self.on_profile_ready, TrackingManagerBase):
                raise AssertionError("Callable self.on_profile_ready should be a subtype of TrackingManagerBase.")

            tracking_manager = self.on_profile_ready(
                self.console_log,
                tracker_payload,
                profile,
                session,
                self.on_profile_merge
            )

            tracker_result = await tracking_manager.invoke_track_process()

        # From now on do not use profile or session, use tracker_result.profile, tracker_result.session
        # For security we override old values
        profile = tracker_result.profile
        session = tracker_result.session

        # Dave debug data
        debug = tracker_payload.is_on('debugger', default=False)
        if tracardi.track_debug or debug:
            await self.save_debug_data(tracker_result.debugger, get_entity_id(tracker_result.profile))

        # Send to destination
        if not tracardi.disable_profile_destinations:
            do = DestinationOrchestrator(
                tracker_result.profile,
                tracker_result.session,
                tracker_result.events,
                self.console_log
            )
            await do.sync_destination(
                has_profile,
                profile_copy,
            )

        return tracker_result

    async def save_debug_data(self, debugger, profile_id):
        try:
            if isinstance(debugger, Debugger) and debugger.has_call_debug_trace():
                # Save debug info in background
                asyncio.create_task(debug_info_db.save_debug_info(debugger))
        except Exception as e:
            message = "Error during saving debug info: `{}`".format(str(e))
            logger.error(message)
            self.console_log.append(
                Console(
                    flow_id=None,
                    node_id=None,
                    event_id=None,
                    profile_id=profile_id,
                    origin='profile',
                    class_name='invoke_track_process_step_2',
                    module=__name__,
                    type='error',
                    message=message,
                    traceback=get_traceback(e)
                )
            )
