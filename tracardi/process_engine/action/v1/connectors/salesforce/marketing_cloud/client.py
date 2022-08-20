import aiohttp
from typing import Optional, Dict, Any
from tracardi.service.tracardi_http_client import HttpClient


class MarketingCloudAuthException(Exception):
    pass


class MarketingCloudClientException(Exception):
    pass


class MarketingCloudClient:

    def __init__(self, subdomain: str, client_id: str, client_secret: str, token: Optional[str] = None):
        self.subdomain = subdomain
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = token
        self.retries = 1

    def set_retries(self, retries: int) -> None:
        self.retries = retries

    async def get_token(self):
        async with HttpClient() as client:
            async with client.post(
                    url=f"https://{self.subdomain}.auth.marketingcloudapis.com/v2/token",
                    data={
                        "grant_type": "client_credentials",
                        "scope": "data_extensions_write",
                        "client_id": self.client_id,
                        "client_secret": self.client_secret
                    }
            ) as response:
                if response.status != 200:
                    raise MarketingCloudClientException(await response.text())

                self.token = (await response.json())["access_token"]

    async def add_record(self, mapping: Dict[str, Any], extension_id: str, update: bool):
        async with HttpClient(
            self.retries,
            [202, 401],
            headers={"Authorization": f"Bearer {self.token}"}
        ) as client:
            method = client.put if update else client.post
            async with method(
                    url=f"https://{self.subdomain}.rest.marketingcloudapis.com/data/v1/async/dataextensions/"
                        f"{extension_id}/rows",
                    json={"items": [mapping]}
            ) as response:

                if response.status == 401:
                    raise MarketingCloudAuthException(await response.text())

                if response.status != 202:
                    raise MarketingCloudClientException(await response.text())

                return await response.json()

    @property
    def credentials(self):
        return {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "subdomain": self.subdomain,
            "token": self.token
        }