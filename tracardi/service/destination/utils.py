from typing import List, AsyncGenerator, Optional

from tracardi.domain import ExtraInfo
from tracardi.domain.destination import Destination
from tracardi.domain.destination_work_package import DestinationWorkPackage

from tracardi.exceptions.log_handler import get_logger
from tracardi.service.cache.resource import load_resource_via_cache
from tracardi.service.notation.dict_traverser import DictTraverser

from tracardi.process_engine.tql.condition import Condition
from tracardi.service.notation.dot_accessor import DotAccessor
from tracardi.service.setup.setup_resources import get_resource_types

logger = get_logger(__name__)


async def _check_condition(query: str, dot) -> Optional[bool]:
    if query:
        condition = Condition()
        try:
            return await condition.evaluate(query, dot)
        except Exception as e:
            logger.warning(f"Query {query} cound not be parsed and returned error: {str(e)}.")
            return None
    # Return always true is not condition
    return True


async def get_destination_data(destinations: List[Destination], dot: DotAccessor) -> AsyncGenerator[
    DestinationWorkPackage, None]:
    if not destinations:
        return

    dict_traverser = DictTraverser(dot, default=None)

    for destination in destinations:

        if not destination.enabled:
            continue

        # Load resource from cache
        try:
            resource = await load_resource_via_cache(destination.resource.id)
            if resource is None:
                logger.warning(f"Destination `{destination.name}` not triggered. Missing resource.",
                               exc_info=ExtraInfo.exact('resource-loading', package=__name__))
                continue

            if resource.enabled is False:
                raise ConnectionError(f"Can't connect to disabled resource: {resource.name}.")

            is_condition_met = await _check_condition(destination.condition, dot)
            if is_condition_met is None:
                # Means some error
                logger.warning(f"Destination `{destination.name}` (id=\"{destination.id}\") not triggered. Reason: Not correct contition: {destination.condition}.")
                continue

            if is_condition_met:
                # Yield work package
                data = dict_traverser.reshape(reshape_template=destination.mapping)

                yield DestinationWorkPackage(destination=destination, resource=resource, data=data)

        except ValueError as e:
            logger.warning(f"Destination `{destination.name}` not triggered. Reason: {str(e)}",
                         exc_info=ExtraInfo.exact('resource-loading', package=__name__))
            continue




def get_destination_types():
    resource_types = get_resource_types()
    for resource_type in resource_types:
        if resource_type.destination is not None:
            yield resource_type.destination.package, resource_type.dict()
