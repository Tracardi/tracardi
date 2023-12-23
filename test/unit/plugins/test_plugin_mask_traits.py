from tracardi.context import ServerContext, Context
from tracardi.domain.entity import Entity
from tracardi.domain.event_metadata import EventMetadata
from tracardi.domain.profile import Profile
from tracardi.domain.time import EventTime
from tracardi.domain.session import Session, SessionMetadata
from tracardi.domain.event import Event, EventSession
from tracardi.process_engine.action.v1.traits.mask_traits_action import MaskTraitsAction
from tracardi.service.plugin.service.plugin_runner import run_plugin
from tracardi.domain.flow import Flow


def test_plugin_mask_traits():
    with ServerContext(Context(production=True)):
        profile = Profile.new()
        profile.traits = {
            "a": 1
        }
        payload = {}
        event = Event(
            id='1',
            type='text',
            name="text",
            metadata=EventMetadata(time=EventTime(), profile_less=True),
            session=EventSession(id='1'),
            source=Entity(id='1'),
            properties={"prop1": 5}
        )
        session = Session(
            id='1',
            metadata=SessionMetadata()
        )
        result = run_plugin(
            MaskTraitsAction,
            {
                "traits": ["flow@id", "profile@traits.a", "event@properties.prop1"]
            },
            payload=payload,
            event=event,
            session=session,
            profile=profile,
            flow=Flow(id="1", name="flow1", lock=False, type="collection")
        )

        assert result.profile.id == profile.id
        assert result.flow.id == "1"
        assert result.profile.traits['a'] == "###"
        assert result.event.properties["prop1"] == 5  # Events can not be changed



