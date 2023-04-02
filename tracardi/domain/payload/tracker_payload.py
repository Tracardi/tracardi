import json
import logging
from hashlib import sha1
from datetime import datetime
from typing import Union, Callable, Awaitable, Optional, List, Any, Tuple
from uuid import uuid4
from pydantic import PrivateAttr, validator, BaseModel, ValidationError
from tracardi.exceptions.exception_service import get_traceback

from tracardi.service.utils.getters import get_entity_id

from tracardi.config import tracardi
from ..console import Console
from ..event import Event
from ..event_metadata import EventPayloadMetadata
from ..event_source import EventSource
from ..geo import Geo
from ..marketing import UTM
from ..payload.event_payload import EventPayload
from ..session import Session, SessionMetadata, SessionTime
from ..time import Time
from ..entity import Entity
from ..profile import Profile
from ...exceptions.log_handler import log_handler
from user_agents import parse

# from ...service.storage.drivers.elastic.profile import *

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


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

    source: Union[EventSource, Entity]  # When read from a API then it is Entity then is replaced by EventSource
    session: Optional[Entity] = None

    metadata: Optional[EventPayloadMetadata]
    profile: Optional[Entity] = None
    context: Optional[dict] = {}
    properties: Optional[dict] = {}
    request: Optional[dict] = {}
    events: List[EventPayload] = []
    options: Optional[dict] = {}
    profile_less: bool = False
    debug: Optional[bool] = False

    @validator("events")
    def events_must_not_be_empty(cls, value):
        if len(value) == 0:
            raise ValueError("Tracker payload must not have empty events.")
        return value

    def __init__(self, **data: Any):
        data['metadata'] = EventPayloadMetadata(
            time=Time(
                insert=datetime.utcnow()
            ))
        super().__init__(**data)
        self._id = str(uuid4())

        if 'scheduledFlowId' in self.options and 'scheduledNodeId' in self.options:
            if isinstance(self.options['scheduledFlowId'], str) and isinstance(self.options['scheduledNodeId'], str):
                if len(self.events) > 1:
                    raise ValueError("Scheduled events may have only one event per tracker payload.")
                if self.source.id[0] != "@":
                    raise ValueError("Scheduled events must be send via internal scheduler event source.")
                self._scheduled_flow_id = self.options['scheduledFlowId']
                self._scheduled_node_id = self.options['scheduledNodeId']

    @property
    def scheduled_event_config(self) -> ScheduledEventConfig:
        return ScheduledEventConfig(flow_id=self._scheduled_flow_id, node_id=self._scheduled_node_id)

    def _replace_profile(self, profile_id):
        self.profile = Entity(id=profile_id)
        self.profile_less = False
        self.options.update({"saveProfile": True})

    def generate_profile_and_session(self, console_log: list) -> bool:

        """

        Returns True if profile or session generated

        :param console_log:
        :return:

        """
        if isinstance(self.source, EventSource):

            if 'webhook' in self.source.type:
                if self.source.config is not None:
                    if 'generate_profile' in self.source.config:
                        if self.source.config['generate_profile'] is True:

                            if 'replace_profile_id' in self.source.config:
                                try:
                                    profile_id_ref = self.source.config['replace_profile_id'].strip()
                                    if bool(profile_id_ref):
                                        # Webhooks have only one event, so it is save to get it from self.events[0]
                                        profile_id = self.events[0].properties[profile_id_ref]
                                        self._replace_profile(profile_id)
                                except KeyError as e:
                                    message = f"Could not generate profile and session for a webhook. " \
                                              f"Event stays profile-less. " \
                                              f"Probable reason: Missing data: {str(e)}"
                                    logger.error(message)
                                    console_log.append(Console(
                                        flow_id=None,
                                        node_id=None,
                                        event_id=None,
                                        profile_id=get_entity_id(self.profile),
                                        origin='tracker',
                                        class_name=__name__,
                                        module=__name__,
                                        type='error',
                                        message=message,
                                        traceback=get_traceback(e)
                                    ))

                            if not self.profile:
                                self._replace_profile(str(uuid4()))

                            if not self.session:
                                self.session = Entity(id=str(uuid4()))
                                self.profile_less = False
                                self.options.update({"saveSession": True})

                            return True
        else:
            logger.error("Can't generate profile. Method _generate_profile_and_session used before "
                         "EventSource was created.")

        return False

    def has_type(self, event_type):
        for event_payload in self.events:
            if event_payload.type == event_type:
                return True
        return False

    def get_event_properties(self, event_type) -> List[dict]:
        for event in self.events:
            if event.type == event_type:
                yield event.properties

    def force_static_profile_id(self, flag=True):
        self._make_static_profile_id = flag

    def has_static_profile_id(self) -> bool:
        return self._make_static_profile_id

    def get_domain_events(self) -> List[Event]:
        for event_payload in self.events:
            yield event_payload.to_event(self.metadata,
                                         self.source,
                                         self.session,
                                         self.profile,
                                         self.profile_less)

    def set_headers(self, headers: dict):
        if 'authorization' in headers:
            del headers['authorization']
        if 'cookie' in headers:
            del headers['cookie']
        self.request['headers'] = headers

    def get_id(self) -> str:
        return self._id

    def get_finger_print(self) -> str:
        jdump = json.dumps(self.dict(exclude={'events': ..., 'metadata': ...}), sort_keys=True, default=str)
        props_hash = sha1(jdump.encode())
        return props_hash.hexdigest()

    def has_events(self):
        return len(self.events) > 0

    def set_ephemeral(self, flag=True):
        self.options.update({
            "saveSession": not flag,
            "saveEvents": not flag
        })

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

    async def get_static_profile_and_session(self,
                                             session: Session,
                                             profile_loader: Callable[['TrackerPayload', bool], Awaitable],
                                             profile_less: bool) -> Tuple[Optional[Profile], Session]:

        if profile_less:
            profile = None
        else:
            if not self.profile.id:
                raise ValueError("Can not use static profile id without profile.id.")

            profile = await profile_loader(self, True)  # is_static is set to true
            if not profile:
                profile = Profile(
                    id=self.profile.id
                )
                profile.operation.new = True

            if session is None:
                session = Session(
                    id=self.session.id,
                    metadata=SessionMetadata(
                        time=SessionTime(
                            insert=datetime.utcnow()
                        )
                    )
                )
                session.operation.new = True

                if isinstance(session.context, dict):
                    session.context.update(self.context)
                else:
                    session.context = self.context

                if isinstance(session.properties, dict):
                    session.properties.update(self.properties)
                else:
                    session.properties = self.properties

                # # Remove the session from cache we just created one.
                # # We repeat it when saving.
                # cache.session_cache().delete(self.session.id)

        return profile, session

    async def get_profile_and_session(self, session: Session,
                                      profile_loader: Callable[['TrackerPayload'], Awaitable],
                                      profile_less) -> Tuple[Optional[Profile], Session]:

        """
        Returns session. Creates profile if it does not exist.If it exists connects session with profile.
        """

        is_new_profile = False
        is_new_session = False
        profile = None

        if session is None:  # loaded session is empty

            session = Session(
                id=self.session.id,
                metadata=SessionMetadata(
                    time=SessionTime(
                        insert=datetime.utcnow()
                    )
                )
            )

            logger.debug("New session is to be created with id {}".format(session.id))

            is_new_session = True

            if profile_less is False:

                # Bind profile
                if self.profile is None:

                    # Create empty default profile generate profile_id
                    profile = Profile.new()

                    # Create new profile
                    is_new_profile = True

                    logger.info(
                        "New profile created at UTC {} with id {}".format(profile.metadata.time.insert, profile.id))

                else:

                    # ID exists, load profile from storage
                    profile: Optional[Profile] = await profile_loader(self)

                    if profile is None:
                        # Profile id delivered but profile does not exist in storage.
                        # ID was forged

                        profile = Profile.new()

                        # Create new profile
                        is_new_profile = True

                        logger.info(
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

            logger.info("Session exists with id {}".format(session.id))

            if profile_less is False:

                # There is session. Copy profile id form session to profile

                if session.profile is not None:
                    # Loaded session has profile

                    # Load profile based on profile id saved in session
                    copy_of_tracker_payload = TrackerPayload(**self.dict())
                    copy_of_tracker_payload.profile = Entity(id=session.profile.id)

                    profile: Optional[Profile] = await profile_loader(copy_of_tracker_payload)

                    if isinstance(profile, Profile) and session.profile.id != profile.id:
                        # Profile in session id has been merged. Change profile in session.

                        session.profile.id = profile.id
                        session.metadata.time.timestamp = datetime.timestamp(datetime.utcnow())

                        is_new_session = True

                else:
                    # Corrupted session, or profile less session

                    profile = None

                # Although we tried to load profile it still does not exist.
                if profile is None:
                    # ID exists but profile not exist in storage.

                    profile = Profile.new()

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

        session.operation.new = is_new_session

        if session.operation.new:

            # Add session created
            self.events.append(
                EventPayload(type='session-opened', properties={})
            )

            # Compute the User Agent data
            try:
                ua_string = session.context['browser']['local']['browser']['userAgent']
                user_agent = parse(ua_string)

                session.os.version = user_agent.os.version_string
                session.os.name = user_agent.os.family

                session.device.touch = user_agent.is_touch_capable
                session.device.name = user_agent.device.family
                session.device.brand = user_agent.device.brand
                session.device.model = user_agent.device.model

                if 'location' in self.context:
                    try:
                        session.device.geo = Geo(**self.context['location'])
                        del self.context['location']
                    except ValidationError:
                        pass

                session.device.type = 'mobile' if user_agent.is_mobile else \
                    'pc' if user_agent.is_pc else \
                        'tablet' if user_agent.is_tablet else \
                            'email' if user_agent.is_email_client else None

                try:
                    session.device.resolution = f"{self.context['screen']['local']['width']}x{self.context['screen']['local']['height']}"
                except KeyError:
                    pass

                try:
                    session.device.color_depth = int(self.context['screen']['local']['colorDepth'])
                except KeyError:
                    pass

                try:
                    session.device.orientation = self.context['screen']['local']['orientation']
                except KeyError:
                    pass

                session.app.bot = user_agent.is_bot
                session.app.name = user_agent.browser.family  # returns 'Mobile Safari'
                session.app.version = user_agent.browser.version_string
                session.app.type = "browser"

                if 'utm' in self.context:
                    try:
                        session.utm = UTM(**self.context['utm'])
                        del self.context['utm']
                    except ValidationError:
                        pass

                # session.app.resolution = session.context['screen']
            except Exception as e:
                pass

            try:
                session.device.ip = self.request['headers']['x-forwarded-for']
            except Exception:
                pass

            try:
                session.app.language = session.context['browser']['local']['browser']['language']
            except Exception:
                pass

        # Updates on EXISTING Session

        # If location is sent but not available in session - update session
        if 'location' in self.context and session.device.geo.is_empty():
            try:
                session.device.geo = Geo(**self.context['location'])
                session.operation.update = True
                del self.context['location']
            except ValidationError:
                pass

        # If UTM is sent but not available in session - update session
        if 'utm' in self.context and session.utm.is_empty():
            try:
                session.utm = UTM(**self.context['utm'])
                session.operation.update = True
                del self.context['utm']
            except ValidationError:
                pass

        if profile_less is False and profile is not None:
            profile.operation.new = is_new_profile

        if profile.operation.new:
            # Add session created
            self.events.append(
                EventPayload(type='profile-created', properties={})
            )

        return profile, session
