from kombu import Connection

from .destination_interface import DestinationInterface
from ...domain.event import Event
from ...domain.profile import Profile
from ...domain.session import Session
from ...service.rabbitmq.queue_config import QueueConfig
from ...service.rabbitmq.queue_publisher import QueuePublisher
from ...service.rabbitmq.rabbit_configuration import RabbitConfiguration


class RabbitMqConnector(DestinationInterface):

    async def _dispatch(self, data):

        credentials = self.resource.credentials.test if self.debug is True else self.resource.credentials.production
        configuration = RabbitConfiguration(**credentials)

        if 'queue' not in self.destination.destination.init:
            raise ValueError("Missing queue config.")

        settings = QueueConfig(**self.destination.destination.init['queue'])

        with Connection(configuration.uri, connect_timeout=configuration.timeout) as conn:
            queue_publisher = QueuePublisher(conn, queue_config=settings)
            queue_publisher.publish(data)

    async def dispatch_profile(self, data, profile: Profile, session: Session):
        await self._dispatch(data)

    async def dispatch_event(self, data, profile: Profile, session: Session, event: Event):
        await self._dispatch(data)
