from typing import Optional, List

from tracardi.domain.destination import Destination
from tracardi.domain.event import Event
from tracardi.domain.profile import Profile
from tracardi.domain.resource import Resource
from tracardi.domain.session import Session


class DestinationInterface:

    def __init__(self, debug: bool, resource: Resource, destination: Destination):
        self.destination = destination
        self.debug = debug
        self.resource = resource

    async def dispatch_profile(self, data, profile: Profile, session: Optional[Session],
                               changed_fields: List[dict] = None, metadata=None):
        pass

    async def dispatch_event(self, data, profile: Optional[Profile], session: Optional[Session], event: Event,
                             metadata=None):
        pass

    def _get_credentials(self):
        return self.resource.credentials.test if self.debug else self.resource.credentials.production
