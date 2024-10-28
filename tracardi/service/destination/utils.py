from typing import List, Any

from tracardi.domain import ExtraInfo
from tracardi.domain.destination import Destination
from tracardi.domain.resource import Resource
from tracardi.process_engine.destination.destination_interface import DestinationInterface
from tracardi.exceptions.log_handler import get_logger
from tracardi.service.cache.resource import load_resource_via_cache
from tracardi.service.notation.dict_traverser import DictTraverser
from tracardi.service.module_loader import load_callable, import_package
from tracardi.process_engine.tql.condition import Condition
from tracardi.service.notation.dot_accessor import DotAccessor
from tracardi.service.setup.setup_resources import get_resource_types

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

async def _check_condition(condition, dot) ->bool:
    if condition:
        condition = Condition()
        return await condition.evaluate(condition, dot)
    # Return always true is not condition
    return True

async def _get_destination_and_resource(destinations: List[Destination], dot: DotAccessor):

    for destination in destinations:

        if not destination.enabled:
            continue

        # Load resource from cache
        try:
            resource = await load_resource_via_cache(destination.resource.id)
            if resource.enabled is False:
                raise ConnectionError(f"Can't connect to disabled resource: {resource.name}.")

        except ValueError as e:
            logger.error(f"Destination `{destination.name}` not triggered. Reason: {str(e)}", exc_info=ExtraInfo.exact('resource-loading', package=__name__))
            continue

        yield destination, resource


async def get_dispatch_destination_and_data(
        dot: DotAccessor,
        destinations: List[Destination],
        debug: bool):

    if not destinations:
        return

    dict_traverser = DictTraverser(dot, default=None)

    async for destination, resource in _get_destination_and_resource(destinations,
                                                                          dot):  # type: Destination, Resource, Any
        if await _check_condition(destination.condition, dot):
            destination_class = _get_destination_class(destination)
            destination_instance = destination_class(debug, resource, destination)  # type: DestinationInterface
            yield destination_instance, dict_traverser.reshape(reshape_template=destination.mapping)


def get_destination_types():
    resource_types = get_resource_types()
    for resource_type in resource_types:
        if resource_type.destination is not None:
            yield resource_type.destination.package, resource_type.dict()
