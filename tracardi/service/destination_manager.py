import asyncio

from tracardi.service.notation.dot_accessor import DotAccessor
from tracardi.service.notation.dict_traverser import DictTraverser
from tracardi.domain.destination import DestinationRecord
from tracardi.process_engine.destination.connector import Connector
from tracardi.service.module_loader import load_callable, import_package
from tracardi.service.storage.driver import storage


class DestinationManager:

    def __init__(self, delta, profile=None, session=None, payload=None, event=None, flow=None):
        self.dot = DotAccessor(profile, session, payload, event, flow)
        self.delta = delta

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

    async def send_data(self):

        template = DictTraverser(self.dot)

        async for destination in self._load_destinations():
            module, class_name = self._get_class_and_module(destination.package)
            module = import_package(module)
            destination_class = load_callable(module, class_name)
            destination_instance = destination_class(destination.config)
            if isinstance(destination_instance, Connector):
                result = template.reshape(reshape_template=destination.mapping)
                asyncio.create_task(destination_instance.run(result, self.delta))
