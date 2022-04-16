import aiohttp
from .send_event.model.config import MatomoPayload


class MatomoClientException(Exception):
    pass


class MatomoClient:

    def __init__(self, token: str, api_url: str):
        self.token = token
        self.api_url = api_url

    async def send_event(self, matomo_payload: MatomoPayload):
        async with aiohttp.ClientSession(headers={"X-FORWARDED-FOR": matomo_payload.cip}) as session:
            async with session.post(
                url=f"{self.api_url}/matomo.php",
                params={"token_auth": self.token, **matomo_payload.to_dict()}
            ) as response:

                if response.status != 204:
                    raise MatomoClientException(await response.text())
