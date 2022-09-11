from time import sleep

from tracardi.domain.session import Session, SessionMetadata


def test_session_metadata():
    session = Session(id="-1", metadata=SessionMetadata())
    sleep(1)
    new_session = Session(**session.dict())
    # Times should not be regenerated, but timestamp yes
    assert session.metadata.time.insert == new_session.metadata.time.insert
    assert session.metadata.time.timestamp != new_session.metadata.time.timestamp