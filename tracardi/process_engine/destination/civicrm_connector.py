from tracardi.process_engine.destination.connector import Connector
from ..action.v1.connectors.civi_crm.client import CiviCRMClient, CiviClientCredentials


class CiviCRMConnector(Connector):

    async def run(self, data, delta) -> None:

        if "id" not in data or "email" not in data:
            raise ValueError("Given fields mapping must contain \"id\" and \"email\" keys.")

        credentials = self.resource.credentials.test if self.debug else self.resource.credentials.production

        client = CiviCRMClient(**CiviClientCredentials(**credentials).dict())

        await client.add_contact(data)


