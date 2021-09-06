import asyncio

from tracardi.domain.record.flow_action_plugin_record import FlowActionPluginRecord

from tracardi.domain.record.event_debug_record import EventDebugRecord

from tracardi.domain.segment import Segment

from tracardi.domain.named_entity import NamedEntity

from tracardi.domain.type import Type

from tracardi.domain.rule import Rule

from tracardi.process_engine.action.v1.start_action import StartAction, register

from tracardi.domain.flow_action_plugin import FlowActionPlugin

from tracardi.domain.flow import Flow

from tracardi.domain.context import Context

from tracardi.domain.event import Event

from tracardi.domain.profile import Profile
from tracardi.domain.resource import Resource, ResourceRecord
from tracardi.domain.session import Session
from tracardi.service.storage.factory import storage


def test_storage():
    objects = [
        Session(id="1"),
        Profile(id="1"),
        # Console(event_id="1", flow_id="1", origin="origin", type="type", class_name="classname", module="module", message="message")
        # Entity,
        Event(id="1", type="test-event", source=Resource(id="1", type="test"), session=Session(id="1"),
              context=Context()),
        Flow(**{
            "id": "1",
            "name": "name",
            "description": "desc",
            "enabled": True,
            "projects": [
                "General", "Test"
            ],
            "draft": "",
            "lock": False
        }),
        FlowActionPlugin(id="1", plugin=register()),  #todo may not be allowed without encoding
        # Resource(id="2", type="test"),  # todo moze nie byc wymagane
        ResourceRecord(id="2", type="test"),
        Rule(id="1", name="rule", event=Type(type="type"), flow=NamedEntity(id="1", name="flow")),
        Segment(id="1", name="segment", condition="a>1"),  #todo segment needs validation on condition
        EventDebugRecord(id="1", content="abc"),
        FlowActionPluginRecord.encode(FlowActionPlugin(id="2", plugin=register())),
    ]

    loop = asyncio.get_event_loop()
    for instance in objects:
        db = storage(instance)
        print(db.domain_class_ref)

        async def main():
            result = await db.save()
            assert result.saved == 1
            result = await db.load()
            assert isinstance(result, db.domain_class_ref)
            # result = await db.delete()
            # print(result)

        loop.run_until_complete(main())
    loop.close()
