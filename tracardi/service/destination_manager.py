import asyncio
import logging
from uuid import uuid4

from tracardi.config import tracardi
from tracardi.domain.api_instance import ApiInstance
from tracardi.exceptions.log_handler import log_handler
from tracardi.process_engine.tql.condition import Condition
from tracardi.service.notation.dot_accessor import DotAccessor
from tracardi.service.notation.dict_traverser import DictTraverser
from tracardi.domain.destination import DestinationRecord, Destination
from tracardi.process_engine.destination.connector import Connector
from tracardi.service.module_loader import load_callable, import_package
from tracardi.service.postpone_call import PostponedCall
from tracardi.service.storage.driver import storage


logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


class DestinationManager:

    def __init__(self, delta, profile=None, session=None, payload=None, event=None, flow=None):
        self.dot = DotAccessor(profile, session, payload, event, flow)
        self.delta = delta
        self.profile = profile
        self.session = session

    @staticmethod
    async def _load_destinations():
        for destination in await storage.driver.destination.load_all():
            yield DestinationRecord(**destination).decode()

    @staticmethod
    def _get_class_and_module(package):
        parts = package.split(".")
        if len(parts) < 2:
            raise ValueError(f"Can not find class in package on {package}")
        return ".".join(parts[:-1]), parts[-1]

    async def send_data(self, profile_id, events, debug):

        template = DictTraverser(self.dot, default=None)

        async for destination in self._load_destinations():  # type: Destination
            module, class_name = self._get_class_and_module(destination.destination.package)
            module = import_package(module)
            destination_class = load_callable(module, class_name)

            # Load resource
            resource = await storage.driver.resource.load(destination.resource.id)

            if resource.enabled is False:
                raise ConnectionError(f"Can't connect to disabled resource: {resource.name}.")

            # Pass resource to destination class

            destination_instance = destination_class(debug, resource, destination)

            if isinstance(destination_instance, Connector):
                if destination.condition:
                    condition = Condition()
                    condition_result = await condition.evaluate(destination.condition, self.dot)
                    if not condition_result:
                        logger.info(f"Condition not met for destination {destination.name}. Data was not sent to "
                                    f"this destination.")
                        return

                result = template.reshape(reshape_template=destination.mapping)

                # Run postponed destination sync
                if tracardi.postpone_destination_sync > 0:
                    postponed_call = PostponedCall(
                        profile_id,
                        destination_instance.run,
                        ApiInstance().id,
                        result,  # *args
                        self.delta,
                        self.profile,
                        self.session,
                        events
                    )
                    postponed_call.wait = tracardi.postpone_destination_sync
                    postponed_call.run(asyncio.get_running_loop())
                else:
                    await destination_instance.run(result, self.delta, self.profile, self.session, events)
