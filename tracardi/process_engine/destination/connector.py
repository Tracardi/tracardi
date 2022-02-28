from tracardi.domain.destination import Destination
from tracardi.domain.resource import Resource


class Connector:

    def __init__(self, debug: bool, resource: Resource, destination: Destination):
        self.destination = destination
        self.debug = debug
        self.resource = resource

    async def run(self, data, delta):
        pass
