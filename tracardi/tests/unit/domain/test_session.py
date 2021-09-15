from tracardi.domain.session import Session
from tracardi.domain.value_object.operation import Operation


def test_session():
    session = Session(id='1')
    assert isinstance(session.operation, Operation)
