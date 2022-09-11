from tracardi.service.event_props_reshaper import EventPropsReshaper
from tracardi.service.notation.dot_accessor import DotAccessor
from tracardi.domain.event import Event, EventMetadata, EventSession
from tracardi.domain.entity import Entity
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session, SessionMetadata
from tracardi.domain.event_metadata import EventTime
from tracardi.domain.event_payload_validator import ReshapeSchema
from copy import deepcopy


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
        }
    }
    schema = ReshapeSchema(
        condition="event@properties.prop1 == 1",
        template={
            "prop5": "event@properties.prop2",
            "prop6": {
                "key": "event@properties.prop3"
            },
            "prop7": "event@properties.does-not-exist"
        }
    )

    EventPropsReshaper(
        event=(event := Event(
            id='1',
            type='text',
            metadata=EventMetadata(time=EventTime()),
            session=EventSession(id='1'),
            source=Entity(id='1'),
            properties=deepcopy(props)
        )),
        dot=DotAccessor(profile=profile, event=event, session=session)
    ).reshape(schema)
    assert event.properties == {
        "prop5": props["prop2"],
        "prop6": {
            "key": props["prop3"]
        },
        "prop7": None
    }

    schema = ReshapeSchema(
        condition="event@properties.prop1 == 2",
        template={
            "prop5": "event@properties.prop2",
            "prop6": {
                "key": "event@properties.prop3"
            },
            "prop7": "event@properties.does-not-exist"
        }
    )
    EventPropsReshaper(
        event=(event := Event(
            id='1',
            type='text',
            metadata=EventMetadata(time=EventTime()),
            session=EventSession(id='1'),
            source=Entity(id='1'),
            properties=deepcopy(props)
        )),
        dot=DotAccessor(profile=profile, event=event, session=session)
    ).reshape(schema)
    assert event.properties == props


def test_should_reshape_without_condition():
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
        condition="",
        template={
            "prop5": "event@properties.prop2",
            "prop6": {
                "key": "event@properties.prop3"
            },
            "prop7": "event@properties.does-not-exist"
        }
    )

    EventPropsReshaper(
        event=(event := Event(
            id='1',
            type='text',
            metadata=EventMetadata(time=EventTime()),
            session=EventSession(id='1'),
            source=Entity(id='1'),
            properties=deepcopy(props)
        )),
        dot=DotAccessor(profile=profile, event=event, session=session)
    ).reshape(schema)
    assert event.properties == {
        "prop5": props["prop2"],
        "prop6": {
            "key": props["prop3"]
        },
        "prop7": None
    }


def test_should_not_reshape_with_false_condition():
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
        condition="event@properties.prop1 == 100",
        template={
            "prop5": "event@properties.prop2",
            "prop6": {
                "key": "event@properties.prop3"
            },
            "prop7": "event@properties.does-not-exist"
        }
    )

    EventPropsReshaper(
        event=(event := Event(
            id='1',
            type='text',
            metadata=EventMetadata(time=EventTime()),
            session=EventSession(id='1'),
            source=Entity(id='1'),
            properties=deepcopy(props)
        )),
        dot=DotAccessor(profile=profile, event=event, session=session)
    ).reshape(schema)
    assert event.properties == props


def test_should_not_reshape_with_wrong_condition():
    """
    If there is an error in condition it should be logged but the whole process should not stop.
    Wrong condition should be evaluated as no reshaping.
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
        condition="wrong_condition",
        template={
            "prop5": "event@properties.prop2",
            "prop6": {
                "key": "event@properties.prop3"
            },
            "prop7": "event@properties.does-not-exist"
        }
    )

    EventPropsReshaper(
        event=(event := Event(
            id='1',
            type='text',
            metadata=EventMetadata(time=EventTime()),
            session=EventSession(id='1'),
            source=Entity(id='1'),
            properties=deepcopy(props)
        )),
        dot=DotAccessor(profile=profile, event=event, session=session)
    ).reshape(schema)
    assert event.properties == props


def test_should_reshape_whole_objects():
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
        condition="",
        template={
            "all": "event@..."
        }
    )

    EventPropsReshaper(
        event=(event := Event(
            id='1',
            type='text',
            metadata=EventMetadata(time=EventTime()),
            session=EventSession(id='1'),
            source=Entity(id='1'),
            properties=deepcopy(props)
        )),
        dot=DotAccessor(profile=profile, event=event, session=session)
    ).reshape(schema)

    # todo add asserts
