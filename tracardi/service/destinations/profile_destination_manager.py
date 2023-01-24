from tracardi.service.cache_manager import CacheManager
from tracardi.service.destinations.destination_manager import DestinationManager
from tracardi.domain.destination import DestinationRecord

cache = CacheManager()


class ProfileDestinationManager(DestinationManager):

    @staticmethod
    async def load_destinations_as_destination_records():
        for destination in await cache.profile_destinations(ttl=30):
            yield DestinationRecord(**destination).decode()

    async def send_data(self, profile_id, events, profile_delta, debug):
        destinations = [destination async for destination in self.load_destinations_as_destination_records()]
        return await self.send_data_to_destinations(destinations, profile_id, events, profile_delta, debug)
