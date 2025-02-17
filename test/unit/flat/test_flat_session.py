from durable_dot_dict.dot import Dot

from tracardi.domain.flat_session import FlatSession


def test_replace():

    fs1 = FlatSession.new(id='1')
    fs2 = FlatSession.new(id='2')
    fs2['profile'] = 1

    assert 'profile' not in fs1

    fs1.replace(fs2)

    assert Dot(fs1).profile == 1

