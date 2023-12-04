import json

import pickle

import logging
import pulsar
from typing import Optional

from pydantic import BaseModel

from tracardi.config import tracardi
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.exceptions.log_handler import log_handler
from .destination_interface import DestinationInterface
from ...domain.event import Event

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


class PulsarCredentials(BaseModel):
    host: str  # AnyHttpUrl
    token: Optional[str] = None

class PulsarTopicConfiguration(BaseModel):
    topic: str
    serializer:str ='json'

class PulsarConnector(DestinationInterface):

    def _dispatch(self, payload):
        try:
            credentials = self.resource.credentials.test if self.debug is True else self.resource.credentials.production
            credentials = PulsarCredentials(**credentials)

            init = self.destination.destination.init
            config = PulsarTopicConfiguration(**init)

            # use credentials and config to setup Apache pulsar client
            if credentials.token:
                client = pulsar.Client(
                    credentials.host,
                    authentication=pulsar.AuthenticationToken(credentials.token)
                )
            else:
                client = pulsar.Client(
                    credentials.host
                )

            producer = client.create_producer(config.topic)

            if config.serializer == 'pickle':
                payload = pickle.dumps(payload)

            elif config.serializer == 'json':
                payload = json.dumps(
                    payload,
                    default=str
                ).encode('utf-8')

            id = producer.send(payload)

        except Exception as e:
            logger.error(str(e))
            raise e


    async def dispatch_profile(self, mapped_data, profile: Profile, session: Session):
        self._dispatch(payload=mapped_data)

    async def dispatch_event(self, mapped_data, profile: Profile, session: Session, event: Event):
        self._dispatch(payload=mapped_data)
