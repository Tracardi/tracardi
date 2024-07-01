from urllib.parse import urlparse, ParseResult

from user_agents.parsers import UserAgent

from tracardi.service.utils.date import now_in_utc

import time

import json
from hashlib import sha1
from datetime import datetime, timedelta
from typing import Union, Callable, Awaitable, Optional, List, Any, Tuple, Generator
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
from ...service.merging.facade_old import merge_profile_by_merging_keys
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

if License.has_service(LICENSE):
    from com_tracardi.bridge.bridges import javascript_bridge
    from com_tracardi.service.browser_fingerprinting import BrowserFingerPrint

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

    # def get_events_dict(self) -> List[dict]:
    #     if self._cached_events_as_dicts is None:
    #         self._cached_events_as_dicts = []
    #         for event_payload in self.events:
    #             self._cached_events_as_dicts.append(
    #                 event_payload.to_event_dict(
    #                     self.source,
    #                     self.session,
    #                     self.profile,
    #                     self.profile_less)
    #             )
    #     return self._cached_events_as_dicts
    #     # yield event_payload.to_event(self.metadata,
    #     #                              self.source,
    #     #                              self.session,
    #     #                              self.profile,
    #     #                              self.profile_less)
    #     # yield event_payload.to_event_data_class(self.metadata,
    #     #                                         self.source,
    #     #                                         self.session,
    #     #                                         self.profile,
    #     #                                         self.profile_less)

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

    def get_browser_agent(self) -> Optional[str]:
        try:
            return self.context['browser']['local']['browser']['userAgent']
        except KeyError:
            return None

    def get_browser_language(self) -> Optional[str]:
        try:
            return self.context['browser']['local']['browser']['language']
        except KeyError:
            return None

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
        # Get session
        if self.session is None or self.session.id is None:
            # Generate random
            self.session = session

    def is_on(self, key, default):
        if key not in self.options or not isinstance(self.options[key], bool):
            # default value
            return default

        return self.options[key]

    def is_debugging_on(self) -> bool:
        return tracardi.track_debug and self.is_on('debugger', default=False)

    def create_default_session(self) -> Session:

        if not self.session:
            self.session = DefaultEntity(id=str(uuid4()))

        if not self.session.id:
            self.session.id = str(uuid4())

        session = Session.new(id=self.session.id)

        if self.session and isinstance(self.session, DefaultEntity) and self.session.metadata:
            if self.session.metadata.insert:
                session.metadata.time.insert = self.session.metadata.insert
            if self.session.metadata.update:
                session.metadata.time.update = self.session.metadata.update
            if self.session.metadata.create:
                session.metadata.time.create = self.session.metadata.create

        return session

    def create_default_profile(self, id: Optional[str] = None) -> Profile:

        if id:
            profile_id = id
        elif self.profile and self.profile.id:
            profile_id = self.profile.id
        else:
            profile_id = str(uuid4())

        profile = Profile.new(id=profile_id)

        if self.profile and self.profile.metadata:
            if self.profile.metadata.insert:
                profile.metadata.time.insert = self.profile.metadata.insert
            if self.profile.metadata.update:
                profile.metadata.time.update = self.profile.metadata.update
            if self.profile.metadata.create:
                profile.metadata.time.create = self.profile.metadata.create

        return profile

    async def get_static_profile_and_session(
            self,
            session: Session,
            profile_loader: Callable[['TrackerPayload', bool], Awaitable],
            profile_less: bool
    ) -> Tuple[Optional[Profile], Session]:

        if profile_less:
            profile = None
        else:
            if not self.profile or not self.profile.id:
                raise ValueError("Can not use static profile id without profile.id.")

            profile = await profile_loader(
                self,
                True  # is_static is set to true
            )

            # Create empty profile if the profile id does nto point to any profile in database.
            if not profile:
                profile = self.create_default_profile()

            # Create empty session if the session id does nto point to any session in database.
            if session is None:
                session = self.create_default_session()

                if isinstance(session.context, dict):
                    session.context.update(self.context)
                else:
                    session.context = self.context

                if isinstance(session.properties, dict):
                    session.properties.update(self.properties)
                else:
                    session.properties = self.properties

            # Assign profile to session

            session.profile = Entity(id=profile.id)

        return profile, session

    def get_tracardi_data_referer(self) -> dict:

        try:
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

    async def get_profile_and_session(
            self,
            session: Optional[Session],
            profile_loader: Callable[['TrackerPayload', bool], Awaitable],
            profile_less
    ) -> Tuple[Optional[Profile], Session]:

        """
        Returns session. Creates profile if it does not exist.If it exists connects session with profile.
        """

        # Fingerprinting.

        fp_profile_id = None
        if self.finger_printing_enabled():
            ttl = 15 * 60
            device_finger_print = BrowserFingerPrint.get_browser_fingerprint(self)
            if self.source.config:
                ttl = int(self.source.config.get('device_fingerprint_ttl', 15 * 60))
            fp = BrowserFingerPrint(device_finger_print, timedelta(seconds=ttl))
            fp_profile_id = fp.get_profile_id_by_device_finger_print()

        is_new_profile = False
        profile = None

        if session is None:  # loaded session is empty

            is_new_session = True

            session = self.create_default_session()

            logger.debug("New session is to be created with id {}".format(session.id))

            if profile_less is False:

                # No profile in tracker payload
                if self.profile is None:

                    # First, check if the tracker_payload does not have events that need merging because
                    # the identification point is defined. In such case we need to try to load profile with
                    # data defined in identification point.

                    # Rafael Bug fixed

                    valid_identification_points = await self.list_identification_points()

                    # Has identification points?
                    if valid_identification_points:
                        # We have new profile and identification point.
                        profile_fields = self.get_profile_attributes_via_identification_data(
                            valid_identification_points)

                        # We have fields that identify profile according to identification point

                        if profile_fields:
                            profile = await merge_profile_by_merging_keys(
                                self.create_default_profile(),
                                merge_by=profile_fields)

                    # If there is still no profile that means that it could not be loaded. It can happen if
                    # event properties did not have all necessary data or the is no profile with defined
                    # attributes.

                    # Then create new profile.

                    if profile is None:
                        # Create empty default profile generate profile_id
                        profile = self.create_default_profile()

                        # Create new profile
                        is_new_profile = True

                        logger.info(
                            "New profile created at UTC {} with id {}".format(profile.metadata.time.insert, profile.id))

                else:

                    # ID exists, load profile from storage
                    profile: Optional[Profile] = await profile_loader(
                        self,
                        False  # Not static profile ID
                    )

                    if profile is None:
                        # Profile id delivered but profile does not exist in storage.
                        # ID was forged

                        profile = self.create_default_profile()

                        # Create new profile
                        is_new_profile = True

                        logger.debug(
                            "No merged profile. New profile created at UTC {} with id {}".format(
                                profile.metadata.time.insert,
                                profile.id))

                    else:
                        logger.info(
                            "Merged profile loaded with date {} UTC and id {}".format(profile.metadata.time.insert,
                                                                                      profile.id))

                # Now we have profile and we should assign it to session

                session.profile = Entity(id=profile.id)

        else:

            # Get flag from existing session
            is_new_session = session.operation.new if session.operation else True

            logger.debug("Session exists with id {}".format(session.id))

            if profile_less is False:

                # There is session. Copy profile id form session to profile

                if session.profile is not None:
                    # Loaded session has profile

                    # Load profile on profile id saved in session
                    copy_of_tracker_payload = TrackerPayload(**self.model_dump())
                    copy_of_tracker_payload.profile = Entity(id=session.profile.id)

                    # Loader can mutate the copy_of_tracker_payload and add merging status

                    profile: Optional[Profile] = await profile_loader(
                        copy_of_tracker_payload,  # Not static profile ID
                        False
                    )

                    # Reassign events that can be mutated
                    self.events = copy_of_tracker_payload.events

                    if isinstance(profile, Profile) and session.profile.id != profile.id:
                        # Profile in session id has been merged. Change profile in session.

                        session.profile.id = profile.id
                        session.metadata.time.timestamp = datetime.timestamp(
                            now_in_utc()
                        )

                        is_new_session = True

                else:
                    # Corrupted session, or profile less session

                    profile = None

                # Although we tried to load profile it still does not exist.
                if profile is None:
                    # ID exists but profile not exist in storage.

                    profile = self.create_default_profile()

                    # Create new profile
                    is_new_profile = True

                    # Update session as there is new profile. Previous session had no profile.id.
                    session.profile = Entity(id=profile.id)
                    is_new_session = True

        if isinstance(session.context, dict):
            session.context.update(self.context)
        else:
            session.context = self.context

        if isinstance(session.properties, dict):
            session.properties.update(self.properties)
        else:
            session.properties = self.properties

        session.set_new(is_new_session)

        if profile_less is False and profile is not None:
            profile.set_new(is_new_profile)

        if profile:
            # If there is fingerprinted profile and we just created new profile then load fingerprinted profile.
            if fp_profile_id:
                # If new profile then check if there is fingerprinted profile
                if is_new_profile:
                    if profile.id != fp_profile_id:

                        # Load profile with finger printed profile id
                        copy_of_tracker_payload = TrackerPayload(**self.model_dump())
                        copy_of_tracker_payload.profile = Entity(id=fp_profile_id)

                        # Loader can mutate the copy_of_tracker_payload and add merging status

                        fp_profile: Optional[Profile] = await profile_loader(
                            copy_of_tracker_payload,
                            False  # Not static profile ID
                        )

                        # Reassign events that can be mutated
                        self.events = copy_of_tracker_payload.events

                        if fp_profile:
                            profile = fp_profile
                        elif self.finger_printing_enabled():
                            fp.save_browser_finger_print(profile.id)

                        print("Loading profile by FP")
                else:
                    pass
                    # Todo merge with fingerprint as merge key. Do not know if I want to do this.

            elif self.finger_printing_enabled():
                # Does not have fingerprinted profile
                fp.save_browser_finger_print(profile.id)

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
