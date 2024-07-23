import asyncio
from uuid import uuid4

from tracardi.context import Context, ServerContext
from tracardi.domain.entity import Entity
from tracardi.domain.event import Event
from tracardi.domain.event_metadata import EventMetadata
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.domain.session import Session
from tracardi.domain.time import EventTime
from tracardi.service.logger_manager import save_logs
from tracardi.service.wf.triggers import exec_workflow


with (ServerContext(Context(production=False))):
    async def main():
        profile_id = '1'
        source_id ="1147e557-afc4-4549-8453-6f505d04ee98"
        session = Session.new()
        tp = TrackerPayload(
            source=Entity(id=source_id),
            session=session
        )

        events = [
            Event(
                id=str(uuid4()),
                name="Page View",
                type="page-view",
                properties={
                    "a": 1
                },
                metadata=EventMetadata(time=EventTime()),
                source=Entity(id=source_id)
            )
        ]
        try:
            await exec_workflow(profile_id, session, events, tp)
        finally:
            await save_logs()

    asyncio.run(main())
