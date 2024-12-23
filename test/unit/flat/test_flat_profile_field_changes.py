import pytest
from unittest.mock import MagicMock

from tracardi.domain.flat_profile import FlatProfile


@pytest.fixture
def flat_profile():
    """Fixture to create a sample FlatProfile with some initial data."""
    profile_data = {
        "id": "test-profile-id",
        "metadata": {
            "fields": {},
            "time": {"create": "2024-01-01T00:00:00", "insert": "2024-01-01T00:00:00"}
        },
        "ids": []
    }
    return FlatProfile(profile_data)


def test_fill_changed_fields_with_custom_changes(flat_profile):
    """Test fill_changed_fields when custom changes are provided."""

    # Mock the has_changes method to return True
    flat_profile.has_changes = MagicMock(return_value=True)

    # Define custom changes to pass to fill_changed_fields
    custom_changes = {
        "field1": ["old_value", "new_value"],
        "field2": ["old_value", "new_value"]
    }

    # Call the method with custom changes
    flat_profile.fill_changed_fields(custom_changes=custom_changes)

    # Verify that metadata.fields was updated correctly
    assert "field1" in flat_profile["metadata.fields"]
    assert flat_profile["metadata.fields.field1"] == ["old_value", "new_value"]
    assert "field2" in flat_profile["metadata"]["fields"]
    assert flat_profile["metadata.fields.field2"] == ["old_value", "new_value"]


def test_fill_changed_fields_without_touching_prev_changes(flat_profile):
    """Test fill_changed_fields without custom changes (using logged changes)."""
    flat_profile.monitor_changes(True)
    # Mock the has_changes method to return True
    flat_profile.set('traits.a', 1)
    flat_profile.set('traits.b', 2)

    assert flat_profile.has_changes()

    assert flat_profile['metadata.fields'] == {}

    flat_profile.fill_changed_fields()

    assert flat_profile['metadata.fields'] != {}
    assert 'traits.a' in flat_profile['metadata.fields']
    assert 'traits.b' in flat_profile['metadata.fields']

    flat_profile.fill_changed_fields(custom_changes={
        "a": [3, None],
        "traits.b": [4, None]
    })
    assert flat_profile['metadata.fields']['traits.b'] == [4, None]
    assert flat_profile['metadata.fields']['a'] == [3, None]


