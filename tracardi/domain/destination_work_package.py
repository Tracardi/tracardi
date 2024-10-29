from typing import Optional

from pydantic import BaseModel

from tracardi.domain.destination import Destination
from tracardi.domain.resource import Resource
from tracardi.process_engine.destination.destination_interface import DestinationInterface


class DestinationWorkPackage(BaseModel):
    destination: Destination
    resource: Resource
    data: Optional[dict] = {}

    def get_destination_instance(self, debug) -> DestinationInterface:
        destination_class = self.destination.get_destination_class()
        return destination_class(debug, self.resource, self.destination)
