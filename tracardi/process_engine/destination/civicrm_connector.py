from typing import Optional, List

from .destination_interface import DestinationInterface
from ..action.v1.connectors.civi_crm.client import CiviCRMClient, CiviClientCredentials
from tracardi.domain.flat_profile import FlatProfile
from ...domain.flat_event import FlatEvent
from ...domain.session import Session


class CiviCRMConnector(DestinationInterface):

    async def _dispatch(self, data):
        if "id" not in data or "email" not in data:
            raise ValueError("Given fields mapping must contain \"id\" and \"email\" keys.")

        credentials = self.resource.credentials.test if self.debug else self.resource.credentials.production

        client = CiviCRMClient(**CiviClientCredentials(**credentials).model_dump())

        await client.add_contact(data)

    async def dispatch_profile(self, data, flat_profile: Optional[FlatProfile], session: Optional[Session],
                               changed_fields: List[dict] = None, metadata=None):
        await self._dispatch(data)

    async def dispatch_event(self, data, flat_profile: Optional[FlatProfile], session: Optional[Session], flat_event: FlatEvent,
                             metadata=None):
        await self._dispatch(data)
