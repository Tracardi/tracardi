import asyncio
import logging
from collections.abc import Callable
from typing import Any

from tracardi.domain.api_instance import ApiInstance
from tracardi.process_engine.destination.destination_interface import DestinationInterface
from tracardi.service.postpone_call import PostponedCall
from tracardi.service.module_loader import load_callable, import_package
from tracardi.domain.resource import Resource
from tracardi.exceptions.log_handler import log_handler
from tracardi.config import tracardi, memory_cache
from tracardi.process_engine.tql.condition import Condition
from tracardi.service.notation.dict_traverser import DictTraverser
from tracardi.service.cache_manager import CacheManager
from tracardi.domain.destination import DestinationRecord, Destination
from tracardi.service.notation.dot_accessor import DotAccessor
from tracardi.service.storage.driver.elastic import resource as resource_db

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)
cache = CacheManager()


def _get_class_and_module(package):
    parts = package.split(".")
    if len(parts) < 2:
        raise ValueError(f"Can not find class in package on {package}")
    return ".".join(parts[:-1]), parts[-1]


def _get_destination_class(destination: Destination):
    module, class_name = _get_class_and_module(destination.destination.package)
    module = import_package(module)
    return load_callable(module, class_name)


async def _get_destination_dispatchers(destinations, dot, template):
    for destination in destinations:

        if not destination.enabled:
            continue

        # Load resource
        resource = await resource_db.load(destination.resource.id)

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
    logger.info("Dispatching events via event destination.")
    dot = DotAccessor(profile, session)
    for ev in events:
        destinations = [DestinationRecord(**destination_record) for destination_record in
                        await load_destination_task(ev.type, ev.source.id,
                                                    ttl=memory_cache.event_destination_cache_ttl)]

        dot.set_storage("event", ev)

        template = DictTraverser(dot, default=None)

        async for destination, resource, data in _get_destination_dispatchers(
                destinations,
                dot,
                template):  # type: Destination, Resource, Any

            destination_class = _get_destination_class(destination)
            destination_instance = destination_class(debug, resource, destination)  # type: DestinationInterface
            logger.info(f"Event destination class {destination_class}.")

            reshaped_data = template.reshape(reshape_template=destination.mapping)
            await destination_instance.dispatch_event(reshaped_data, profile=profile, session=session, event=ev)


async def profile_destination_dispatch(load_destination_task: Callable,
                                       profile,
                                       session,
                                       debug):
    logger.info("Dispatching profile via profile destination.")

    dot = DotAccessor(profile, session)
    template = DictTraverser(dot, default=None)

    destinations = [DestinationRecord(**destination_record) for destination_record in
                    await load_destination_task(ttl=memory_cache.profile_destination_cache_ttl)]

    async for destination, resource, data in _get_destination_dispatchers(
                destinations,
                dot,
                template):  # type: Destination, Resource, Any

        destination_class = _get_destination_class(destination)
        destination_instance = destination_class(debug, resource, destination)  # type: DestinationInterface

        # Run postponed destination sync
        if tracardi.postpone_destination_sync > 0:
            postponed_call = PostponedCall(
                profile.id,
                destination_instance.dispatch_profile,
                ApiInstance().id,
                data,  # *args
                profile,
                session
            )
            postponed_call.wait = tracardi.postpone_destination_sync
            postponed_call.run(asyncio.get_running_loop())
        else:
            await destination_instance.dispatch_profile(data, profile, session)
