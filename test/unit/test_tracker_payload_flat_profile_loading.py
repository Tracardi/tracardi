import pytest
from unittest.mock import AsyncMock, patch

from tracardi.context import ServerContext, Context
from tracardi.domain.entity import PrimaryEntity
from tracardi.domain.flat_profile import FlatProfile
from tracardi.domain.flat_session import FlatSession
from tracardi.service.tracking.profile_loading import get_profile_and_session


@pytest.mark.asyncio
async def test_get_profile_and_session():
    # Arrange
    profile_id = "2"

    # Mock session and profile
    flat_session = FlatSession.new(id="session-123", profile_id=profile_id)
    static = False

    # Act
    with patch('tracardi.service.tracking.profile_loading._has_profile_id_in_session') as has_profile_id_in_session, \
        patch('tracardi.service.tracking.profile_loading._get_profile', AsyncMock()) as get_profile:

            has_profile_id_in_session.return_value = True
            get_profile.return_value = (FlatProfile(dict(id="2")), flat_session, None, None)

            flat_profile, session_result, tracker_profile, tracker_session = await get_profile_and_session(
                flat_session,
                static,
                False,
                PrimaryEntity(id=profile_id),
                None
            )

    # Assert
    assert isinstance(flat_profile, FlatProfile), "Profile should be of type FlatProfile"
    assert flat_profile.id == profile_id, "Profile ID should match the expected value"
    assert session_result.id == "session-123", "Session ID should match the expected value"
    assert session_result.get_or_none('profile') is not None, "Session should have an associated profile"


@pytest.mark.asyncio
async def test_get_profile_and_session_with_profile_less():

    with ServerContext(Context(production=True)):

        # Arrange
        profile_id = "2"

        flat_session = FlatSession.new(id="session-456", profile_id=profile_id)
        static = False

        # Act
        flat_profile, session_result, tracker_profile, tracker_session = await get_profile_and_session(
            flat_session,
            static,
            True,
            None,
            None
        )

        # Assert
        assert flat_profile is None, "Profile should be None when profile_less is True"
        assert session_result.id == "session-456", "Session ID should match the expected value"


@pytest.mark.asyncio
async def test_get_profile_and_session_with_static():
    # Arrange
    profile_id = "3"

    # Mock session and profile
    flat_session = FlatSession.new(id="session-789", profile_id=profile_id)
    static = True

    # Act
    with patch('tracardi.service.tracking.profile_loading._has_profile_id_in_session') as has_profile_id_in_session, \
            patch('tracardi.service.tracking.profile_loading._get_profile', AsyncMock()) as get_profile:

        has_profile_id_in_session.return_value = True
        get_profile.return_value = (FlatProfile(dict(id=profile_id)), flat_session, None, None)

        flat_profile, session_result, tracker_profile, tracker_session = await get_profile_and_session(
            flat_session,
            static,
            False,
            PrimaryEntity(id=profile_id),
            None
        )

    # Assert
    assert isinstance(flat_profile, FlatProfile), "Profile should be of type FlatProfile"
    assert flat_profile.id == profile_id, "Profile ID should match the expected value"
    assert session_result.id == "session-789", "Session ID should match the expected value"
    assert session_result.get_or_none('profile') is not None, "Session should not have an associated profile"
