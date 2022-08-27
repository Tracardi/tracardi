import json
from json import JSONDecodeError

import aiohttp


class ElasticEmailClientException(Exception):
    pass


class ElasticEmailClientAuthException(Exception):
    pass


class ElasticEmailClient:

    def __init__(self, api_key: int, public_account_id: str):
        self.api_url = 'https://api.elasticemail.com'
        self.api_key = api_key
        self.public_account_id = public_account_id

    async def add_contact(self, contact_data: dict, ) -> dict:
        params = {
            "publicAccountID": self.public_account_id,
            "consentTracking": 1,
            "sendActivation": 'false',
            **contact_data,
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(
                    url=f"{self.api_url}/v2/Contact/Add",
                    params=params
            ) as response:
                return await self.handle_response(response)

    @staticmethod
    async def handle_response(response):
        if response.status == 401:
            raise ElasticEmailClientAuthException()
        try:
            content = await response.json(content_type='text/html')

        except JSONDecodeError:
            content = await response.text()
        if response.status not in (200, 201) or content.get('success') is False:
            raise ElasticEmailClientException(content)
        return content

    @property
    def credentials(self):
        return {
            "api_key": self.api_key,
            "public_account_id": self.public_account_id,
            "api_url": self.api_url,
        }
