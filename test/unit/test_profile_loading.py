from typing import Callable

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
from tracardi.service.tracker_config import TrackerConfig
from tracardi.service.tracking.profile_loading import load_profile_and_session


async def _check_loading(loaded_session, profile_from_db, tracker_payload, expected_loads_no):
    # Use `patch` to mock the `load_session` function
    with patch("tracardi.domain.payload.tracker_payload.load_profile",
               new_callable=AsyncMock,
               return_value=profile_from_db) as mock_load_session:

        if isinstance(profile_from_db, Callable):
            mock_load_session.side_effect = profile_from_db

        tracker_config = TrackerConfig(ip='0.0.0.0', allowed_bridges=['rest'])

        result = await load_profile_and_session(
            loaded_session,
            tracker_config,
            tracker_payload
        )
        assert mock_load_session.call_count == expected_loads_no

        return result


@pytest.mark.asyncio
async def test_profile_loading_test_1():
    with ServerContext(Context(production=False)):

        # Test 1 - This test is loading profile by profile id in payload. Positive path.
        # Loaded profile ID equal to requested profile in payload
        # Both session and profile are correct

        profile = Profile.new(id='p123')
        existing_session = Session.new(id='s123', profile_id='p123')

        tracker_payload = TrackerPayload(
            source=Entity(id="1"),
            session=DefaultEntity(id=existing_session.id),
            metadata=EventPayloadMetadata(time=Time()),
            profile=PrimaryEntity(id=profile.id),
            context={},
            request={},
            properties={},
            events=[EventPayload(type="111222", properties={})],
        )

        profile_from_db = profile

        loaded_profile, loaded_session = await _check_loading(existing_session,
                                                              profile_from_db,
                                                              tracker_payload,
                                                              expected_loads_no=1)

        assert loaded_profile.id == profile.id
        assert loaded_session.id == existing_session.id
        assert loaded_session.profile.id == loaded_profile.id


@pytest.mark.asyncio
async def test_profile_loading_test_2():
    with ServerContext(Context(production=False)):
        # Test 2 - This test is loading profile by profile id in payload
        #
        # Loaded profile ID is not equal to requested profile ID in payload
        # Requested profile ID was p123 but loaded profile has x123, The p123 is in ids.
        # This can happen when the profile is merged and all device ids are moved to profile.ids.
        # The client id may be different then the selected it in profile. So profile has id=x123 but its
        # previous id was p123. now it is in profile.ids.
        # Expected behaviour. Returned profile has id x123, and tracker payload is corrected and its
        # profile id is now x123. This can only happen if the loaded profile has p123 in profile.ids.
        # Indicating that the correct profile was loaded.

        # Returned profile
        returned_profile = Profile.new(id='x123')
        returned_profile.ids = ['p123']
        existing_session = Session.new(id='s123', profile_id='p123')

        tracker_payload = TrackerPayload(
            source=Entity(id="1"),
            session=DefaultEntity(id=existing_session.id),
            metadata=EventPayloadMetadata(time=Time()),
            profile=PrimaryEntity(id='p123'),
            context={},
            request={},
            properties={},
            events=[EventPayload(type="111222", properties={})],
        )

        profile_from_db = returned_profile

        loaded_profile, loaded_session = await _check_loading(existing_session,
                                                              profile_from_db,
                                                              tracker_payload,
                                                              expected_loads_no=1)
        # Expecting profile id to be x123
        assert loaded_profile.id == returned_profile.id
        assert loaded_profile.id != 'p123'

        # Existing session should be returned
        assert loaded_session.id == existing_session.id
        assert loaded_session.profile.id == loaded_profile.id


