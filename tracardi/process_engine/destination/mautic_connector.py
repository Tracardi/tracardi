from typing import List

from tracardi.service.domain import resource as resource_db
from .destination_interface import DestinationInterface
from ..action.v1.connectors.mautic.client import MauticClient, MauticClientAuthException
from ...domain.event import Event
from ...domain.profile import Profile
from ...domain.session import Session


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

    async def dispatch_profile(self, data, profile: Profile, session: Session, changed_fields: List[dict] = None,
                               metadata=None):
        await self._dispatch(data)

    async def dispatch_event(self, data, profile: Profile, session: Session, event: Event, metadata=None):
        await self._dispatch(data)
