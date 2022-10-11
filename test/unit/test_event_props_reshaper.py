import pytest

from tracardi.service.event_props_reshaper import EventPropsReshaper
from tracardi.service.notation.dot_accessor import DotAccessor
from tracardi.domain.event import Event, EventMetadata, EventSession
from tracardi.domain.entity import Entity
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session, SessionMetadata
from tracardi.domain.event_metadata import EventTime
from tracardi.domain.event_payload_validator import ReshapeSchema
from copy import deepcopy
from pydantic import ValidationError


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

    event_to_reshape = Event(
        id='1',
        type='text',
        metadata=EventMetadata(time=EventTime()),
        session=EventSession(id='1'),
        source=Entity(id='1'),
        properties=deepcopy(props)
    )
    event = EventPropsReshaper(
        event=event_to_reshape,
        dot=DotAccessor(profile=profile, event=event_to_reshape, session=session)
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
    event_to_reshape = Event(
        id='1',
        type='text',
        metadata=EventMetadata(time=EventTime()),
        session=EventSession(id='1'),
        source=Entity(id='1'),
        properties=deepcopy(props)
    )
    event = EventPropsReshaper(
        event=event_to_reshape,
        dot=DotAccessor(profile=profile, event=event_to_reshape, session=session)
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

    event_to_reshape = Event(
        id='1',
        type='text',
        metadata=EventMetadata(time=EventTime()),
        session=EventSession(id='1'),
        source=Entity(id='1'),
        properties=deepcopy(props)
    )
    event = EventPropsReshaper(
        event=event_to_reshape,
        dot=DotAccessor(profile=profile, event=event_to_reshape, session=session)
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

    event_to_reshape = Event(
        id='1',
        type='text',
        metadata=EventMetadata(time=EventTime()),
        session=EventSession(id='1'),
        source=Entity(id='1'),
        properties=deepcopy(props)
    )
    event = EventPropsReshaper(
        event=event_to_reshape,
        dot=DotAccessor(profile=profile, event=event_to_reshape, session=session)
    ).reshape(schema)
    assert event.properties == props


def test_should_not_reshape_with_wrong_condition():
    """
    Condition is validated in ReshapeSchema class. There is no way reshaping runs with wrong condition.
    Although event is not going to be reshaped if the condition is somehow invalid.
    """
    with pytest.raises(ValidationError):
        _ = ReshapeSchema(
            condition="wrong_condition",
            template={}
        )
    props = {
        "prop1": 1,
        "prop2": 2,
        "prop3": {
            "prop4": "string"
        }
    }
    profile = Profile(id="1")
    session = Session(
        id='1',
        metadata=SessionMetadata()
    )
    schema = ReshapeSchema(
        template={"key": "profile@id"}
    )
    schema.condition = "wrong_condition"

    event_to_reshape = Event(
            id='1',
            type='text',
            metadata=EventMetadata(time=EventTime()),
            session=EventSession(id='1'),
            source=Entity(id='1'),
            properties=deepcopy(props)
    )
    event = EventPropsReshaper(
        event=event_to_reshape,
        dot=DotAccessor(profile=profile, event=event_to_reshape, session=session)
    ).reshape(schema)
    assert event.properties == props


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
        template={
            "all": "event@..."
        }
    )

    event = EventPropsReshaper(
        event=(_event := Event(
            id='1',
            type='text',
            metadata=EventMetadata(time=EventTime()),
            session=EventSession(id='1'),
            source=Entity(id='1'),
            properties=deepcopy(props)
        )),
        dot=DotAccessor(profile=profile, event=_event, session=session)
    ).reshape(schema)

    assert event.properties['all']['id'] == event.id
    assert event.properties['all']['properties'] == props
