from json import JSONDecodeError


from tracardi.service.tracardi_http_client import HttpClient


class ElasticEmailClientException(Exception):
    pass


class ElasticEmailClientAuthException(Exception):
    pass


class ElasticEmailClient:

    def __init__(self, api_key: int, public_account_id: str, retries: int = 1):
        self.api_url = 'https://api.elasticemail.com'
        self.api_key = api_key
        self.public_account_id = public_account_id
        self.retries = retries if retries >= 1 else 1

    def set_retries(self, retries: int) -> None:
        self.retries = retries

    async def emails_post(self, contact_data: dict, ) -> dict:
        data = {
            "apikey": self.api_key,
            **contact_data,
        }
        async with HttpClient(
                self.retries,
                [200, 201, 401],
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                }
        ) as session:
            async with session.post(
                    url=f"{self.api_url}/v2/Email/Send",
                    data=data
            ) as response:
                return await self.handle_response(response)

    async def contact_status_change(self, contact_data: dict, ) -> dict:
        params = {
            "apikey": self.api_key,
            **contact_data,
        }
        async with HttpClient(
                self.retries,
                [200, 201, 401],
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                }
        ) as session:
            async with session.post(
                    url=f"{self.api_url}/Contact/ChangeStatus",
                    data=params
            ) as response:
                return await self.handle_response(response)

    async def add_contact(self, contact_data: dict, ) -> dict:
        params = {
            "publicAccountID": self.public_account_id,
            "consentTracking": 1,
            "sendActivation": 'false',
            **contact_data,
        }
        async with HttpClient(
                self.retries,
                [200, 201, 401],
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                }
        ) as session:
            async with session.get(
                    url=f"{self.api_url}/v2/Contact/Add",
                    params=params
            ) as response:
                return await self.handle_response_add_contact(response)

    @staticmethod
    async def handle_response_add_contact(response):
        if response.status == 401:
            raise ElasticEmailClientAuthException()
        try:
            content = await response.json(content_type='text/html')
        except JSONDecodeError:
            content = await response.text()
        if response.status not in (200, 201) or content.get('success') is False:
            raise ElasticEmailClientException(content)
        return content

    @staticmethod
    async def handle_response(response):
        if response.status == 401:
            raise ElasticEmailClientAuthException()
        try:
            content = await response.json()
        except JSONDecodeError:
            content = await response.text()
        if response.status not in (200, 201) or content.get('success') is False:
            raise ElasticEmailClientException(content)
        return content

