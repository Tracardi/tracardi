import pytest, pytest_asyncio
from unittest.mock import AsyncMock, patch

from tracardi.context import ServerContext, Context
from tracardi.domain.flat_profile import FlatProfile
from tracardi.domain.entity import PrimaryEntity
from tracardi.domain.flat_session import FlatSession
from tracardi.service.tracking.profile_loading import load_profile_and_session1

pytest_plugins = ('pytest_asyncio',)

@pytest.mark.asyncio
async def test_load_profile_and_session():

    with ServerContext(Context(production=False)):

        # Arrange
        profile_id = "4"

        flat_session = FlatSession.new(id="session-101", profile_id=profile_id)

        # Act
        with patch('tracardi.service.tracking.profile_loading._has_profile_id_in_session') as has_profile_id_in_session, \
                patch('tracardi.service.tracking.profile_loading._get_profile', AsyncMock()) as get_profile:

            has_profile_id_in_session.return_value = True
            get_profile.return_value = (FlatProfile(dict(id=profile_id)), flat_session, None, None)

            flat_profile, session_result, _, _ = await load_profile_and_session1(
                flat_session,
                True,
                False,
                PrimaryEntity(id=profile_id),
                None
            )

        # Assert
        assert isinstance(flat_profile, FlatProfile), "Profile should be of type FlatProfile"
        assert flat_profile.id == profile_id, "Profile ID should match the expected value"
        assert session_result.id == "session-101", "Session ID should match the expected value"
        assert session_result.get('profile',None) is not None, "Session should have an associated profile"
