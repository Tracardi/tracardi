import pytest
from unittest.mock import AsyncMock

from tracardi.context import ServerContext, Context
from tracardi.domain.flat_profile import FlatProfile
from tracardi.domain.entity import Entity, PrimaryEntity
from tracardi.domain.event_metadata import EventPayloadMetadata
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.domain.session import SessionMetadata, Session
from tracardi.domain.time import Time
from tracardi.service.tracking.profile_loading import load_profile_and_session


@pytest.mark.asyncio
async def test_load_profile_and_session():

    with ServerContext(Context(production=False)):

        # Arrange
        profile_id = "4"
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

        session = Session(id="session-101", profile=Entity(id=profile_id), metadata=SessionMetadata())

        tracker_payload._get_profile = AsyncMock(return_value=(FlatProfile(dict(id=profile_id)), session))

        # Act
        flat_profile, session_result = await load_profile_and_session(session, True, tracker_payload)

        # Assert
        assert isinstance(flat_profile, FlatProfile), "Profile should be of type FlatProfile"
        assert flat_profile.id == profile_id, "Profile ID should match the expected value"
        assert session_result.id == "session-101", "Session ID should match the expected value"
        assert session_result.profile is not None, "Session should have an associated profile"
