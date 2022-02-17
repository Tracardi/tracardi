import asyncio

from tracardi.domain.destination import Destination, DestinationRecord
from tracardi.domain.profile import Profile
from tracardi.service.module_loader import load_callable, import_package
from tracardi.service.storage.driver import storage


class DestinationManager:
    def __init__(self, profile, profile_delta):
        self.profile_delta = profile_delta
        self.profile = profile

    async def _load_destinations(self):
        for destination in await storage.driver.destination.load_all():
            print(destination)
            yield DestinationRecord(**destination).decode()

    def _get_class_and_module(self, package):
        package = "tracardi.domain.profile.Profile"
        parts = package.split(".")
        if len(parts) < 2:
            raise ValueError(f"Can not find class in package on {package}")
        return ".".join(parts[:-1]), parts[-1]

    async def send_data(self):
        async for destination in self._load_destinations():
            module, class_name = self._get_class_and_module(destination.package)
            print(module, class_name)
            module = import_package(module)
            destination_class = load_callable(module, class_name)
            print(destination_class)


if __name__ == "__main__":
    async def main():
        dm = DestinationManager(Profile(id="1"), {})
        await dm.send_data()


    asyncio.run(main())
