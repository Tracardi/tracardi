from datetime import datetime
from typing import Optional, List, Tuple, Any
from pydantic import BaseModel
from tracardi.config import tracardi

from tracardi.domain.event import Event, RECEIVED

from ..entity import Entity
from ..event_metadata import EventPayloadMetadata
from ..payload.event_payload import EventPayload
from ..profile import Profile
from ..session import Session, SessionMetadata, SessionTime
from ..time import Time


class TrackerPayload(BaseModel):
    source: Entity
    session: Entity

    metadata: Optional[EventPayloadMetadata]
    profile: Optional[Entity] = None
    context: Optional[dict] = {}
    properties: Optional[dict] = {}
    events: List[EventPayload] = []
    options: Optional[dict] = {}

    def __init__(self, **data: Any):
        data['metadata'] = EventPayloadMetadata(
            time=Time(
                insert=datetime.utcnow()
            ))
        super().__init__(**data)

    def get_events(self, session: Optional[Session], profile: Optional[Profile], profile_less) -> List[Event]:
        event_list = []
        if self.events:
            for event in self.events:  # type: EventPayload
                _event = event.to_event(self.metadata, self.source, session, profile, event.options, profile_less)
                _event.metadata.status = RECEIVED
                event_list.append(_event)
        return event_list

    def return_profile(self):
        return self.options and "profile" in self.options and self.options['profile'] is True

    def is_on(self, key, default):
        if key not in self.options or not isinstance(self.options[key], bool):
            # default value
            return default

        return self.options[key]

    def is_debugging_on(self) -> bool:
        return tracardi.track_debug and self.is_on('debugger', default=False)

    async def get_profile_and_session(self, session: Session, load_merged_profile, profile_less) -> Tuple[
        Optional[Profile], Session]:

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

            is_new_session = True

            if profile_less is False:

                # Bind profile
                if self.profile is None:

                    # Create empty default profile generate profile_id
                    profile = Profile.new()

                    # Create new profile
                    is_new_profile = True

                else:

                    # Id exists load profile from storage
                    profile = await load_merged_profile(id=self.profile.id)  # type: Profile

                    if profile is None:
                        # Profile id delivered but profile does not exist in storage.
                        # Id was forged

                        profile = Profile.new()

                        # Create new profile
                        is_new_profile = True

        else:

            if profile_less is False:

                # There is session. Copy profile id form session to profile

                if session.profile is not None:
                    # Loaded session has profile

                    # Load profile based on profile id saved in session
                    profile = await load_merged_profile(id=session.profile.id)  # type: Profile

                    if isinstance(profile, Profile) and session.profile.id != profile.id:
                        # Profile in session id has been merged. Change profile in session.

                        session.profile.id = profile.id
                        session.metadata.time.timestamp = datetime.timestamp(datetime.utcnow())

                        is_new_session = True

                else:
                    # Corrupted session, or profile less session

                    profile = None

                if profile is None:
                    # Id exists but profile not exist in storage.

                    profile = Profile.new()

                    # Create new profile
                    is_new_profile = True

        session.context = self.context
        session.properties = self.properties
        session.operation.new = is_new_session

        if profile_less is False and profile is not None:
            profile.operation.new = is_new_profile

        return profile, session
