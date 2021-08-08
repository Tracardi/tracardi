from tracardi.domain.context import Context
from tracardi.domain.event import Event
from tracardi.domain.flow import Flow
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.domain.source import Source
from tracardi_dot_notation.dot_accessor import DotAccessor


def test_value_read():
    profile = Profile(id="1")
    session = Session(id="2")
    payload = {"a": 3}
    source = Source(id="3", type="event")
    context = Context()
    event = Event(id="event-id", type="type", source=source, context=context, profile=profile, session=session)
    flow = Flow(id="flow-id", name="flow")
    dot = DotAccessor(profile, session, payload, event, flow)

    assert dot['profile@id'] == "1"
    assert dot['session@id'] == "2"
    assert dot['payload@a'] == 3
    assert dot['flow@id'] == "flow-id"
    assert dot['event@id'] == "event-id"

    try:
        _ = dot['profile@none']
        assert False
    except KeyError:
        assert True

    dot['payload@b'] = 2
    assert dot['payload@b'] == 2

    dot['profile@other.a'] = 2
    assert dot['profile@other.a'] == 2

    assert dot.profile['other']['a'] == 2


def test_value_exists():
    profile = Profile(id="1")
    session = Session(id="2")
    payload = {"a": 3}
    source = Source(id="3", type="event")
    context = Context()
    event = Event(id="event-id", type="type", source=source, context=context, profile=profile, session=session)
    flow = Flow(id="flow-id", name="flow")
    dot = DotAccessor(profile, session, payload, event, flow)

    assert 'profile@id' in dot
    assert 'profile@missing' not in dot
