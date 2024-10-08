from uuid import uuid4

import pytest

from tracardi.context import ServerContext, Context
from tracardi.domain.profile import FlatProfile
from tracardi.domain.profile_data import PREFIX_EMAIL_MAIN, PREFIX_IDENTIFIER_ID, PREFIX_IDENTIFIER_PK


def test_logger():
    fp = FlatProfile({
        "id": 1,
        "prop": {
            "a": 1
        }
    })

    assert fp['prop.a'] == 1
    assert 'prop.a' not in fp.log.get_log()

    fp['prop.a'] = 2
    assert 'prop.a' in fp.log.get_log().keys()
    assert fp['prop.a'] == 2

    # do not update change log
    fp['metadata.fields.xxx'] = 2
    assert 'metadata.fields.xxx' not in fp.log.get_log().keys()


def test_id():
    fp = FlatProfile({
        "id": "1",
        "prop": {
            "a": 1
        }
    })

    fp.id = "2"

    assert fp.id == "2"

    with pytest.raises(ValueError):
        fp.id = 1


def test_ids():
    fp = FlatProfile({
        "id": "1",
        "prop": {
            "a": 1
        }
    })

    assert fp['ids'] == []

    with pytest.raises(ValueError):
        fp.ids = "2"

    assert fp.ids == []

    fp.ids.append("3")

    assert fp.ids == ["3"]

    fp = FlatProfile({
        "id": "1",
        "ids": ["1", "2"],
        "prop": {
            "a": 1
        }
    })

    assert fp['ids'] == ["1", "2"]

    with pytest.raises(ValueError):
        fp = FlatProfile({
            "id": "1",
            "ids": "2",
            "prop": {
                "a": 1
            }
        })


def test_bool():
    fp = FlatProfile({
        "id": "1",
        "prop": {
            "a": 1
        }
    })
    assert fp.has('data.identifier.pk') is False


def test_flat_profile_initialization():
    # Test initialization with no ids provided
    profile_data = {}
    profile = FlatProfile(profile_data)
    assert profile['ids'] == []

    # Test initialization with ids
    profile_data = {'ids': ['id1', 'id2']}
    profile = FlatProfile(profile_data)
    assert profile['ids'] == ['id1', 'id2']


def test_flat_profile_add_auto_merge_hashed_id():
    profile_data = {}
    profile = FlatProfile(profile_data)

    # Test adding auto-merge hashed id
    flat_field = 'data.contact.email.main'
    result = profile.add_auto_merge_hashed_id(flat_field)
    assert result is None or isinstance(result, str)


def test_flat_profile_set_and_get_ids():
    # Test setting and getting ids
    profile_data = {}
    profile = FlatProfile(profile_data)
    profile.ids = ['id1', 'id2']
    assert profile.ids == ['id1', 'id2']

    # Test setting ids with invalid type
    with pytest.raises(ValueError):
        profile.ids = 'not_a_list'


def test_flat_profile_increase_interest():
    # Test increase in interest
    profile_data = {}
    profile = FlatProfile(profile_data)
    interest_key = 'interest1'
    profile.increase_interest(interest_key, 2)
    assert profile[f'interests.{interest_key}'] == 2

    # Test decrease in interest
    profile.decrease_interest(interest_key, 1)
    assert profile[f'interests.{interest_key}'] == 1

    # Test reset of interest
    profile.reset_interest(interest_key, 0)
    assert profile[f'interests.{interest_key}'] == 0


def test_flat_profile_metadata_fields():
    # Test adding metadata timestamps
    profile_data = {}
    profile = FlatProfile(profile_data)
    field_change_logger = profile.log
    field_change_logger.log('test_field')
    profile.set_metadata_fields_timestamps(field_change_logger)
    assert 'metadata.fields' in profile


def test_flat_profile_new():
    # Test creating a new FlatProfile
    with ServerContext(Context(production=False)):
        new_id = str(uuid4())
        flat_profile = FlatProfile.new(id=new_id)
        assert flat_profile['id'] == new_id

        assert flat_profile.has('metadata.time.create')
        assert flat_profile.has('metadata.time.insert')


def test_flat_profile_has_methods():
    profile_data = {
        'ids': [f'{PREFIX_EMAIL_MAIN}_identifier_id_some_hash', f'{PREFIX_IDENTIFIER_ID}_identifier_pk_some_hash',
                f'{PREFIX_IDENTIFIER_PK}-xx'],
    }
    profile = FlatProfile(profile_data)

    # Test has_hashed_email_id method
    assert profile.has_hashed_email_id() is True

    # Test has_hashed_phone_id method
    assert profile.has_hashed_phone_id() is False

    # Test has_hashed_id and has_hashed_pk
    assert profile.has_hashed_id() is True
    assert profile.has_hashed_pk() is True


def test_flat_profile_mark_for_update():
    # Test marking profile for update
    profile_data = {}
    profile = FlatProfile(profile_data)
    profile.mark_for_update()
    assert profile['operation.update'] is True
    assert 'metadata.time.update' in profile


if __name__ == "__main__":
    pytest.main()
