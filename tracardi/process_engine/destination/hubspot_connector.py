from .destination_interface import DestinationInterface
from ..action.v1.connectors.hubspot.client import HubSpotClient, HubSpotClientException
from ...domain.event import Event
from ...domain.profile import Profile
from ...domain.session import Session
from ...exceptions.log_handler import get_logger
from ...service.integration_id import load_integration_id, save_integration_id

logger = get_logger(__name__)


class HubSpotConnector(DestinationInterface):
    name = 'hubspot'

    async def _dispatch(self, data, profile: Profile):  # Data comes from mapping

        credentials = self._get_credentials()
        client = HubSpotClient(credentials.get('token', None))

        payload = {}
        if profile.data.pii.firstname:
            payload["firstname"] = profile.data.pii.firstname
        if profile.data.pii.firstname:
            payload["lastname"] = profile.data.pii.lastname
        if profile.data.contact.email.main:
            payload["email"] = profile.data.contact.email.main

        # If there is any data to send
        logger.info(f"Prepared data payload {payload}")

        if not payload:
            logger.info(f"No update in hubspot data is empty for profile {profile.id}.")
            return

        integration_ids = await load_integration_id(profile.id, self.name)

        if integration_ids:

            logger.info(f"Found hubspot integration data {integration_ids}")

            # Get first
            integration = integration_ids[0]

            remotes_id = integration.get_first_id()

            if remotes_id is None:
                response = await client.add_contact(payload)
                logger.info(f"Adding contact to hubspot with data {payload}; response {response}")
                if 'id' in response:
                    print(await save_integration_id(profile.id, self.name, response['id'], {}))
            else:
                # If data changed
                try:
                    response = await client.update_contact(integration.get_first_id(), payload)
                    logger.info(f"Updating in hubspot with data {payload}; response {response}")
                except HubSpotClientException as e:
                    logger.warning(str(e))
                print(await save_integration_id(profile.id, self.name, integration.id, {}))

        else:
            try:
                response = await client.add_contact(payload)

                logger.info(f"Adding contact to hubspot with data {payload}; response {response}")

                if 'id' in response:
                    print(await save_integration_id(profile.id, self.name, response['id'], {}))
            except HubSpotClientException:
                if 'email' in payload:
                    ids = await client.get_contact_ids_by_email(payload["email"])
                    if len(ids) > 0:
                        await save_integration_id(profile.id, self.name, ids[0], {})

    async def dispatch_profile(self, data, profile: Profile, session: Session):
        await self._dispatch(data, profile)

    async def dispatch_event(self, data, profile: Profile, session: Session, event: Event):
        await self._dispatch(data, profile)
