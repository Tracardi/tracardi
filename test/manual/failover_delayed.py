from datetime import timedelta

import asyncio

from com_tracardi.service.tracking.queue.pulsar_queue import QueueWithFailOverPublisher
from com_tracardi.service.tracking.queue.pulsar_topics import EVENT_TOPIC, EVENT_FO
from tracardi.context import Context
from tracardi.exceptions.log_handler import get_logger

logger = get_logger(__name__)


async def main():
    context = Context(production=True)
    manager = QueueWithFailOverPublisher.instance(EVENT_TOPIC, EVENT_FO, send_timeout_millis=1000)

    message = ("workflow", {
        "payload": {},
        "profile": {},
        "session": {},
        "events": {}
    })

    manager.send(message, context, options=dict(
        deliver_after = timedelta(seconds=15)
    ))


asyncio.run(main())
