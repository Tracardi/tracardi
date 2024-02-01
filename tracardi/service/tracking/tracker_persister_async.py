import asyncio

import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from tracardi.service.tracking.storage.event_storage import save_events
from tracardi.service.tracking.storage.profile_storage import save_profile
from tracardi.service.tracking.storage.session_storage import save_session
from tracardi.config import tracardi
from tracardi.domain.entity import Entity
from tracardi.domain.value_object.save_result import SaveResult
from tracardi.service.cache_manager import CacheManager

from tracardi.exceptions.log_handler import get_logger

from tracardi.domain.event import Event
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.exceptions.exception import StorageException, FieldTypeConflictException
from tracardi.service.field_mappings_cache import FieldMapper

logger = get_logger(__name__)
cache = CacheManager()


def clear_relations(tracker_payload, profile: Profile, session: Session, events: List[Event]) -> Tuple[Profile, Session, List[Event]]:

    _save_session_flag = tracker_payload.is_on('saveSession', default=True)
    _save_events_flag = tracker_payload.is_on('saveEvents', default=True)
    _save_profile_flag = tracker_payload.is_on('saveProfile', default=True)

    if not _save_events_flag:
        events = []

    if not _save_session_flag:
        session = None
        for event in events:
            event.session = None

    if not _save_profile_flag:
        profile = None
        for event in events:
            event.profile = None

    return profile, session, events


def _get_savable_session(session: Optional[Session], profile: Profile) -> Optional[Session]:
    if isinstance(session, Session):
        if session.has_not_saved_changes():
            # Session to add. Add new profile id to session if it does not exist,
            # or profile id in session is different from the real profile id.
            if session.profile is None or (
                    isinstance(session.profile, Entity)
                    and isinstance(profile, Entity)
                    and session.profile.id != profile.id):
                # save only profile Entity
                if profile is not None:
                    session.profile = Entity(id=profile.id)

        # This is a hack. Storage has dynamic content and sometimes can not be stored.
        # Saves it as json and removes storage

        if 'storage' in session.context:
            session.context['local_storage'] = json.dumps(session.context['storage'])
            del (session.context['storage'])

        if not isinstance(session.context, dict):
            session.context = {}

        return session

    return None


async def _save_profiles(self, profiles: List[Profile], _save_profile_to_db: bool):
    if _save_profile_to_db:

        _profiles_to_save = []

        for profile in profiles:

            if profile:
                _profiles_to_save.append(profile)

        results = []
        try:
            result = await save_profile(_profiles_to_save)
            if result.has_errors():
                for id in result.ids:
                    self.profile_errors[id] = f"Error while storing profile id: {id}. Details: {result.errors}"
            results.append(result)

        except StorageException as e:
            message = "Could not save profile. Error: {}".format(str(e))
            raise FieldTypeConflictException(message, rows=e.details)

        return results
    return None


class TrackingPersisterAsync:

    def __init__(self):
        self.profile_errors: Dict[str, str] = {}  # Keeps errors from profiles
        self.session_errors: Dict[str, str] = {}  # Keeps errors from session

    async def _save_profile(self, profile: Profile):
        if profile:
            if profile.has_not_saved_changes():

                results = []
                try:
                    result = await save_profile(profile)
                    if result.has_errors():
                        for id in result.ids:
                            self.profile_errors[id] = f"Error while storing profile id: {id}. Details: {result.errors}"
                    results.append(result)
                except StorageException as e:
                    message = "Could not save profile. Error: {}".format(str(e))
                    raise FieldTypeConflictException(message, rows=e.details)

                return results
        return None

    async def _save_session(self, session: Session, profile: Profile):
        try:
            if session:
                session = _get_savable_session(session, profile)

                if session and session.has_not_saved_changes():

                    result = await save_session(session)

                    if result.has_errors():
                        for id in result.ids:
                            self.session_errors[id] = f"Error while storing session id: {id}. Details: {result.errors}"

                    return result

            return None

        except StorageException as e:
            raise FieldTypeConflictException("Could not save session. Error: {}".format(str(e)), rows=e.details)

    @staticmethod
    async def __standard_event_save(events):
        # Skip events that should not be saved
        events = [event for event in events if event.is_persistent()]

        event_result = await save_events(events)
        event_result = SaveResult(**event_result.model_dump())

        # Add event types
        for event in events:
            event_result.types.append(event.type)

        return event_result

    async def _modify_events(self, events: List[Event]) -> List[Event]:

        for event in events:

            event.metadata.time.total_time = datetime.timestamp(datetime.utcnow()) - datetime.timestamp(
                event.metadata.time.insert)

            if self.profile_errors:
                event.metadata.error = True

            if self.session_errors:
                event.metadata.error = True

        return events

    async def _save_events(self, events: List[Event]):
        try:
            if events:
                # Set statuses
                events = await self._modify_events(events)

                return await self.__standard_event_save(events)

        except StorageException as e:
            raise FieldTypeConflictException("Could not save event. Error: {}".format(str(e)), rows=e.details)

        return None

    async def save_events(self, events: List[Event]):
        if tracardi.expose_gui_api is True:
            if events:
                FieldMapper().add_field_mappings('event', events)
        return await self._save_events(events)

    async def save_profile_and_session(self,
                                       session: Session,
                                       profile: Profile,
                                       ) -> tuple:

        # Add mappings
        if tracardi.expose_gui_api is True:
            if profile:
                FieldMapper().add_field_mappings('profile', [profile])

            if session:
                FieldMapper().add_field_mappings('session', [session])

        coroutines = [
            self._save_profile(profile),
            self._save_session(session, profile)
        ]

        return await asyncio.gather(*coroutines)

