import asyncio
import logging

from time import sleep

from com_tracardi.service.pulsar.fail_over_publisher import QueueWithFailOverPublisher
from com_tracardi.service.tracking.queue.pulsar_topics import EVENT_TOPIC
from tracardi.config import tracardi
from tracardi.context import Context
from tracardi.domain.entity import Entity
from tracardi.domain.event import Event
from tracardi.domain.event_metadata import EventMetadata
from tracardi.domain.time import EventTime
from tracardi.exceptions.log_handler import log_handler
from com_tracardi.service.pulsar.queue import pulsar_queue

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


async def main():
    context = Context(production=True)
    event_producer = pulsar_queue.produce(EVENT_TOPIC, send_timeout_millis=1000)  # How long to wait if no connection
    manager = QueueWithFailOverPublisher(event_producer, 'event-fail-over.db')
    manager.init(context)

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

        manager.send(events, context)
        sleep(.05)


asyncio.run(main())
