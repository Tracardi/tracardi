from uuid import uuid4

from tracardi.context import Context
from tracardi.domain.entity import Entity
from tracardi.domain.event import Event
from tracardi.domain.event_metadata import EventMetadata
from tracardi.domain.time import EventTime
from tracardi.service.failover.failover_manager import FailOverManager


def closure_true(event: Event):
    return True

def closure_false(event: Event):
    return False

def test_fail_over():
    fail_over = FailOverManager('test')
    events = [Event(
        id=str(uuid4()),
        name="test",
        type="test",
        metadata=EventMetadata(time=EventTime()),
        source=Entity(id="1")
    ).model_dump() for _ in range(0, 10)]

    fail_over.add(events)

    fail_over.flush(closure_false)
    assert not fail_over.is_empty()
    fail_over.flush(closure_true)
    assert fail_over.is_empty()
