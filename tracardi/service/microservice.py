import aiohttp
from aiohttp import ClientResponse
from pydantic import BaseModel
from tracardi.domain.credentials import Credentials
from tracardi.domain.token import Token
from tracardi.exceptions.exception import ConnectionException


class MicroserviceApi:

    def __init__(self, url, credentials: Credentials, timeout=15):
        if len(url) > 0 and url[-1] == '/':
            url = url[:-1]
        self.credentials = credentials
        self.url = url
        self.token = None
        self.timeout = aiohttp.ClientTimeout(total=timeout)

    async def authorize(self) -> Token:
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            if len(self.url) > 0 and self.url[-1] == '/':
                token_endpoint = 'token'
            else:
                token_endpoint = '/token'
            async with session.request(
                    method="POST",
                    url=f"{self.url}{token_endpoint}",
                    data=self.credentials.dict()
            ) as response:
                if 200 <= response.status < 400:
                    token = await response.json()
                    return Token(**token)

                raise ConnectionException("Authentication failed", response=response)

    async def _call(self, endpoint, method, data):
        async with aiohttp.ClientSession(timeout=self.timeout,
                                         headers=self.token.authorization_header()) as session:
            if endpoint[0] == '/':
                url = f"{self.url}{endpoint}"
            else:
                url = f"{self.url}/{endpoint}"

            async with session.request(
                    method=method,
                    url=url,
                    json=data
            ) as response:
                await response.json()

                return response

    async def call(self, endpoint, method, data=None) -> ClientResponse:

        if self.token is None:
            self.token = await self.authorize()

        if isinstance(data, BaseModel):
            data = data.dict()

        response = await self._call(endpoint, method, data)
        if response.status == 401:
            self.token = await self.authorize()
            response = await self._call(endpoint, method, data)
        return response