@pytest.mark.asyncio
async def test_profile_loading_test_3():
    with ServerContext(Context(production=False)):
        # Test 3 - This test is loading profile by session id in payload
        #
        # There is no profile ID in tracker payload
        # There is session ID in payload
        # Profile ID from session is used to load the profile.
        # Requested profile ID (ID from session) was p123 but loaded profile has x123, The p123 is in ids.
        # This can happen when the profile is merged and all device ids are moved to profile.ids.
        # The client id may be different than the selected it in profile. So profile has id=x123 but its
        # previous id was p123. now it is in profile.ids.
        # Expected behaviour. Returned profile has id x123, and tracker payload is corrected and its
        # profile id is now x123. This can only happen if the loaded profile has p123 in profile.ids.
        # Indicating that the correct profile was loaded.

        existing_session = Session.new(id='s123', profile_id='p123')

        tracker_payload = TrackerPayload(
            source=Entity(id="1"),
            session=DefaultEntity(id='s123'),
            metadata=EventPayloadMetadata(time=Time()),
            profile=None,
            context={},
            request={},
            properties={},
            events=[EventPayload(type="111222", properties={})],
        )

        # Returned profile
        profile_from_db = Profile.new(id='x123')
        profile_from_db.ids = ['p123']
        profile_from_db.set_new(False)

        loaded_profile, loaded_session = await _check_loading(existing_session,
                                                              profile_from_db,
                                                              tracker_payload,
                                                              expected_loads_no=1)
        # Expecting profile id to be x123
        assert loaded_profile.id == profile_from_db.id
        assert loaded_profile.id != 'p123'

        # Existing session should be returned
        assert loaded_session.id == existing_session.id
        assert loaded_session.profile.id == loaded_profile.id

        assert not profile_from_db.is_new()


@pytest.mark.asyncio
async def test_profile_loading_test_4():
    with ServerContext(Context(production=False)):
        # Test 4 - This test is loading profile by tracker.session.profile.id in payload. tracker.profile.id is None
        #
        # There is no profile ID in tracker payload
        # There is session ID in payload
        # Profile ID from session is used to load the profile.
        # Requested profile ID (ID from session) was p123 but loaded profile has x123, The p123 IS NOT IN IDS.
        # Expected behaviour: loading error

        existing_session = Session.new(id='s123', profile_id='p123')

        tracker_payload = TrackerPayload(
            source=Entity(id="1"),
            session=DefaultEntity(id='s123'),
            metadata=EventPayloadMetadata(time=Time()),
            profile=None,
            context={},
            request={},
            properties={},
            events=[EventPayload(type="111222", properties={})],
        )

        # Returned profile
        profile_from_db = Profile.new(id='x123')
        profile_from_db.ids = ['NONE']

        with pytest.raises(ValueError):
            await _check_loading(existing_session,
                                 profile_from_db,
                                 tracker_payload,
                                 expected_loads_no=1)


@pytest.mark.asyncio
async def test_profile_loading_test_5():
    with ServerContext(Context(production=False)):
        # Test 5 - This test is generating profile. Profile id does not exists in session.
        #
        # There is no profile ID in tracker payload
        # There is session ID in payload but does not have profile id.

        # Profile is generated as new profile
        # Expected behaviour: New profile returned, session has new profile
        # Tracker payload has corrected values

        existing_session = Session.new(id='s123')

        tracker_payload = TrackerPayload(
            source=Entity(id="1"),
            session=DefaultEntity(id=existing_session.id),
            metadata=EventPayloadMetadata(time=Time()),
            profile=None,
            context={},
            request={},
            properties={},
            events=[EventPayload(type="111222", properties={})],
        )

        # Returned profile
        profile_from_db = None

        profile, session = await _check_loading(existing_session,
                                                profile_from_db,
                                                tracker_payload,
                                                expected_loads_no=0)

        assert profile.is_new()
        assert session.profile.id == profile.id

        assert tracker_payload.profile.id == profile.id
        assert tracker_payload.session.id == session.id


