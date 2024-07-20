from typing import Optional, List

from pydantic import BaseModel

from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.exceptions.log_handler import get_logger
from .destination_interface import DestinationInterface
from ...domain.event import Event

logger = get_logger(__name__)


class GhostCredentials(BaseModel):
    api_url: str
    api_key: Optional[str] = None


class GhostConnector(DestinationInterface):

    def _dispatch(self, payload):
        try:
            credentials = self.resource.credentials.test if self.debug is True else self.resource.credentials.production
            credentials = GhostCredentials(**credentials)

            init = self.destination.destination.init

            # TODO Finish.

        except Exception as e:
            logger.error(str(e))
            raise e

    async def dispatch_profile(self, mapped_data, profile: Profile, session: Session, changed_fields: List[dict] = None,
                               metadata=None):
        self._dispatch(payload=mapped_data)

    async def dispatch_event(self, mapped_data, profile: Profile, session: Session, event: Event, metadata=None):
        self._dispatch(payload=mapped_data)
