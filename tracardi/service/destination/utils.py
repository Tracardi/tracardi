from typing import List, AsyncGenerator

from tracardi.domain import ExtraInfo
from tracardi.domain.destination import Destination
from tracardi.domain.destination_work_package import DestinationWorkPackage

from tracardi.common.logging.log_handler import get_logger
from tracardi.common.dot_notation.dict_traverser import DictTraverser

from tracardi.process_engine.tql.condition import Condition
from tracardi.common.dot_notation.dot_accessor import DotAccessor
from tracardi.service.setup.setup_resources import get_resource_types

from tracardi.service.storage.mysql.interface import resource_dao

logger = get_logger(__name__)


async def _check_condition(query: str, dot) -> bool:
    if query:
        condition = Condition()
        return await condition.evaluate(query, dot)
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
            resource = await resource_dao.load_resource_via_cache(destination.resource.id)
            if resource.enabled is False:
                raise ConnectionError(f"Can't connect to disabled resource: {resource.name}.")

            if await _check_condition(destination.condition, dot):
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