@pytest.mark.asyncio
async def test_profile_loading_test_6():
    with ServerContext(Context(production=False)):
        # Test 6 - This test tries to load profile but it does not exists then it fallback to loading via session
        # ID, and it succeeds
        #
        # There is profile ID in tracker payload but it returns None for profile (profile for this ID does not exist)
        # There is session ID in payload and it has existing profile id.
        #
        # Expected behaviour:
        # Profile is loaded twice
        # First with id="this-profile-does-not-exist" and it fails
        # Then it fallbacks to session.profile.id = 'x123' and it is ok
        # Correct profile is returned
        # Tracker payload is corrected

        existing_session = Session.new(id='s123', profile_id='x123')

        tracker_payload = TrackerPayload(
            source=Entity(id="1"),
            session=DefaultEntity(id=existing_session.id),
            metadata=EventPayloadMetadata(time=Time()),
            profile=PrimaryEntity(id="this-profile-does-not-exist"),
            context={},
            request={},
            properties={},
            events=[EventPayload(type="111222", properties={})],
        )

        # Returned profile
        def loading_function(profile_id):
            if profile_id == "this-profile-does-not-exist":
                return None
            elif profile_id == 'x123':
                profile = Profile.new(id='x123')
                profile.set_new(False)
                return profile

        profile, session = await _check_loading(existing_session,
                                                loading_function,
                                                tracker_payload,
                                                expected_loads_no=2)  # Profile was loaded twice

        assert not profile.is_new()
        assert profile.id == 'x123'
        assert session.profile.id == profile.id

        assert tracker_payload.profile.id == profile.id
        assert tracker_payload.session.id == session.id


@pytest.mark.asyncio
async def test_profile_loading_test_7():
    with ServerContext(Context(production=False)):
        # Test 7 - This test tries to load profile but it does not exists then it fallback to loading via session ID
        #
        # There is profile ID in tracker payload but it returns None for profile (profile for this ID does not exist)
        # There is session ID in payload and it has existing profile id.
        #
        # Expected behaviour:
        # Profile is loaded only ONCE as the session.profile.id and profile.id are equal
        # First with id="this-profile-does-not-exist" and it fails
        # Then it fallbacks to session.profile.id id="this-profile-does-not-exist" but it does not load as IDS ARE THE SAME.
        # NEW Profile is created
        # Tracker payload is corrected

        existing_session = Session.new(id='s123', profile_id="this-profile-does-not-exist")

        tracker_payload = TrackerPayload(
            source=Entity(id="1"),
            session=DefaultEntity(id=existing_session.id),
            metadata=EventPayloadMetadata(time=Time()),
            profile=PrimaryEntity(id="this-profile-does-not-exist"),
            context={},
            request={},
            properties={},
            events=[EventPayload(type="111222", properties={})],
        )

        # Returned profile
        def loading_function(profile_id):
            if profile_id == "this-profile-does-not-exist":
                return None
            else:
                assert False  # This should never be called

        profile, session = await _check_loading(existing_session,
                                                loading_function,
                                                tracker_payload,
                                                expected_loads_no=1)  # Profile was loaded once

        assert profile.is_new()
        assert profile.id != "this-profile-does-not-exist"
        assert session.profile.id == profile.id

        assert tracker_payload.profile.id == profile.id
        assert tracker_payload.session.id == session.id

@pytest.mark.asyncio
async def test_profile_loading_test_8():
    with ServerContext(Context(production=False)):
        # Test 8 - This test tries to load profile, but it does not exist then it fall-back to loading via session ID
        # and is also does not exist.
        #
        # There is profile ID in tracker payload, but it returns None for profile (profile for this ID does not exist)
        # There is session ID in payload, and it has existing profile id.
        #
        # Expected behaviour:
        # Profile is loaded twice
        # First with id="this-profile-does-not-exist-1" and it fails
        # Then it fallbacks to session.profile.id id="this-profile-does-not-exist-1" but also fails.
        # NEW Profile is created
        # Tracker payload is corrected

        existing_session = Session.new(id='s123', profile_id="this-profile-does-not-exist-2")

        tracker_payload = TrackerPayload(
            source=Entity(id="1"),
            session=DefaultEntity(id=existing_session.id),
            metadata=EventPayloadMetadata(time=Time()),
            profile=PrimaryEntity(id="this-profile-does-not-exist-1"),
            context={},
            request={},
            properties={},
            events=[EventPayload(type="111222", properties={})],
        )

        # Returned profile
        def loading_function(profile_id):
            if profile_id == "this-profile-does-not-exist-1":  # loading with profile.id
                return None
            elif profile_id == "this-profile-does-not-exist-2":  # loading with session.profile.id
                return None
            else:
                assert False  # This should never be called

        profile, session = await _check_loading(existing_session,
                                                loading_function,
                                                tracker_payload,
                                                expected_loads_no=2)  # Profile was loaded twice

        assert profile.is_new()
        assert profile.id != "this-profile-does-not-exist"
        assert session.profile.id == profile.id

        assert tracker_payload.profile.id == profile.id
        assert tracker_payload.session.id == session.id


