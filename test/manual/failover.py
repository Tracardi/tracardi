import asyncio
import logging

from time import sleep

from com_tracardi.service.tracking.queue.pulsar_queue import QueueWithFailOverPublisher
from com_tracardi.service.tracking.queue.pulsar_topics import EVENT_TOPIC, EVENT_FO
from tracardi.config import tracardi
from tracardi.context import Context
from tracardi.domain.entity import Entity
from tracardi.domain.event import Event
from tracardi.domain.event_metadata import EventMetadata
from tracardi.domain.time import EventTime
from tracardi.exceptions.log_handler import log_handler


logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


async def main():
    context = Context(production=True)
    manager = QueueWithFailOverPublisher.instance(EVENT_TOPIC, EVENT_FO, send_timeout_millis=1000)

    counter = 0
    while True:
        counter += 1

        events = [Event(
            id=str(counter),
            name="test",
            type="test",
            metadata=EventMetadata(time=EventTime()),
            source=Entity(id="1")
        ).model_dump()]

        message = ("workflow", {
            "payload": {},
            "profile": {},
            "session": {},
            "events": events
        })

        manager.send(message, context)
        sleep(.05)


asyncio.run(main())
