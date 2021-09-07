from datetime import datetime
from typing import Optional, List, Tuple, Any
from pydantic import BaseModel
from tracardi.domain.event import Event

from ..entity import Entity
from ..payload.event_payload import EventPayload
from ..profile import Profile
from ..session import Session
from ..metadata import Metadata
from ..time import Time


class TrackerPayload(BaseModel):
    source: Entity
    session: Entity

    metadata: Optional[Metadata]
    profile: Optional[Entity] = None
    context: Optional[dict] = {}
    properties: Optional[dict] = {}
    events: List[EventPayload] = []
    options: Optional[dict] = {}

    def __init__(self, **data: Any):
        data['metadata'] = Metadata(
            time=Time(
                insert=datetime.utcnow()
            ))
        super().__init__(**data)

    def get_events(self, session: Session, profile: Profile) -> List[Event]:
        _events = []
        if self.events:
            for event in self.events:  # type: EventPayload
                _event = event.to_event(self.metadata, self.source, session, profile, self.options)
                _events.append(_event)
        return _events

    def return_profile(self):
        return self.options and "profile" in self.options and self.options['profile'] is True

    def is_disabled(self, key):
        return key in self.options and self.options[key] is False

    # async def save_collected_data(self, profile: Profile, session: Session, events: list) -> Tuple[Profile, Session, list, CollectResult]:
    #
    #     # Get profile, session objects
    #     # profile, session = await self.get_profile_and_session()
    #     # events = self.get_events(session, profile)
    #
    #     # Presistence
    #
    #     save_session = False if self.is_disabled('saveSession') else True
    #     save_events = False if self.is_disabled('saveEvents') else True
    #     save_profile = True
    #
    #     # Save profile
    #     if save_profile and profile.operation.new:
    #         profile_result = await StorageFor(profile).index().save()
    #     else:
    #         profile_result = BulkInsertResult()
    #
    #     # Save session
    #     if save_session and (session.operation.new or session.profile is None or session.profile.id != profile.id):
    #         # save only profile Entity
    #         session.profile = Entity(id=profile.id)
    #         session_result = await StorageFor(session).index().save()
    #     else:
    #         session_result = BulkInsertResult()
    #
    #     # Save events
    #     if save_events:
    #         events_to_save = [event for event in events if event.is_persistent()]
    #         event_result = await StorageForBulk(events_to_save).index('event').save()
    #         event_result = SaveResult(**event_result.dict())
    #
    #         # Add event types
    #         for event in events:
    #             event_result.types.append(event.type)
    #     else:
    #         event_result = BulkInsertResult()
    #
    #     result = {
    #         "session": session_result,
    #         "events": event_result,
    #         "profile": profile_result
    #
    #     }
    #     return profile, session, events, CollectResult(**result)

    async def get_profile_and_session(self, session: Session, load_merged_profile) -> Tuple[Profile, Session]:

        """
        Returns session. Creates profile if it does not exist.If it exists connects session with profile.
        """

        is_new_profile = False
        is_new_session = False

        if session is None:  # loaded session is empty

            session = Session(id=self.session.id)
            is_new_session = True

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

            # There is session. Copy profile id form session to profile

            if session.profile is not None:
                # Loaded session has profile

                # Load profile based on profile id saved in session
                profile = await load_merged_profile(id=session.profile.id)  # type: Profile

                if session.profile.id != profile.id:
                    # Profile in session id has been merged. Change profile in session.

                    session.profile.id = profile.id
                    session.metadata.time = Time(insert=datetime.utcnow())

                    is_new_session = True

                # profile = await profile.storage().load()  # type: Profile

            else:
                # Corrupted session

                profile = None

            if profile is None:
                # Id exists but profile not exist in storage.

                profile = Profile.new()

                # Create new profile
                is_new_profile = True

        session.context = self.context
        session.properties = self.properties
        session.operation.new = is_new_session

        profile.operation.new = is_new_profile

        return profile, session

    # async def process(self, profile, session, events) -> Tuple[dict, Profile]:
    #
    #     # profile, session, events, collect_result = await self.save_collected_data(profile, session, events)
    #
    #     rules_engine = RulesEngine(
    #         session,
    #         profile,
    #         events)
    #
    #     debug_info_by_event_type_and_rule_name, segmentation_result, console_log = await rules_engine.execute(
    #         self.source.id
    #     )
    #
    #     # Prepare response
    #     result = {}
    #
    #     # Debugging
    #     # todo save result to different index
    #     if not tracardi.track_debug and not self.is_disabled('debugger'):
    #         debug_result = TrackerPayloadResult(**collect_result.dict())
    #         debug_result = debug_result.dict()
    #         debug_result['execution'] = debug_info_by_event_type_and_rule_name
    #         debug_result['segmentation'] = segmentation_result
    #         debug_result['logs'] = console_log
    #         result['debugging'] = debug_result
    #
    #     # Profile
    #     if self.return_profile():
    #         result["profile"] = profile.dict(
    #             exclude={
    #                 "traits": {"private": ...},
    #                 "pii": ...,
    #                 "operation": ...
    #             })
    #     else:
    #         result["profile"] = profile.dict(include={"id": ...})
    #
    #     return result, profile
