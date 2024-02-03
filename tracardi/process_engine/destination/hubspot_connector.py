from hashlib import sha1

from .destination_interface import DestinationInterface
from ..action.v1.connectors.hubspot.client import HubSpotClient, HubSpotClientException
from ...domain.event import Event
from ...domain.profile import Profile
from ...domain.session import Session
from ...exceptions.log_handler import get_logger

logger= get_logger(__name__)

class HubSpotConnector(DestinationInterface):

    name = 'hubspot'

    @staticmethod
    def _get_hash_of_values(data):
        return sha1(
            f"{data.get('firstname', 'none')}-{data.get('lastname', 'none')}-{data.get('email', 'none')}".encode()).hexdigest()

    async def _dispatch(self, data, profile: Profile):  # Data comes from mapping

        logger.info(f"Destination for {profile.id}.")

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

        new_hash = self._get_hash_of_values(payload)

        if profile.metadata.system.has_integration(self.name):
            integration = profile.metadata.system.get_integration(self.name)

            old_hash = integration.data.get('hash', None)

            # If data changed
            if old_hash != new_hash:
                response = await client.update_contact(integration.id, payload)

                # Update hash
                profile.metadata.system.set_integration(self.name, integration.id, {"hash": new_hash})
                profile.mark_for_update()

                logger.info(f"Updating in hubspot with data {payload}; response {response}")

        else:
            try:
                response = await client.add_contact(payload)

                logger.info(f"Adding contact to hubspot with data {payload}; response {response}")

                if 'id' in response:
                    profile.metadata.system.set_integration(self.name, response['id'], {"hash": new_hash})
                    profile.mark_for_update()
            except HubSpotClientException:
                if 'email' in payload:
                    ids = await client.get_contact_ids_by_email(payload["email"])
                    if len(ids) > 0:
                        profile.metadata.system.set_integration(self.name, ids[0], {"hash": new_hash})
                        profile.mark_for_update()
    async def dispatch_profile(self, data, profile: Profile, session: Session):
        await self._dispatch(data, profile)

    async def dispatch_event(self, data, profile: Profile, session: Session, event: Event):
        await self._dispatch(data, profile)
