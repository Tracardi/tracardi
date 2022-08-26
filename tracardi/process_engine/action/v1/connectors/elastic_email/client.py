import aiohttp


class ElasticEmailClientException(Exception):
    pass


class ElasticEmailClientAuthException(Exception):
    pass


class ElasticEmailClient:

    def __init__(self, api_url: str, api_key: int, public_account_id: str):
        self.api_url = api_url
        self.api_key = api_key
        self.public_account_id = public_account_id

    async def add_contact(self, contact_data: dict, field: dict) -> dict:
        params = {
            "publicAccountID": self.public_account_id,
            "consentTracking": 1,
            "sendActivation": False,
            **contact_data,
            # todo field is a Repeated list of string keys and string values
            # "field": custom_fields,
            # **kwargs
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(
                    url=f"{self.api_url}/Contact/Add",
                    params=params
            ) as response:

                if response.status == 401:
                    raise ElasticEmailClientAuthException()

                if response.status not in (200, 201) or "error" in await response.text() or "errors" in \
                        await response.json():
                    raise ElasticEmailClientException(await response.text())

                return await response.json()



    @property
    def credentials(self):
        return {
            "api_key": self.api_key,
            "public_account_id": self.public_account_id,
            "api_url": self.api_url,
        }
