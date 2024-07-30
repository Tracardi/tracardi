from uuid import uuid4

from tracardi.domain.named_entity import NamedEntity
from tracardi.service.notation.dot_accessor import DotAccessor
from tracardi.domain.event import Event, EventMetadata, EventSession
from tracardi.domain.entity import Entity
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session, SessionMetadata
from tracardi.domain.time import EventTime
from tracardi.domain.event_reshaping_schema import ReshapeSchema, EventReshapingSchema, EventReshapeDefinition
from copy import deepcopy

from tracardi.service.tracking.tracker_event_props_reshaper import EventDataReshaper


def _test_reshaper(dot, schema):
    edr = EventDataReshaper(dot)
    return edr.reshape(schemas=[
        EventReshapingSchema(
            id="1",
            name="reshape",
            event_type="test",
            event_source=NamedEntity(id="2", name="some name"),
            reshaping=ReshapeSchema(
                reshape_schema=schema
            ),
            enabled=True
        )
    ])


def test_reshaping_event_properties_when_schema_has_event_reshapes():
    dot = DotAccessor(profile={id: "1"})
    result = _test_reshaper(
        dot,
        EventReshapeDefinition(
            properties={}
        )
    )
    assert result is None

    result = _test_reshaper(
        dot,
        EventReshapeDefinition()
    )
    assert result is None


def test_removing_event_properties():
    event_to_reshape = Event(
        id='1',
        type='text',
        name='text',
        metadata=EventMetadata(time=EventTime()),
        session=EventSession(id='1'),
        source=Entity(id='1'),
        properties={"id": "1", "a": 2}
    )

    dot = DotAccessor(event=event_to_reshape)
    event_properties, event_context, session_context = _test_reshaper(
        dot,
        EventReshapeDefinition(
            properties={
                "-": ['id']
            }
        )
    )
    assert dot.event['properties'] == {'a': 2, 'id': '1'}
    assert event_properties == {"a": 2}
    assert event_context is None
    assert session_context is None

    event_dict = {"properties": {"id": "1", "a": 3}}
    dot = DotAccessor(event=event_dict)
    event_properties, event_context, session_context = _test_reshaper(
        dot,
        EventReshapeDefinition(
            properties={
                "-": ['id'],
                "a": 4
            }
        )
    )

    assert dot.event['properties'] == {'a': 3, 'id': '1'}
    assert event_properties == {"a": 4}
    assert event_context is None
    assert session_context is None


def test_should_return_none_if_no_reshaping():
    profile = Profile(id="1")
    session = Session(
        id='1',
        metadata=SessionMetadata()
    )
    props = {
        "prop1": 1,
        "prop2": 2,
        "prop3": {
            "prop4": "string"
        },
        "sess1": {
            "context": "session"
        }
    }

    # Empty schema
    schema = ReshapeSchema(
        reshape_schema=EventReshapeDefinition()
    )

    schemas = [
        EventReshapingSchema(
            id=str(uuid4()),
            name="test",
            event_type='text',
            reshaping=schema,
            event_source=NamedEntity(id="1", name="1")
        )
    ]

    event_to_reshape = Event(
        id='1',
        type='text',
        name='text',
        metadata=EventMetadata(time=EventTime()),
        session=EventSession(id='1'),
        source=Entity(id='1'),
        properties=deepcopy(props)
    )

    result = EventDataReshaper(
        dot=DotAccessor(profile=profile, event=event_to_reshape, session=session)
    ).reshape(schemas)

    assert result is None


def test_should_reshape_event_properties():
    profile = Profile(id="1")
    session = Session(
        id='1',
        metadata=SessionMetadata()
    )
    props = {
        "prop1": 1,
        "prop2": 2,
        "prop3": {
            "prop4": "string"
        },
        "sess1": {
            "context": "session"
        }
    }

    schema = ReshapeSchema(
        reshape_schema=EventReshapeDefinition(
            properties={
                "prop5": "event@properties.prop2",
                "prop6": {
                    "key": ["event@properties.prop3"]
                },
                "prop7": ["event@properties.does-not-exist"]
            },
            session={
                "context": "event@properties.sess1",
                "empty": "event@none"
            }
        )
    )

    schemas = [
        EventReshapingSchema(
            id=str(uuid4()),
            name="test",
            event_type='text',
            reshaping=schema,
            event_source=NamedEntity(id="1", name="1")
        )
    ]

    event_to_reshape = Event(
        id='1',
        type='text',
        name='text',
        metadata=EventMetadata(time=EventTime()),
        session=EventSession(id='1'),
        source=Entity(id='1'),
        properties=deepcopy(props)
    )

    event_properties, event_context, session_context = EventDataReshaper(
        dot=DotAccessor(profile=profile, event=event_to_reshape, session=session)
    ).reshape(schemas)

    assert event_properties == {
        "prop5": props["prop2"],
        "prop6": {
            "key": [props["prop3"]]
        },
        "prop7": [None]
    }

    assert session_context == {'context': {'context': 'session'}, 'empty': None}
    assert event_context is None


def test_should_reshape_whole_objects():
    """
    Check line 72 in dict_traverser.py
    """
    profile = Profile(id="1")
    session = Session(
        id='1',
        metadata=SessionMetadata()
    )
    props = {
        "prop1": 1,
        "prop2": 2,
        "prop3": {
            "prop4": "string"
        }
    }
    schema = ReshapeSchema(
        reshape_schema=EventReshapeDefinition(properties={
            "all": "event@..."
        })
    )
    event = Event(
        id='1',
        type='text',
        name='text',
        metadata=EventMetadata(time=EventTime()),
        session=EventSession(id='1'),
        source=Entity(id='1'),
        properties=deepcopy(props)
    )

    event_properties, event_context, session_context = EventDataReshaper(
        dot=DotAccessor(profile=profile, event=event, session=session)
    ).reshape([
        EventReshapingSchema(
            id=str(uuid4()),
            name="test",
            event_type='text',
            reshaping=schema,
            event_source=NamedEntity(id="1", name="1")
        )
    ])

    assert event_properties['all']['id'] == event.id
    assert event_properties['all']['properties'] == props
    assert event_context is None
    assert session_context is None
