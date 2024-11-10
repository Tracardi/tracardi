from typing import List, Optional

from .destination_interface import DestinationInterface
from ..action.v1.connectors.hubspot.client import HubSpotClient, HubSpotClientException
from ...domain.destination import Destination
from tracardi.domain.flat_profile import FlatProfile
from ...domain.flat_event import FlatEvent
from ...domain.resource import Resource
from ...exceptions.log_handler import get_logger
from tracardi.service.storage.elastic.interface.integration_id import load_integration_id, save_integration_id

logger = get_logger(__name__)


class HubSpotConnector(DestinationInterface):
    name = 'hubspot'

    def __init__(self, debug: bool, resource: Resource, destination: Destination):
        super().__init__(debug, resource, destination)
        credentials = self._get_credentials()
        self.client = HubSpotClient(credentials.get('token', None))

    async def _update_contact(self, payload: dict, profile_id: str, hubspot_id):
        try:
            logger.info(f"Updating in hubspot with data {payload} for remote ID {hubspot_id}")
            response = await self.client.update_contact(hubspot_id, payload)
            logger.info(f"Updated data {payload} in hubspot; response {response}")
            print(await save_integration_id(profile_id, self.name, hubspot_id, {}))

        except HubSpotClientException as e:
            # Record deleted
            logger.warning(str(e))
            await self._add_contact(payload, profile_id)

    async def _add_contact(self, payload: dict, profile_id: str):
        hubspot_id = None
        try:
            logger.info(f"Adding contact to hubspot with data {payload}")
            response = await self.client.add_contact(payload)
            logger.info(f"Added contact to hubspot with data {payload}; response {response}")

            if 'id' in response:
                hubspot_id = response['id']

        except HubSpotClientException:

            # Contact already exists
            ids = await self.client.get_contact_ids_by_email(payload["email"])
            logger.info(f"Found contact to hubspot {ids}")
            if len(ids) > 0:
                hubspot_id = ids[0]

        finally:
            if hubspot_id:
                logger.info(f"Updating hubspot integration with {hubspot_id}")
                print(await save_integration_id(profile_id, self.name, hubspot_id, {}))

    @staticmethod
    def _prepare_payload(flat_profile: FlatProfile, config_data):
        payload = {}
        if flat_profile.has('data.pii.firstname'):
            payload["firstname"] = flat_profile['data.pii.firstname']
        if flat_profile.has('data.pii.firstname'):
            payload["lastname"] = flat_profile['data.pii.lastname']
        if flat_profile.has('data.contact.email.main'):
            payload["email"] = flat_profile['data.contact.email.main']
        if flat_profile.has('data.contact.phone.main'):
            payload["phone"] = flat_profile['data.contact.phone.main']
        # if profile.data.job.company:
        #     payload["company"] = profile.data.job.company
        # if profile.data.contact.address.town:
        #     payload["city"] = profile.data.contact.address.town
        # if profile.data.contact.address.county:
        #     payload["state"] = profile.data.contact.address.county
        # if profile.data.contact.address.postcode:
        #     payload["zip"] = profile.data.contact.address.postcode
        # if profile.data.job.position:
        #     payload["jobtitle"] = profile.data.job.position
        # if profile.data.contact.phone.whatsapp:
        #     payload['hs_whatsapp_phone_number'] = profile.data.contact.phone.whatsapp
        # if profile.data.contact.phone.mobile:
        #     payload['mobilephone'] = profile.data.contact.phone.mobile
        # if profile.data.media.social.twitter:
        #     payload['twitterhandle'] = profile.data.media.social.twitter

        if config_data:
            payload.update(config_data)

        return payload

    async def _dispatch(self, data: dict, flat_profile: FlatProfile):  # Data comes from mapping

        payload = self._prepare_payload(flat_profile, data)

        # If there is any data to send
        logger.info(f"Prepared data payload {payload}")

        if not payload:
            logger.info(f"No update in hubspot data is empty for profile {flat_profile.id}.")
            return

        integration_ids = await load_integration_id(flat_profile.id, self.name)

        if not integration_ids:
            return await self._add_contact(payload, flat_profile.id)

        logger.info(f"Found hubspot integration data {integration_ids}")

        # Get first
        integration = integration_ids[0]

        hubspot_id = integration.get_first_id()

        if hubspot_id is None:
            # Try to add
            await self._add_contact(payload, flat_profile.id)

        else:
            # Try to update
            await self._update_contact(payload, flat_profile.id, hubspot_id)

    async def dispatch_profile(self, data: dict, flat_profile: Optional[FlatProfile], changed_fields: List[dict] = None,
                               metadata=None):
        if flat_profile:
            await self._dispatch(data, flat_profile)

    async def dispatch_event(self, data, flat_event: FlatEvent, metadata=None, profile_id: Optional[str] = None, session_id: Optional[str] = None):
        raise NotImplementedError("Sending events to hubspot is not implemented")
