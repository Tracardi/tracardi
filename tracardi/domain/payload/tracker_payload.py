from urllib.parse import urlparse, ParseResult

from user_agents.parsers import UserAgent

from tracardi.service.utils.date import now_in_utc

import time

import json
from hashlib import sha1
from typing import Union, Optional, List, Any, Tuple, Generator
from uuid import uuid4

from dotty_dict import dotty
from pydantic import PrivateAttr, BaseModel
from user_agents import parse

from tracardi.config import tracardi
from .. import ExtraInfo
from ..request import Request
from ...exceptions.log_handler import get_logger
from ...service.decorators.function_memory_cache import async_cache_for
from ...service.license import License, LICENSE
from ..event_metadata import EventPayloadMetadata
from ..event_source import EventSource
from ..identification_point import IdentificationPoint
from ..payload.event_payload import EventPayload
from ..session import Session
from ..time import Time
from ..entity import Entity, PrimaryEntity, DefaultEntity
from ..profile import Profile

from ...service.storage.mysql.mapping.identification_point_mapping import map_to_identification_point
from ...service.storage.mysql.service.idetification_point_service import IdentificationPointService
from tracardi.service.storage.elastic.interface.collector.load.profile import load_profile
from ...service.utils.getters import get_entity_id
from ...service.utils.hasher import get_shadow_session_id

if License.has_service(LICENSE):
    from com_tracardi.bridge.bridges import javascript_bridge

logger = get_logger(__name__)


class ScheduledEventConfig:

    def __init__(self, flow_id: Optional[str], node_id: Optional[str]):
        self.node_id = node_id
        self.flow_id = flow_id

    def is_scheduled(self) -> bool:
        return self.node_id is not None and self.flow_id is not None

    def __repr__(self):
        return f"ScheduledEventConfig(node_id={self.node_id}, flow_id={self.flow_id})"


