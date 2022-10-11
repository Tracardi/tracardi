from tracardi.domain.entity import Entity
from tracardi.domain.event_metadata import EventMetadata, EventTime
from tracardi.domain.session import Session, SessionMetadata
from tracardi.domain.event import Event, EventSession
from tracardi.domain.profile import Profile
from tracardi.process_engine.action.v1.traits.append_trait_action import AppendTraitAction
from tracardi.service.plugin.service.plugin_runner import run_plugin


def test_plugin_append_trait():
    payload = {}
    profile = Profile(id="1")
    event = Event(
        id='1',
        type='text',
        metadata=EventMetadata(time=EventTime()),
        session=EventSession(id='1'),
        source=Entity(id='1')
    )
    session = Session(
        id='1',
        metadata=SessionMetadata()
    )

    result = run_plugin(AppendTraitAction, {
        "append": {
            "profile@traits.public.value": 1
        }
    }, payload, profile=profile, event=event, session=session)
    assert result.profile.traits.public['value'] == 1

    result = run_plugin(AppendTraitAction, {
        "append": {
            "profile@traits.public.value": 2
        }
    }, payload, profile=profile, event=event, session=session)
    assert result.profile.traits.public['value'] == [1, 2]

    result = run_plugin(AppendTraitAction, {
        "remove": {
            "profile@traits.public.value": 2
        }
    }, payload, profile=profile, event=event, session=session)
    assert result.profile.traits.public['value'] == [1]

    result = run_plugin(AppendTraitAction, {
        "append": {
            "profile@traits.public.value": 3
        }
    }, payload, profile=profile, event=event, session=session)
    assert result.profile.traits.public['value'] == [1, 3]

    result = run_plugin(AppendTraitAction, {
        "remove": {
            "profile@traits.public.value": [1, 3]
        }
    }, payload, profile=profile, event=event, session=session)
    assert result.profile.traits.public['value'] == []

    result = run_plugin(AppendTraitAction, {
        "append": {
            "profile@traits.public.objects": [{"A": 1}]
        }
    }, payload, profile=profile, event=event, session=session)
    assert result.profile.traits.public['objects'] == [{"A": 1}]

    result = run_plugin(AppendTraitAction, {
        "remove": {
            "profile@traits.public.objects": [{"A": 1}]
        }
    }, payload, profile=profile, event=event, session=session)
    assert result.profile.traits.public['objects'] == []


def test_plugin_append_trait_fail():
    payload = {}
    profile = Profile(id="1")
    event = Event(
        id='1',
        type='text',
        metadata=EventMetadata(time=EventTime()),
        session=EventSession(id='1'),
        source=Entity(id='1')
    )
    session = Session(
        id='1', metadata=SessionMetadata()
    )

    try:
        run_plugin(AppendTraitAction, {
            "remove": {
                "profile@id": 1
            }
        }, payload, profile=profile, event=event, session=session)
        assert False
    except ValueError as e:
        assert str(e) == 'Can not remove from non-list data.'

