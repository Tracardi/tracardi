from typing import List

from tracardi.domain.destination import Destination
from tracardi.domain.event import Event
from tracardi.domain.profile import Profile
from tracardi.domain.resource import Resource
from tracardi.domain.session import Session


class Connector:

    def __init__(self, debug: bool, resource: Resource, destination: Destination):
        self.destination = destination
        self.debug = debug
        self.resource = resource

    async def run(self, data, delta, profile: Profile, session: Session, events: List[Event]):
        pass
