import json
import logging
from hashlib import sha1
from datetime import datetime
from typing import Union, Callable, Awaitable, Optional, List, Any, Tuple
from uuid import uuid4

from dotty_dict import dotty
from pydantic import PrivateAttr, BaseModel

from tracardi.exceptions.exception_service import get_traceback
from tracardi.service.utils.getters import get_entity_id

from tracardi.config import tracardi
from ...service.profile_merger import ProfileMerger
from ..console import Console
from ..event_metadata import EventPayloadMetadata
from ..event_source import EventSource
from ..identification_point import IdentificationPoint
from ..payload.event_payload import EventPayload
from ..session import Session, SessionMetadata, SessionTime
from ..time import Time
from ..entity import Entity
from ..profile import Profile
from ...exceptions.log_handler import log_handler


from tracardi.service.storage.driver.elastic import identification as identification_db


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
    _tracardi_referer: dict = PrivateAttr({})

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

    def __init__(self, **data: Any):
        data['metadata'] = EventPayloadMetadata(
            time=Time(
                insert=datetime.utcnow()
            ))
        super().__init__(**data)
        self._id = str(uuid4())
        self._tracardi_referer = self.get_tracardi_data_referer()
        if 'scheduledFlowId' in self.options and 'scheduledNodeId' in self.options:
            if isinstance(self.options['scheduledFlowId'], str) and isinstance(self.options['scheduledNodeId'], str):
                if len(self.events) > 1:
                    raise ValueError("Scheduled events may have only one event per tracker payload.")
                if self.source.id[0] != "@":
                    raise ValueError("Scheduled events must be send via internal scheduler event source.")
                self._scheduled_flow_id = self.options['scheduledFlowId']
                self._scheduled_node_id = self.options['scheduledNodeId']


    @property
    def tracardi_referer(self):
        return self._tracardi_referer

    @property
    def scheduled_event_config(self) -> ScheduledEventConfig:
        return ScheduledEventConfig(flow_id=self._scheduled_flow_id, node_id=self._scheduled_node_id)

    def _replace_profile(self, profile_id):
        self.profile = Entity(id=profile_id)
        self.profile_less = False
        self.options.update({"saveProfile": True})

    def _replace_session(self, session_id):
        self.session = Entity(id=session_id)
        self.profile_less = False
        self.options.update({"saveSession": True})

    def generate_profile_and_session_for_webhook(self, console_log: list) -> bool:

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

                            if 'replace_session_id' in self.source.config:
                                try:
                                    session_id_ref = self.source.config['replace_session_id'].strip()
                                    if bool(session_id_ref):
                                        # Webhooks have only one event, so it is save to get it from self.events[0]
                                        session_id = self.events[0].properties[session_id_ref]
                                        self._replace_session(session_id)
                                except KeyError as e:
                                    message = f"Could not generate set session for a webhook. " \
                                              f"Event stays session-less. " \
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
                                self._replace_session(str(uuid4()))

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

    def get_events_dict(self) -> List[dict]:
        # Todo Cache in property - this is expensive
        for event_payload in self.events:
            # Todo Performance
            yield event_payload.to_event_dict(
                self.source,
                self.session,
                self.profile,
                self.profile_less)
            # yield event_payload.to_event(self.metadata,
            #                              self.source,
            #                              self.session,
            #                              self.profile,
            #                              self.profile_less)
            # yield event_payload.to_event_data_class(self.metadata,
            #                                         self.source,
            #                                         self.session,
            #                                         self.profile,
            #                                         self.profile_less)

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
            if not self.profile or not self.profile.id:
                raise ValueError("Can not use static profile id without profile.id.")

            profile = await profile_loader(self, True)  # is_static is set to true

            # Create empty profile if the profile id does nto point to any profile in database.
            if not profile:
                profile = Profile(
                    id=self.profile.id
                )
                profile.operation.new = True

            # Create empty session if the session id does nto point to any session in database.
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

    def get_tracardi_data_referer(self) -> dict:

        try:
            return self.context['tracardi']['pass']
        except KeyError:
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

    async def list_identification_points(self):
        return list(await self.get_identification_points())

    def get_profile_attributes_via_identification_data(self, valid_identification_points) -> Optional[List[Tuple[str, str]]]:
        try:
            # Get first event type and match identification point for it
            _identification = valid_identification_points[0]
            properties = dotty(next(self.get_event_properties(_identification.event_type.id)))
            find_profile_by_fields = []
            for field in _identification.fields:
                if field.event_property.ref and field.profile_trait.ref:
                    if field.event_property.value not in properties:
                        raise AssertionError(f"While creating new profile Tracardi was forced to load data by merging "
                                             f"key because identification must be performed on new profile. "
                                             f"We encountered missing data issue for property "
                                             f"[{field.event_property.value}] in the event property. "
                                             f"Identification point [{_identification.name}] has it defined as customer "
                                             f"merging key but the event has only the properties {properties}.")
                        # error
                    find_profile_by_fields.append((field.profile_trait.value, properties[field.event_property.value]))
            if find_profile_by_fields:
                # load profile
                return find_profile_by_fields
            return None
        except AssertionError as e:
            logger.error(f"Can not find property to load profile by identification data: {str(e)}")
            return None

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

                    # First, check if the tracker_payload does not have events that need merging because
                    # the identification point is defined. In such case we need to try to load profile with
                    # data defined in identification point.

                    # Rafael Bug fixed

                    valid_identification_points = await self.list_identification_points()

                    # Has identification points?
                    if valid_identification_points:
                        # We have new profile and identification point.
                        profile_fields = self.get_profile_attributes_via_identification_data(valid_identification_points)

                        # We have fields that identify profile according to identification point

                        if profile_fields:

                            profile = await ProfileMerger.invoke_merge_profile(
                                Profile.new(),
                                merge_by=profile_fields,
                                limit=1000)

                        # todo remove after 2023-11
                        # profiles = await profile_driver.load_profiles_to_merge(merge_key_values=profile_fields)
                        print("profiles", profile)
                        print(profile_fields)

                    # If there is still no profile that means that it could not be loaded. It can happen if
                    # event properties did not have all necessary data or the is no profile with defined
                    # attributes.

                    # Then create new profile.

                    if profile is None:

                        # Create empty default profile generate profile_id
                        profile = Profile.new()

                        # Create new profile
                        is_new_profile = True

                        logger.info(
                            "New profile created at UTC {} with id {}".format(profile.metadata.time.insert, profile.id))

                    # if True:  # has identification point
                    #     self.profile = profile
                    #     # load profile by identification data

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

                    # Load profile on profile id saved in session
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

        if profile_less is False and profile is not None:
            profile.operation.new = is_new_profile

        return profile, session

    @staticmethod
    async def _load_identification_points():
        identification_points = await identification_db.load_enabled(limit=200)
        return identification_points.to_domain_objects(IdentificationPoint)

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
