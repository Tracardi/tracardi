from typing import List

from tracardi.process_engine.destination.connector import Connector
from ..action.v1.connectors.mautic.client import MauticClient, MauticClientAuthException
from tracardi.service.storage.driver import storage
from ...domain.event import Event
from ...domain.profile import Profile
from ...domain.session import Session


class MauticConnector(Connector):

    async def run(self, data, delta, profile: Profile, session: Session, events: List[Event]) -> None:

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

            await storage.driver.resource.save_record(self.resource)

