from typing import Protocol


class PubSubProtocol(Protocol):

    def publish(self, channel, payload):
        pass

    def subscribe(self, channel):
        pass