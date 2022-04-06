import aiohttp
import json


class MatomoClientException(Exception):
    pass


class MatomoClient:

    def __init__(self, token: str, api_url: str):
        self.token = token
        self.api_url = api_url

    async def send_event(self, id_site: int, data: dict):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=f"{self.api_url}/matomo.php",
                params={
                    "token_auth": self.token,
                    "idsite": id_site,
                    "send_image": 0,
                    "rec": 1,
                    **{key: json.dumps(value) for key, value in data.items() if isinstance(value, dict)}
                }
            ) as response:

                if response.status != 204:
                    raise MatomoClientException(await response.text())
