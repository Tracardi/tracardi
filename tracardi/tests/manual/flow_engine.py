from pprint import pprint
from uuid import uuid4

from tracardi.domain.context import Context
from tracardi.domain.event import Event
from tracardi.domain.events import Events
from tracardi.domain.flow import FlowRecord
from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.profile import Profile
from tracardi.domain.rule import Rule
from tracardi.domain.session import Session
from tracardi.domain.type import Type
from tracardi.process_engine.rules_engine import RulesEngine
import asyncio


if __name__ == "__main__":
    async def main():
        source = NamedEntity(id="mobile-app", name="mobile-app")

        # Create profile, rule needs it
        p = Profile.new()
        await p.storage().save()
        profile = await p.storage().load()
        assert p.id == profile.id
        assert isinstance(profile, Profile)

        flow_record = FlowRecord(id="1", name="flow-1")
        await flow_record.storage().save()

        rule = Rule(
            id="string",
            source=source,
            name="my-rule",
            event=Type(type="xxx1"),
            flow=flow_record
        )
        await rule.storage().save()

        saved_rule = await rule.storage().load()
        assert saved_rule.id == rule.id
        x = await RulesEngine.load_rules("xxx2")
        pprint(x)

        payload = {
            "id": str(uuid4()),
            "event_server": Context(),
            "source": source.dict(),
            "profile": p.dict(),
            "context": {},
            "session": {"id": "0e6121a5-3ea0-45ed-a9ad-552e1765167f",
                        "event_server": {
                            "page": {"url": "http://localhost:8002/tracker/", "path": "/tracker/", "hash": "",
                                     "title": "My title",
                                     "referer": {"host": None, "query": None}, "history": {"length": 2}}},
                        },
            "properties": {"a": "tak"}, "type": "xxx1", "user": {"id": "user-id-2"}
        }

        event = Event(**payload)
        events = Events()
        events.append(event)
        events.append(event)
        session = Session(id="session-id")
        profile = Profile(id="profile-id")

        rules_engine = RulesEngine(
            session,
            profile,
            events)

        flow_result, segmentation_result = await rules_engine.execute(source.id)
        # print(stats.to_json())
        print(flow_result, segmentation_result)

        await rule.storage().delete()


    asyncio.run(main())
