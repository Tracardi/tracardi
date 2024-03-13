from typing import List, Any

from tracardi.domain.destination import Destination
from tracardi.domain.resource import Resource
from tracardi.process_engine.destination.destination_interface import DestinationInterface
from tracardi.exceptions.log_handler import get_logger
from tracardi.service.cache.resource import load_resource
from tracardi.service.notation.dict_traverser import DictTraverser
from tracardi.service.module_loader import load_callable, import_package
from tracardi.process_engine.tql.condition import Condition
from tracardi.service.notation.dot_accessor import DotAccessor

logger = get_logger(__name__)


def _get_class_and_module(package):
    parts = package.split(".")
    if len(parts) < 2:
        raise ValueError(f"Can not find class in package on {package}")
    return ".".join(parts[:-1]), parts[-1]


def _get_destination_class(destination: Destination):
    module, class_name = _get_class_and_module(destination.destination.package)
    module = import_package(module)
    return load_callable(module, class_name)


async def _get_destination_dispatchers(destinations: List[Destination], dot, template):
    for destination in destinations:

        if not destination.enabled:
            continue

        # Load resource from cache
        resource = await load_resource(destination.resource.id)

        if resource.enabled is False:
            raise ConnectionError(f"Can't connect to disabled resource: {resource.name}.")

        data = template.reshape(reshape_template=destination.mapping)

        if destination.condition:
            condition = Condition()
            condition_result = await condition.evaluate(destination.condition, dot)
            if condition_result:
                yield destination, resource, data
        else:
            yield destination, resource, data


async def get_dispatch_destination_and_data(
        dot: DotAccessor,
        destinations: List[Destination],
        debug: bool):

    template = DictTraverser(dot, default=None)

    async for destination, resource, data in _get_destination_dispatchers(destinations,
                                                                          dot,
                                                                          template):  # type: Destination, Resource, Any

        destination_class = _get_destination_class(destination)
        destination_instance = destination_class(debug, resource, destination)  # type: DestinationInterface
        reshaped_data = template.reshape(reshape_template=destination.mapping)

        return destination_instance, reshaped_data

    return None