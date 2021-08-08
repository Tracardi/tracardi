import elasticsearch
import pytest

import tracardi
from .mocks.mock_storage import MockStorageCrud
from tracardi.domain.entity import Entity
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.domain.payload.tracker_payload import TrackerPayload


@pytest.mark.asyncio
async def test_get_context_session_exists_profile_not_exists(mocker):

    mocker.patch('tracardi.domain.session.StorageCrud', MockStorageCrud)
    mocker.patch('tracardi.domain.session.StorageCrud', MockStorageCrud)
    mocker.patch('tracardi.domain.entity.crud', tracardi.tests.unit.mocks.mock_storage)
    mocker.patch('tracardi.domain.profile.StorageCrud', MockStorageCrud)

    # Session exists and has profile equal to 1
    tracker_payload = TrackerPayload(
        session=Entity(id="1"),
        profile=None,
        source=Entity(id="scope")
    )

    profile, session = await tracker_payload._get_profile_and_session()

    assert isinstance(profile, Profile)
    assert isinstance(session, Session)

    assert profile.id == "1"
    assert session.id == "1"


@pytest.mark.asyncio
async def test_get_context_session_exists_profile_exists_conflict(mocker):
    mocker.patch('tracardi.domain.session.StorageCrud', MockStorageCrud)
    mocker.patch('tracardi.domain.session.StorageCrud', MockStorageCrud)
    mocker.patch('tracardi.domain.entity.crud', tracardi.tests.unit.mocks.mock_storage)
    mocker.patch('tracardi.domain.profile.StorageCrud', MockStorageCrud)

    # Session exists and has profile equal to 1
    tracker_payload = TrackerPayload(
        session=Entity(id="1"),
        profile=Entity(id="2"),
        source=Entity(id="scope")
    )

    profile, session = await tracker_payload._get_profile_and_session()

    assert isinstance(profile, Profile)
    assert isinstance(session, Session)

    # profile from session is most important
    assert profile.id == "1"
    assert session.id == "1"


@pytest.mark.asyncio
async def test_get_context_session_not_exists_profile_exists(mocker):
    mocker.patch('tracardi.domain.session.StorageCrud', MockStorageCrud)
    mocker.patch('tracardi.domain.session.StorageCrud', MockStorageCrud)
    mocker.patch('tracardi.domain.entity.crud', tracardi.tests.unit.mocks.mock_storage)
    mocker.patch('tracardi.domain.profile.StorageCrud', MockStorageCrud)

    # Session 2 does not exist
    # Profile 2 exists
    tracker_payload = TrackerPayload(
        session=Entity(id="generated_not_exists-01"),
        profile=Entity(id="2"),
        source=Entity(id="scope")
    )

    profile, session = await tracker_payload._get_profile_and_session()

    assert isinstance(profile, Profile)
    assert isinstance(session, Session)

    # Do not generate profile copy it from param
    assert session.id == "generated_not_exists-01"
    assert profile.id == "2"


@pytest.mark.asyncio
async def test_get_context_session_not_exists_profile_not_exists(mocker):
    mocker.patch('tracardi.domain.session.StorageCrud', MockStorageCrud)
    mocker.patch('tracardi.domain.session.StorageCrud', MockStorageCrud)
    mocker.patch('tracardi.domain.entity.crud', tracardi.tests.unit.mocks.mock_storage)
    mocker.patch('tracardi.domain.profile.StorageCrud', MockStorageCrud)

    tracker_payload = TrackerPayload(
        session=Entity(id="generated_not_exists-02"),
        profile=None,
        source=Entity(id="scope")
    )

    profile, session = await tracker_payload._get_profile_and_session()

    assert isinstance(profile, Profile)
    assert isinstance(session, Session)

    # Profile generated
    assert profile.id != "2"
    # Session generated
    assert session.id == "generated_not_exists-02"


@pytest.mark.asyncio
async def test_load_session_with_error(mocker):
    def exc(*args):
        raise elasticsearch.exceptions.ElasticsearchException("test")

    mocker.patch('tracardi.domain.session.StorageCrud.load', exc)

    try:
        tracker_payload = TrackerPayload(
            session=Entity(id="non_existent"),
            profile=None,
            source=Entity(id="scope")
        )

        profile, session = await tracker_payload._get_profile_and_session()

    except elasticsearch.exceptions.ElasticsearchException as e:
        assert str(e) == "test"
