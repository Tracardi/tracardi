import pytest

from tracardi.domain.profile import FlatProfile


def test_logger():
    fp = FlatProfile({
        "id": 1,
        "prop": {
            "a": 1
        }
    })

    assert fp['prop.a'] == 1
    assert fp.log.get_log() == {}

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
