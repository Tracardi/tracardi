from durable_dot_dict.dot import Dot

from tracardi.domain.flat_session import FlatSession


def test_replace():

    fs1 = FlatSession.new(id='1')
    fs2 = FlatSession.new(id='2')
    fs2['profile'] = 1

    assert 'profile' not in fs1

    fs1.replace(fs2)

    assert Dot(fs1).profile == 1


def test_props():
    fs1 = FlatSession.new(id='1') << {"metadata.time.tz": "UTC"}
    assert fs1.metadata_time_tz == 'UTC'
    assert FlatSession.metadat_time_tz == 'metadata.time.tz'


def test_dynamic_props():
    fs1 = FlatSession.new(id='1') << {"metadata.time.tz": "UTC"}
    print(fs1.id)
    fs1.id = 2

