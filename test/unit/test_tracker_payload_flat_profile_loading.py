import pytest
from unittest.mock import AsyncMock, MagicMock

from tracardi.domain.entity import Entity, PrimaryEntity
from tracardi.domain.event_metadata import EventPayloadMetadata
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.domain.flat_profile import FlatProfile
from tracardi.domain.session import Session, SessionMetadata
from tracardi.domain.time import Time


@pytest.mark.asyncio
async def test_get_profile_and_session():
    # Arrange
    profile_id = "2"
    tracker_payload = TrackerPayload(
        source=Entity(id="1"),
        session=None,
        metadata=EventPayloadMetadata(time=Time()),
        profile=PrimaryEntity(id=profile_id),
        context={},
        request={},
        properties={},
        events=[],
        options={},
        profile_less=False
    )

    # Mock session and profile
    session = Session(id="session-123", profile=Entity(id=profile_id), metadata=SessionMetadata())
    static = False
    profile_less = False

    tracker_payload._get_profile = AsyncMock(return_value=(FlatProfile(dict(id="2")), session))
    tracker_payload._has_profile_id_in_session = MagicMock(return_value=True)

    # Act
    flat_profile, session_result = await tracker_payload.get_profile_and_session(session, static, profile_less)

    # Assert
    assert isinstance(flat_profile, FlatProfile), "Profile should be of type FlatProfile"
    assert flat_profile.id == profile_id, "Profile ID should match the expected value"
    assert session_result.id == "session-123", "Session ID should match the expected value"
    assert session_result.profile is not None, "Session should have an associated profile"


@pytest.mark.asyncio
async def test_get_profile_and_session_with_profile_less():
    # Arrange
    profile_id = "2"
    tracker_payload = TrackerPayload(
        source=Entity(id="1"),
        session=None,
        metadata=EventPayloadMetadata(time=Time()),
        profile=None,
        context={},
        request={},
        properties={},
        events=[],
        options={},
        profile_less=True
    )

    session = Session(id="session-456", profile=Entity(id=profile_id), metadata=SessionMetadata())
    static = False
    profile_less = True

    # Act
    profile, session_result = await tracker_payload.get_profile_and_session(session, static, profile_less)

    # Assert
    assert profile is None, "Profile should be None when profile_less is True"
    assert session_result.id == "session-456", "Session ID should match the expected value"


@pytest.mark.asyncio
async def test_get_profile_and_session_with_static():
    # Arrange
    profile_id = "3"
    tracker_payload = TrackerPayload(
        source=Entity(id="1"),
        session=None,
        metadata=EventPayloadMetadata(time=Time()),
        profile=PrimaryEntity(id=profile_id),
        context={},
        request={},
        properties={},
        events=[],
        options={},
        profile_less=False
    )

    # Mock session and profile
    session = Session(id="session-789", profile=Entity(id=profile_id), metadata=SessionMetadata())
    static = True
    profile_less = False

    tracker_payload._get_profile = AsyncMock(return_value=(FlatProfile(dict(id=profile_id)), session))
    tracker_payload._has_profile_id_in_session = MagicMock(return_value=True)

    # Act
    flat_profile, session_result = await tracker_payload.get_profile_and_session(session, static, profile_less)

    # Assert
    assert isinstance(flat_profile, FlatProfile), "Profile should be of type FlatProfile"
    assert flat_profile.id == profile_id, "Profile ID should match the expected value"
    assert session_result.id == "session-789", "Session ID should match the expected value"
    assert session_result.profile is not None, "Session should not have an associated profile"
