from typing import List, Optional

from tracardi.service.domain import resource as resource_db
from .destination_interface import DestinationInterface
from ..action.v1.connectors.mautic.client import MauticClient, MauticClientAuthException
from tracardi.domain.flat_profile import FlatProfile
from ...domain.flat_event import FlatEvent


class MauticConnector(DestinationInterface):

    async def _dispatch(self, data):

        if "email" not in data:
            raise ValueError("Given mapping must contain email.")

        credentials = self.resource.credentials.test if self.debug else self.resource.credentials.production

        client = MauticClient(**credentials)

        try:
            await client.add_contact(
                data["email"],
                self.destination.destination.init["overwrite_with_blank"],
                **{key: value for key, value in data.items() if key not in ("overwrite_with_blank", "email")}
            )

        except MauticClientAuthException:
            await client.update_token()
            await client.add_contact(
                data["email"],
                self.destination.destination.init["overwrite_with_blank"],
                **{key: value for key, value in data.items() if key not in ("overwrite_with_blank", "email")}
            )

            if self.debug:
                self.resource.credentials.test = client.credentials
            else:
                self.resource.credentials.production = client.credentials

            await resource_db.save_record(self.resource)

    async def dispatch_profile(self, data, flat_profile: Optional[FlatProfile],
                               changed_fields: List[dict] = None,
                               metadata=None):
        await self._dispatch(data)

    async def dispatch_event(self, data, flat_event: FlatEvent, metadata=None, profile_id: Optional[str] = None, session_id: Optional[str] = None):
        await self._dispatch(data)
