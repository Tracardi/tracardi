import pytest
from unittest.mock import patch, AsyncMock

from tracardi.context import ServerContext, Context
from tracardi.domain.entity import Entity, PrimaryEntity, DefaultEntity
from tracardi.domain.event_metadata import EventPayloadMetadata
from tracardi.domain.payload.event_payload import EventPayload
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.domain.time import Time
from tracardi.service.tracking.session_loading import load_or_create_session


async def _check_loading(session, tracker_payload, expected_loads_no):

    # Use `patch` to mock the `load_session` function
    with patch("tracardi.service.tracking.session_loading.load_session",
               new_callable=AsyncMock,
               return_value=session) as mock_load_session:

        # Call your async function
        result = await load_or_create_session(tracker_payload)
        assert mock_load_session.call_count == expected_loads_no

        return result


@pytest.mark.asyncio
async def test_load_or_create_session_all_data():
    with ServerContext(Context(production=False)):

        # Test 1 - All data provided. Positive path
        # Session, Profile in payload.
        # Correct session loaded with the correct profile attached.

        session_id = "s123"
        profile_id = "p123"
        profile = Profile.new(profile_id)

        tracker_payload = TrackerPayload(
            source=Entity(id="1"),
            session=DefaultEntity(id=session_id),
            metadata=EventPayloadMetadata(time=Time()),
            profile=PrimaryEntity(id=profile.id),
            context={},
            request={},
            properties={},
            events=[EventPayload(type="111222", properties={})],
        )

        session_from_db = Session.new(id=session_id)
        session_from_db.profile = Entity(id=profile.id)

        # Expecting to load the profile and session as defined in tracker payload

        session, payload = await _check_loading(session_from_db, tracker_payload, 1)

        assert session.id == session_id
        assert session.profile.id == profile.id

@pytest.mark.asyncio
async def test_load_or_create_session__only_session():
    with ServerContext(Context(production=False)):
        # Test 2 - Only session provided.
        # Session, Profile in payload.
        # Correct session loaded with the some profile from DB attached.

        session_id = "s123"
        profile = None

        tracker_payload = TrackerPayload(
            source=Entity(id="1"),
            session=DefaultEntity(id=session_id),
            metadata=EventPayloadMetadata(time=Time()),
            profile=None,
            context={},
            request={},
            properties={},
            events=[EventPayload(type="111222", properties={})],
        )

        # What db should return

        session_from_db = Session.new(id=session_id)
        session_from_db.profile = Profile.new(id="pid")

        # Expecting to load the profile and session as defined in tracker payload

        session, payload = await _check_loading(session_from_db, tracker_payload, 1)

        assert session.id == session_id
        assert session.profile.id == session_from_db.profile.id


@pytest.mark.asyncio
async def test_load_or_create_session_no_session():
    with ServerContext(Context(production=False)):
        # Test 3 - No session or profile in payload.
        # Database is not used to load the session (no ID).
        # Session is generated with empty profile

        tracker_payload = TrackerPayload(
            source=Entity(id="1"),
            session=None,
            metadata=EventPayloadMetadata(time=Time()),
            profile=None,
            context={},
            request={},
            properties={},
            events=[EventPayload(type="111222", properties={})],
        )

        # What db should return

        session_from_db = None

        # Expecting to load the profile and session as defined in tracker payload

        session, payload = await _check_loading(session_from_db, tracker_payload, 0)

        assert session.id is not None
        assert session.profile is None


@pytest.mark.asyncio
async def test_load_or_create_session_with_session_but_on_session_in_db():
    with ServerContext(Context(production=False)):
        # Test 4 - Session and profile in payload.
        # Both the session anf profile does not exist in DB.
        # Session is generated ID from payload and empty now has ID.

        # TODO poninna miec sessja profile przypiety czy nie. Chyba nie nie wiem czy jest w bazie.TO wszystko jest
        # TODO przy ładowaniu sessji. NIe wiem czy session.profile.id jest wykorzystywany do ładowania profily
        # TODO raczej nie.

        tracker_payload = TrackerPayload(
            source=Entity(id="1"),
            session=DefaultEntity(id='s123'),
            metadata=EventPayloadMetadata(time=Time()),
            profile=PrimaryEntity(id="p123"),
            context={},
            request={},
            properties={},
            events=[EventPayload(type="111222", properties={})],
        )

        # What db should return

        session_from_db = None

        # Expecting to load the profile and session as defined in tracker payload

        session, payload = await _check_loading(session_from_db, tracker_payload, 1)

        assert session.id == 's123'
        assert session.profile.id == 'p123'


@pytest.mark.asyncio
async def test_load_or_create_session_profile_conflict():
    with ServerContext(Context(production=False)):
        # Test 5 - Session and profile in payload.
        # Database loads the session but it has different profile then the one in tracker payload.
        # Conflicting profiles.
        # Expected behaviour:
        # Conflict resolution must wait until the profile is loaded and checked if the profile in payload
        # will not be used to load via profile.ids.  That's why the profile id in session and tracker are different.

        tracker_payload = TrackerPayload(
            source=Entity(id="1"),
            session=DefaultEntity(id='s123'),
            metadata=EventPayloadMetadata(time=Time()),
            profile=PrimaryEntity(id="p123"),
            context={},
            request={},
            properties={},
            events=[EventPayload(type="111222", properties={})],
        )

        # What db should return

        session_from_db = Session.new(id='s123')
        session_from_db.profile = Profile.new(id="incorrect-pid")

        session, payload = await _check_loading(session_from_db, tracker_payload, 1)

        # New session must be created
        assert session.id == 's123'
        # For delivered profile
        assert session.profile.id != tracker_payload.profile.id

