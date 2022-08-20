from tracardi.service.tracardi_http_client import HttpClient
from .send_event.model.config import MatomoPayload


class MatomoClientException(Exception):
    pass


class MatomoClient:

    def __init__(self, token: str, api_url: str):
        self.token = token
        self.api_url = api_url
        self.retries = 1

    def set_retries(self, retries: int) -> None:
        self.retries = retries

    async def send_event(self, matomo_payload: MatomoPayload):
        async with HttpClient(self.retries, 204, headers={"X-FORWARDED-FOR": matomo_payload.cip}) as client:
            async with client.post(
                url=f"{self.api_url}/matomo.php",
                params={"token_auth": self.token, **matomo_payload.to_dict()}
            ) as response:

                if response.status != 204:
                    raise MatomoClientException(await response.text())
