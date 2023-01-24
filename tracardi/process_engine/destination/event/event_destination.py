from tracardi.domain.destination import Destination
from tracardi.domain.event import Event
from tracardi.domain.profile import Profile
from tracardi.domain.resource import Resource
from tracardi.domain.session import Session


class EventDestination:

    def __init__(self, debug: bool, resource: Resource, destination: Destination):
        self.destination = destination
        self.resource = resource
        self.debug = debug

    async def run(self, data, profile: Profile, session: Session, event: Event):
        pass
