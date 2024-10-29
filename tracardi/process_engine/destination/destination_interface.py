from typing import Optional, List

from tracardi.domain.destination import Destination
from tracardi.domain.flat_event import FlatEvent
from tracardi.domain.flat_profile import FlatProfile
from tracardi.domain.resource import Resource


class DestinationInterface:

    def __init__(self, debug: bool, resource: Resource, destination: Destination):
        self.destination = destination
        self.debug = debug
        self.resource = resource

    async def dispatch_profile(self, data, flat_profile: Optional[FlatProfile],
                               changed_fields: List[dict] = None, metadata=None):
        pass

    async def dispatch_event(self, data, flat_event: FlatEvent, metadata=None, profile_id: Optional[str] = None, session_id: Optional[str] = None):
        pass

    def _get_credentials(self):
        return self.resource.credentials.test if self.debug else self.resource.credentials.production