@pytest.mark.asyncio
async def test_profile_loading_test_9():
    with ServerContext(Context(production=False)):
        # Test 9 - This test tries to load profile (via session.profile.id) but it does not exists then it fallback generate profile
        #
        # There is not profile ID in tracker payload
        # There is session ID in payload and it has NOT-EXISTING profile id.
        #
        # Expected behaviour:
        # Profile is loaded once
        # Loading by tracker.profile.id is skipped. No profile ID in payload.
        # Then with tracker.session.profile.id="this-profile-does-not-exist" and it fails (does not exists in DB)
        # Then NEW Profile is created
        # Tracker payload is corrected

        existing_session = Session.new(id='s123', profile_id="this-profile-does-not-exist")

        tracker_payload = TrackerPayload(
            source=Entity(id="1"),
            session=DefaultEntity(id=existing_session.id),
            metadata=EventPayloadMetadata(time=Time()),
            profile=None,
            context={},
            request={},
            properties={},
            events=[EventPayload(type="111222", properties={})],
        )

        # Returned profile
        def loading_function(profile_id):
            if profile_id == "this-profile-does-not-exist":  # loading with session.profile.id
                return None
            else:
                assert False  # This should never be called

        profile, session = await _check_loading(existing_session,
                                                loading_function,
                                                tracker_payload,
                                                expected_loads_no=1)  # Profile was once twice

        assert profile.is_new()
        assert profile.id != "this-profile-does-not-exist"
        assert session.profile.id == profile.id

        assert tracker_payload.profile.id == profile.id
        assert tracker_payload.session.id == session.id


@pytest.mark.asyncio
async def test_profile_loading_test_10():
    with ServerContext(Context(production=False)):

        # Test 10 - This test is fully corrupted:
        # It loads profile and session both exists. But there is no connection between them.
        # Session profile ID is not equal to profile ID or IDS.
        #
        # There is profile ID in tracker payload
        # There is session ID in payload it has profile ID that does not exist in loaded profile.ids.
        #
        # Scenario
        # Profile B is loaded. It exists in DB and has ID = "D", IDS=['B']
        # Session has profile.id = 'A'
        # There is no match between session and profile.
        #
        # Expected behaviour:
        #
        # Loaded profile is returned has ID = "D", IDS=['B']
        # New shadow session generated.

        existing_session = Session.new(id='s123', profile_id="A")

        tracker_payload = TrackerPayload(
            source=Entity(id="1"),
            session=DefaultEntity(id='s123'),
            metadata=EventPayloadMetadata(time=Time()),
            profile=PrimaryEntity(id="B"),
            context={},
            request={},
            properties={},
            events=[EventPayload(type="111222", properties={})],
        )

        # Returned profile
        loaded_profile_from_db = Profile.new(id="D")
        loaded_profile_from_db.ids = ['B']
        loaded_profile_from_db.set_new(False)

        profile, session = await _check_loading(existing_session,
                                                loaded_profile_from_db,
                                                tracker_payload,
                                                expected_loads_no=1)  # Profile was once twice

        assert profile.id == loaded_profile_from_db.id
        assert 'B' in loaded_profile_from_db.ids
        assert session.id.startswith('shd-')

        assert not profile.is_new()

        assert tracker_payload.profile.id == profile.id
        assert tracker_payload.session.id == session.id