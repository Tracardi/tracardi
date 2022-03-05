from tracardi.process_engine.destination.connector import Connector
from ..action.v1.connectors.mautic.client import MauticClient, MauticClientAuthException
from tracardi.service.storage.driver import storage


class MauticConnector(Connector):

    async def run(self, data, delta) -> None:

        if "email" not in data:
            raise ValueError("Given mapping must contain email.")

        credentials = self.resource.credentials.test if self.debug else self.resource.credentials.production

        client = MauticClient(**credentials)

        try:
            await client.add_contact(
                data["email"],
                self.destination.destination.init["overwrite_with_blank"],
                **data
            )

        except MauticClientAuthException:
            await client.update_token()
            await client.add_contact(
                data["email"],
                self.destination.destination.init["overwrite_with_blank"],
                **data
            )

            if self.debug:
                self.resource.credentials.test = client.credentials
            else:
                self.resource.credentials.production = client.credentials

            await storage.driver.resource.save_record(self.resource)

