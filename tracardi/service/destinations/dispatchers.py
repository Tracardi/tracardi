from collections.abc import Callable
from typing import Any, Optional, List

from tracardi.domain.entity import Entity
from tracardi.domain.event import Event
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.process_engine.destination.destination_interface import DestinationInterface
from tracardi.service.license import License
from tracardi.service.module_loader import load_callable, import_package
from tracardi.domain.resource import Resource
from tracardi.exceptions.log_handler import get_logger
from tracardi.config import memory_cache
from tracardi.process_engine.tql.condition import Condition
from tracardi.service.notation.dict_traverser import DictTraverser
from tracardi.service.cache_manager import CacheManager
from tracardi.domain.destination import DestinationRecord, Destination
from tracardi.service.notation.dot_accessor import DotAccessor
from tracardi.service.storage.driver.elastic import resource as resource_db

logger = get_logger(__name__)
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
        # todo cache
        resource = await resource_db.load(destination.resource.id)

        if resource.enabled is False:
            raise ConnectionError(f"Can't connect to disabled resource: {resource.name}.")

        if resource.is_destination_pro() and not License.has_license():
            continue

        destination = destination.decode()
        data = template.reshape(reshape_template=destination.mapping)

        if destination.condition:
            condition = Condition()
            condition_result = await condition.evaluate(destination.condition, dot)
            if condition_result:
                yield destination, resource, data
        else:
            yield destination, resource, data


async def event_destination_dispatch(load_destination_task: Callable,
                                     profile: Optional[Profile],
                                     session: Optional[Session],
                                     events: List[Event],
                                     debug):

    dot = DotAccessor(profile, session)
    for ev in events:
        destinations = [DestinationRecord(**destination_record) for destination_record in
                        await load_destination_task(ev.type,
                                                    ev.source.id,
                                                    ttl=memory_cache.event_destination_cache_ttl)]

        dot.set_storage("event", ev)

        template = DictTraverser(dot, default=None)

        async for destination, resource, data in _get_destination_dispatchers(
                destinations,
                dot,
                template):  # type: Destination, Resource, Any

            destination_class = _get_destination_class(destination)
            destination_instance = destination_class(debug, resource, destination)  # type: DestinationInterface
            reshaped_data = template.reshape(reshape_template=destination.mapping)

            if session is None:
                logger.warning(f"Dispatching event without session. New session created.")
                session = Session.new()
                if profile:
                    session.profile = Entity(id=profile.id)

            logger.info(f"Dispatching event with destination class {destination_class}.")
            try:
                await destination_instance.dispatch_event(reshaped_data, profile=profile, session=session, event=ev)
            except Exception as e:
                logger.error(str(e))

async def profile_destination_dispatch(load_destination_task: Callable,
                                       profile,
                                       session,
                                       debug):

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

        logger.info(f"Dispatching profile with destination class {destination_class}.")
        await destination_instance.dispatch_profile(data, profile, session)