class TrackerPayload(BaseModel):
    _id: str = PrivateAttr(None)
    _make_static_profile_id: bool = PrivateAttr(False)
    _scheduled_flow_id: str = PrivateAttr(None)
    _scheduled_node_id: str = PrivateAttr(None)
    _tracardi_referer: dict = PrivateAttr({})
    _timestamp: float = PrivateAttr(None)
    _user_agent: Optional[UserAgent] = PrivateAttr(None)

    source: Union[EventSource, Entity]  # When read from a API then it is Entity then is replaced by EventSource
    session: Optional[Union[DefaultEntity, Entity]] = None

    metadata: Optional[EventPayloadMetadata] = None
    profile: Optional[PrimaryEntity] = None
    context: Optional[dict] = {}
    properties: Optional[dict] = {}
    request: Optional[dict] = {}
    events: List[EventPayload] = []
    options: Optional[dict] = {}
    profile_less: bool = False
    debug: Optional[bool] = False

    def __init__(self, **data: Any):

        if data.get('context', None) is None:
            data['context'] = {}

        data['metadata'] = EventPayloadMetadata(
            time=Time(
                insert=now_in_utc()
            ))
        super().__init__(**data)
        self._id = str(uuid4())
        self._tracardi_referer = self.get_tracardi_data_referer()
        self._timestamp = time.time()
        if 'scheduledFlowId' in self.options and 'scheduledNodeId' in self.options:
            if isinstance(self.options['scheduledFlowId'], str) and isinstance(self.options['scheduledNodeId'], str):
                if len(self.events) > 1:
                    raise ValueError(
                        f"Scheduled events may have only one event per tracker payload. Expected one event got {self.get_event_types()}")
                if self.source.id[0] != "@":
                    raise ValueError("Scheduled events must be send via internal scheduler event source.")
                self._scheduled_flow_id = self.options['scheduledFlowId']
                self._scheduled_node_id = self.options['scheduledNodeId']

        self._cached_events_as_dicts: Optional[List[dict]] = None
        self._set_user_agent()

    @property
    def tracardi_referer(self):
        return self._tracardi_referer

    @property
    def scheduled_event_config(self) -> ScheduledEventConfig:
        return ScheduledEventConfig(flow_id=self._scheduled_flow_id, node_id=self._scheduled_node_id)

    def _set_user_agent(self):
        if self._user_agent is None:
            try:
                user_agent = self.request['headers']['user-agent']
                self._user_agent = parse(user_agent)
            except Exception:
                pass

    def get_user_agent(self) -> Optional[UserAgent]:
        return self._user_agent

    def is_bot(self) -> bool:
        if Request(self.request).get_origin() == 'https://gtm-msr.appspot.com':
            return True
        _user_agent = self.get_user_agent()
        if _user_agent:
            return _user_agent.is_bot
        return False

    def get_origin_or_referer(self) -> Optional[ParseResult]:
        try:

            origin: str = self.request['headers'].get('origin', "")
            referer: str = self.request['headers'].get('referer', "")

            origin = origin.strip()
            referer = referer.strip()

            if not origin and not referer:
                return None

            available_sources = [item for item in [origin, referer] if item]

            if not available_sources:
                return None

            url = urlparse(available_sources[0])
            if not url.scheme or not url.netloc:
                return None
            return url

        except KeyError:
            return None

    def replace_profile(self, profile_id):
        if profile_id:
            self.profile = PrimaryEntity(id=profile_id)
            self.profile_less = False
            self.options.update({"saveProfile": True})

    def replace_session(self, session_id):
        if session_id:
            self.session = Entity(id=session_id)
            self.profile_less = False
            self.options.update({"saveSession": True})

    def get_timestamp(self) -> float:
        return self._timestamp

    def has_type(self, event_type):
        for event_payload in self.events:
            if event_payload.type == event_type:
                return True
        return False

    def get_event_types(self) -> List[str]:
        return [event_payload.type for event_payload in self.events]

    def get_event_payloads_by_type(self, event_type) -> Generator[EventPayload, Any, None]:
        for event_payload in self.events:
            if event_payload.type == event_type:
                yield event_payload

    def force_static_profile_id(self, flag=True):
        self._make_static_profile_id = flag

    def has_static_profile_id(self) -> bool:
        return self._make_static_profile_id

    def set_headers(self, headers: dict):
        if 'authorization' in headers:
            del headers['authorization']
        if 'cookie' in headers:
            del headers['cookie']
        self.request['headers'] = headers

    def get_id(self) -> str:
        return self._id

    def get_finger_print(self) -> str:
        jdump = json.dumps(self.model_dump(exclude={'events': ..., 'metadata': ...}), sort_keys=True, default=str)
        props_hash = sha1(jdump.encode())
        return props_hash.hexdigest()

    def has_events(self):
        return len(self.events) > 0

    def has_event_type(self, event_type: str):
        return len([event.type for event in self.events if event.type == event_type]) > 0

    def has_profile(self) -> bool:
        return isinstance(self.profile, Entity)

    def set_ephemeral(self, flag=True):
        self.options.update({
            "saveSession": not flag,
            "saveEvents": not flag
        })

    def get_browser_agent_from_header(self) -> Optional[str]:
        try:
            return self.request['headers']['user-agent']
        except KeyError:
            return None

    def get_browser_agent(self) -> Optional[str]:
        try:
            return self.context['browser']['local']['browser']['userAgent']
        except KeyError:
            return self.get_browser_agent_from_header()

    def get_browser_language(self) -> Optional[str]:
        try:
            return self.context['browser']['local']['browser']['language']
        except KeyError:
            return None

    def add_context_to_events(self, context: dict):
        if isinstance(context, dict) and context:
            for event in self.events:
                event.context.update(context)

    def get_ip(self) -> Optional[str]:
        return Request(self.request).get_ip()

    def get_resolution(self) -> Optional[str]:
        try:
            return f"{self.context['screen']['local']['width']}x{self.context['screen']['local']['height']}"
        except KeyError:
            pass

    def get_color_depth(self) -> Optional[int]:
        try:
            return int(self.context['screen']['local']['colorDepth'])
        except KeyError:
            return None

    def get_screen_orientation(self) -> Optional[str]:
        try:
            return self.context['screen']['local']['orientation']
        except KeyError:
            return None

    def force_session(self, session):
        if self.session is None or self.session.id is None:
            self.session = session

    def is_on(self, key, default):
        if key not in self.options or not isinstance(self.options[key], bool):
            # default value
            return default

        return self.options[key]

    def is_debugging_on(self) -> bool:
        return tracardi.track_debug and self.is_on('debugger', default=False)

    def _fill_session_metadata(self, session: Session) -> Session:
        if self.session and isinstance(self.session, DefaultEntity) and self.session.metadata:
            if self.session.metadata.insert:
                session.metadata.time.insert = self.session.metadata.insert
            if self.session.metadata.update:
                session.metadata.time.update = self.session.metadata.update
            if self.session.metadata.create:
                session.metadata.time.create = self.session.metadata.create
        return session

    def create_default_session(self) -> Session:

        if not self.session:
            self.session = DefaultEntity(id=str(uuid4()))

        if not self.session.id:
            self.session.id = str(uuid4())

        session = Session.new(id=self.session.id)

        self._fill_session_metadata(session)

        return session

    def _fill_profile_metadata(self, profile):
        # Copy metadata to new profile
        if self.profile and self.profile.metadata:
            if self.profile.metadata.insert:
                profile.metadata.time.insert = self.profile.metadata.insert
            if self.profile.metadata.update:
                profile.metadata.time.update = self.profile.metadata.update
            if self.profile.metadata.create:
                profile.metadata.time.create = self.profile.metadata.create

    def create_default_profile(self, static: bool) -> Profile:

        if static:
            profile_id = self.profile.id
        else:
            profile_id = str(uuid4())

        profile = Profile.new(id=profile_id)

        # Copy metadata to new profile
        self._fill_profile_metadata(profile)

        return profile

    def get_tracardi_data_referer(self) -> dict:

        try:
            # Referred ids are passed in context.tracardi.pass = {
            #    profile: profile,
            #    source: source
            # }
            return self.context['tracardi']['pass']
        except (KeyError, TypeError):
            return {}

    def get_referer_data(self, type: str) -> Optional[str]:
        if self._tracardi_referer:
            if type in self._tracardi_referer:
                return self._tracardi_referer[type].strip()
        return None

    def has_referred_profile(self) -> bool:
        refer_profile_id = self.get_referer_data('profile')
        if refer_profile_id is None:
            return False
        if self.profile is None:
            return True
        return self.profile.id != refer_profile_id.strip()

    def is_cde(self) -> bool:
        return self.get_referer_data('source') is not None and self.has_referred_profile()

    @async_cache_for(30, use_context=True)
    async def list_identification_points(self):
        return list(await self.get_identification_points())

    def get_profile_attributes_via_identification_data(self, valid_identification_points) -> Optional[
        List[Tuple[str, str]]]:
        try:
            # Get first event type and match identification point for it
            _identification = valid_identification_points[0]
            event_payload = next(self.get_event_payloads_by_type(_identification.event_type.id))
            flat_properties = dotty({"properties": event_payload.properties})
            find_profile_by_fields = []
            for field in _identification.fields:
                if field.event_property.ref and field.profile_trait.ref:
                    if field.event_property.value not in flat_properties:
                        raise AssertionError(f"While creating new profile Tracardi was forced to load data by merging "
                                             f"key because identification must be performed on new profile. "
                                             f"We encountered missing data issue for event property "
                                             f"[{field.event_property.value}]. "
                                             f"Identification point [{_identification.name}] has it defined as customer "
                                             f"merging key but the event has only the properties {flat_properties}.")

                        # error
                    find_profile_by_fields.append(
                        (field.profile_trait.value, flat_properties[field.event_property.value]))
            if find_profile_by_fields:
                # load profile
                return find_profile_by_fields
            return None
        except AssertionError as e:
            logger.error(f"Can not find property to load profile by identification data: {str(e)}", e,
                         exc_info=True,
                         extra=ExtraInfo.build(origin="collector", object=self, error_number="T0001")
                         )
            return None

    def finger_printing_enabled(self):
        if License.has_service(LICENSE) and self.source.bridge.id == javascript_bridge.id:
            ttl = int(self.source.config.get('device_fingerprint_ttl', 30))
            return ttl > 0
        return False

    def create_session(self) -> Session:
        # Artificial session (Mutates tracker Payload)

        # If no session in tracker payload this means that we do not need session.
        # But we may need an artificial session for workflow handling. We create
        # one but will not save it.

        session = self.create_default_session()

        assert (session.operation.new is True)

        # Set profile from tracker payload to session
        if isinstance(self.profile, Entity) and self.profile.id:
            session.profile = Entity(id=self.profile.id)

        return session

    def has_tracker_payload_profile_id(self) -> bool:
        return self.profile is not None and isinstance(self.profile.id, str) and self.profile.id.strip() != ""

    @staticmethod
    def _has_profile_id_in_session(session) -> bool:
        return session and session.profile and isinstance(session.profile.id, str) and session.profile.id.strip() != ""

    @staticmethod
    def _profile_consistency_check(requested_profile_id, profile):
        if profile.id != requested_profile_id and requested_profile_id not in profile.ids:
            raise ValueError(f"Loading of profile failed. Some inconsistent profile loaded. "
                             f"Requested profile (ID: {requested_profile_id}), loaded profile (ID: {profile.id} "
                             f"with profile.ids={profile.ids}). "
                             f"Requested id could not be found in any ID collection.")

    def _resolve_conflicts(self, requested_profile_id, loaded_session_profile_id, profile, session):
        no_profiles_conflict = loaded_session_profile_id in profile.ids or loaded_session_profile_id == profile.id

        if not no_profiles_conflict:
            # The first attempt to resolve this issue was on the session loading level.
            # But we did not have profile loaded, so we are resolving it again.

            # Force new session ID. Create shadow session
            shadow_session_id = get_shadow_session_id(session.id)

            self.context.update({
                "session_conflict": {
                    "session_id": session.id,
                    "shadow_session_id": shadow_session_id,
                    "profile_in_payload": requested_profile_id,
                    "profile_id_in_loaded_session": loaded_session_profile_id
                }
            })

            # Create new session, to protect old session
            session = Session.new(id=shadow_session_id, profile_id=profile.id)
            self._fill_session_metadata(session)

            # Update tracker payload
            self.session.id = session.id

            logger.warning(f"Conflicting data in tracker payload. Session exists but belongs to profile "
                           f"profile (ID: {session.profile.id}) that has not the same ID as requested in payload profile "
                           f"(ID: {loaded_session_profile_id}). "
                           f"New session ID ({session.id}) created with attached existing in DB profile "
                           f"(ID {session.profile.id}).",
                           extra=ExtraInfo.build(origin='profile-loading', profile_id=profile.id)
                           )
        return session

    def _load_default_profile(self, session, static: bool) -> Tuple[Profile, Session]:

        # Create new profile
        profile = self.create_default_profile(static)

        assert profile.operation.new is True
        assert profile.operation.update is True

        if profile:
            if not isinstance(self.profile, PrimaryEntity):
                self.profile = PrimaryEntity(id=profile.id)
            else:
                self.profile.id = profile.id

        if not session.profile:
            session.profile = Entity(id=profile.id)
        else:
            session.profile.id = profile.id

        return profile, session

    async def _load_profile_by_session_profile_id(self, session: Session, static: bool) -> Tuple[Profile, Session]:

        # Check if the profile.id from session is not empty

        if not session.profile or not session.profile.id:
            return self._load_default_profile(session, static)

        requested_profile_id = session.profile.id

        # ID exists in session, load profile with session.profile.id
        profile: Optional[Profile] = await load_profile(requested_profile_id)

        if profile is not None:

            self._profile_consistency_check(requested_profile_id, profile)

            # Update client profile ids
            if self.profile:
                self.profile.id = profile.id
            else:
                self.profile = PrimaryEntity(id=profile.id)

            session.profile.id = profile.id  # Assign profile id it could be different then requested_profile_id (it could load form profile.ids)

            return profile, session

        # Profile id delivered but profile does not exist in storage.
        # ID was forged. Create new.

        return self._load_default_profile(session, static)

    async def _load_profile_by_payload_profile_id(self, session: Session, static: bool) -> Tuple[Profile, Session]:

        # We have valid profile definition
        requested_profile_id = get_entity_id(self.profile)
        loaded_session_profile_id = session.profile.id  # Session id delivered in payload

        # ID exists, load profile from storage
        profile: Optional[Profile] = await load_profile(requested_profile_id)

        if profile is not None:

            self._profile_consistency_check(requested_profile_id, profile)

            # Check if the loaded profile has not different ID.
            # It may happen if profile is loaded by IDS and the Profile ID is different

            # Update Tracker Profile ID
            self.profile.id = profile.id

            # Update Tracker Session Profile ID
            session.profile.id = profile.id

            # Check if there is a conflict in IDS.
            # Session ID exists but do not point to profile ID from tracker payload

            session = self._resolve_conflicts(requested_profile_id, loaded_session_profile_id, profile, session)

            return profile, session

        # Profile missing in db
        conflicting_profiles = session.profile.id != get_entity_id(self.profile)
        if conflicting_profiles:  # if there is different profile in session lets try to load this profile
            return await self._load_profile_by_session_profile_id(session, static)
        else:
            return self._load_default_profile(session, static)

    async def _get_profile(self, session, static: bool) -> Tuple[Profile, Session]:

        # Check consistency

        if static and not get_entity_id(self.profile):
            raise ValueError("Can not use static profile id without profile.id.")

        # Let's check what was sent

        if self.has_tracker_payload_profile_id():

            # Tracked Profile ID exists, start loading profile with tracker_payload.profile.id
            # And do the regular fallback

            profile, session = await self._load_profile_by_payload_profile_id(session, static)

        elif self._has_profile_id_in_session(session):

            # Fallback to loading from session with regular fallback

            profile, session = await self._load_profile_by_session_profile_id(session, static)

        else:

            profile, session = self._load_default_profile(session, static)

        return profile, session


    async def get_profile_and_session(
            self,
            session: Session,
            static: bool,
            profile_less
    ) -> Tuple[Optional[Profile], Session]:

        """
        Returns session. Creates profile if it does not exist.If it exists connects session with profile.
        """

        if session is None:  # loaded session is empty
            raise ValueError("Session must exist at this point")

        # Update session
        if isinstance(session.context, dict):
            session.context.update(self.context)
        else:
            session.context = self.context

        if isinstance(session.properties, dict):
            session.properties.update(self.properties)
        else:
            session.properties = self.properties

        if profile_less is True:
            return None, session

        # There is profile

        # Calling self._get_profile(session) revolves inconsistencies such as - missing ids.
        profile, session = await self._get_profile(session, static=static)

        # Check consistency

        if session and self.session:
            # Correct session ID are when they are the same or a shadowed session was created when there was a conflict.
            correct_session = self.session.id == session.id or session.id == get_shadow_session_id(session.id)
            if not correct_session:
                logger.warning(
                    f"Session ID ({self.session.id}) in Tracker Payload does not equal to "
                    f"loaded session ({session.id}) ")
        if profile and self.profile:
            if self.profile.id != profile.id:
                raise AssertionError(f"Profile ID ({self.profile.id}) in Tracker Payload does not equal "
                                     f"to loaded profile ({profile.id}) ")
            if session.profile.id != profile.id:
                raise AssertionError(
                    f"Profile ID in session ({session.profile.id}) does not equal to loaded profile ({profile.id}) ")

        return profile, session

    @staticmethod
    async def _load_identification_points():
        ips = IdentificationPointService()
        records = await ips.load_enabled(limit=200)
        return records.map_to_objects(map_to_identification_point)

    def _get_valid_identification_points(self,
                                         identification_points: List[IdentificationPoint]):
        for identification_point in identification_points:
            if identification_point.source.id != "" and identification_point.source.id != self.source.id:
                continue

            if not self.has_type(identification_point.event_type.id):
                continue

            yield identification_point

    async def get_identification_points(self):
        return self._get_valid_identification_points(await self._load_identification_points())
