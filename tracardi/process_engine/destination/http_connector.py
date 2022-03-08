import json

import aiohttp
from typing import Optional
from pydantic import BaseModel, AnyHttpUrl
from tracardi.process_engine.tql.utils.dictonary import flatten

from tracardi.process_engine.action.v1.connectors.api_call.model.configuration import Method

from tracardi.process_engine.destination.connector import Connector


class HttpCredentials(BaseModel):
    url: AnyHttpUrl
    username: str
    password: str


class HttpConfiguration(BaseModel):
    timeout: int = 30
    method: Method = Method.get
    headers: Optional[dict] = {}
    cookies: Optional[dict] = {}
    ssl_check: bool = True

    def get_params(self, body: dict) -> dict:

        content_type = self.headers['content-type'] if 'content-type' in self.headers else 'application/json'

        if content_type == 'application/json':

            if self.method.lower() == 'get':
                params = flatten(body)
                return {
                    "params": params
                }

            return {
                "json": body
            }
        else:
            return {"data": json.dumps(body)}


class HttpConnector(Connector):

    @staticmethod
    def _validate_key_value(values, label):
        for name, value in values.items():
            if not isinstance(value, str):
                raise ValueError(
                    "{} values must be strings, `{}` given for {} `{}`".format(label, type(value), label.lower(),
                                                                               name))

    async def run(self, data, delta):

        credentials = self.resource.credentials.test if self.debug is True else self.resource.credentials.production
        credentials = HttpCredentials(**credentials)

        init = self.destination.destination.init

        config = HttpConfiguration(**init)

        self._validate_key_value(config.headers, "Header")
        self._validate_key_value(config.cookies, "Cookie")

        timeout = aiohttp.ClientTimeout(total=config.timeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.request(
                    method=config.method,
                    url=str(credentials.url),
                    headers=config.headers,
                    cookies=config.cookies,
                    ssl=config.ssl_check,
                    **config.get_params(data)
            ) as response:
                result = {
                    "status": response.status,
                    "content": await response.json(),
                    "cookies": response.cookies
                }

                print(result)
