import logging
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


class GhostCredentials(BaseModel):
    api_url: str
    api_key: Optional[str] = None

class GhostConnector(DestinationInterface):

    def _dispatch(self, payload):
        try:
            credentials = self.resource.credentials.test if self.debug is True else self.resource.credentials.production
            credentials = GhostCredentials(**credentials)

            init = self.destination.destination.init

        except Exception as e:
            logger.error(str(e))
            raise e

    async def dispatch_profile(self, mapped_data, profile: Profile, session: Session):
        self._dispatch(payload=mapped_data)

    async def dispatch_event(self, mapped_data, profile: Profile, session: Session, event: Event):
        self._dispatch(payload=mapped_data)
