import asyncio
import logging
from collections import Callable
from typing import Any

from tracardi.domain.api_instance import ApiInstance
from tracardi.service.postpone_call import PostponedCall

from tracardi.domain.resource import Resource
from tracardi.exceptions.log_handler import log_handler
from tracardi.config import tracardi
from tracardi.process_engine.destination.event.event_destination import EventDestination
from tracardi.process_engine.tql.condition import Condition
from tracardi.service.destinations.destination_manager import get_destination_class
from tracardi.service.notation.dict_traverser import DictTraverser
from tracardi.service.cache_manager import CacheManager
from tracardi.domain.destination import DestinationRecord, Destination
from tracardi.service.notation.dot_accessor import DotAccessor
from tracardi.service.storage.driver import storage

cache = CacheManager()
logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


async def get_destination_dispatchers(destinations, dot, template):
    for destination in destinations:

        if not destination.enabled:
            continue

        # Load resource
        resource = await storage.driver.resource.load(destination.resource.id)

        if resource.enabled is False:
            raise ConnectionError(f"Can't connect to disabled resource: {resource.name}.")

        destination = destination.decode()
        data = template.reshape(reshape_template=destination.mapping)

        if destination.condition:
            condition = Condition()
            condition_result = await condition.evaluate(destination.condition, dot)
            if condition_result:
                yield destination, resource, data
        else:
            yield destination, resource, data


async def event_destination_dispatch(load_destination_task: Callable, profile, session, events, debug):
    dot = DotAccessor(profile, session)
    for ev in events:
        destinations = [DestinationRecord(**destination_record) for destination_record in
                        await load_destination_task(ev.type, ev.source.id, ttl=30)]

        dot.set_storage("event", ev)
        template = DictTraverser(dot, default=None)

        async for destination, resource, data in get_destination_dispatchers(
                destinations,
                dot,
                template):  # type: Destination, Resource, Any

            destination_class = get_destination_class(destination)
            destination_instance = destination_class(debug, resource, destination)

            print(isinstance(destination_instance, EventDestination), destination)
            if isinstance(destination_instance, EventDestination):
                reshaped_data = template.reshape(reshape_template=destination.mapping)

                await destination_instance.run(reshaped_data, profile, session, ev)


async def profile_destination_dispatch(load_destination_task: Callable,
                                       profile,
                                       session,
                                       events, profile_delta,
                                       debug):

    dot = DotAccessor(profile, session)
    template = DictTraverser(dot, default=None)

    destinations = [DestinationRecord(**destination_record) for destination_record in
                    await load_destination_task(ttl=30)]

    async for destination, resource, data in get_destination_dispatchers(
                destinations,
                dot,
                template):  # type: Destination, Resource, Any

        destination_class = get_destination_class(destination)
        destination_instance = destination_class(debug, resource, destination)

        # Run postponed destination sync
        if tracardi.postpone_destination_sync > 0:
            postponed_call = PostponedCall(
                profile.id,
                destination_instance.run,
                ApiInstance().id,
                data,  # *args
                profile_delta,
                profile,
                session,
                events
            )
            postponed_call.wait = tracardi.postpone_destination_sync
            postponed_call.run(asyncio.get_running_loop())
        else:
            await destination_instance.run(data, profile_delta, profile, session, events)
