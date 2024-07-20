import asyncio
import json
from json import JSONDecodeError

import aiohttp
from typing import Optional, List

from aiohttp import ClientConnectorError, BasicAuth, ContentTypeError
from pydantic import BaseModel

from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.exceptions.log_handler import get_logger
from tracardi.process_engine.tql.utils.dictonary import flatten
from tracardi.process_engine.action.v1.connectors.api_call.model.configuration import Method
from .destination_interface import DestinationInterface
from ...domain.event import Event

logger = get_logger(__name__)


class HttpCredentials(BaseModel):
    url: str  # AnyHttpUrl
    username: Optional[str] = None
    password: Optional[str] = None

    def has_basic_auth(self):
        return self.username and self.password


class HttpConfiguration(BaseModel):
    timeout: int = 30
    method: Method = Method.get
    headers: Optional[dict] = {}
    cookies: Optional[dict] = {}
    ssl_check: bool = True

    @staticmethod
    def _convert_params(param):
        if isinstance(param, bool):
            return 1 if param else 0
        return param

    def get_params(self, body: dict) -> dict:

        self.headers = {key.lower(): value for key, value in self.headers.items()}

        content_type = self.headers['content-type'] if 'content-type' in self.headers else 'application/json'

        if content_type == 'application/json':

            if self.method.lower() == 'get':
                params = flatten(body)
                params = {key: self._convert_params(value) for key, value in params.items() if value is not None}
                return {
                    "params": params
                }

            return {
                "json": body
            }
        else:
            return {"data": json.dumps(body)}


class HttpConnector(DestinationInterface):

    @staticmethod
    def _validate_key_value(values, label):
        for name, value in values.items():
            if not isinstance(value, str):
                raise ValueError(
                    "{} values must be strings, `{}` given for {} `{}`".format(label, type(value), label.lower(),
                                                                               name))

    async def _dispatch(self, data, changed_fields):
        try:
            credentials = self.resource.credentials.test if self.debug is True else self.resource.credentials.production
            credentials = HttpCredentials(**credentials)

            init = self.destination.destination.init

            config = HttpConfiguration(**init)

            self._validate_key_value(config.headers, "Header")
            self._validate_key_value(config.cookies, "Cookie")

            timeout = aiohttp.ClientTimeout(total=config.timeout)
            url = str(credentials.url)

            async with aiohttp.ClientSession(timeout=timeout) as session:
                params = config.get_params({
                    "data": data,
                    "changes": changed_fields
                })

                async with session.request(
                        method=config.method,
                        url=url,
                        headers=config.headers,
                        cookies=config.cookies,
                        ssl=config.ssl_check,
                        auth=BasicAuth(credentials.username,
                                       credentials.password) if credentials.has_basic_auth() else None,
                        **params
                ) as response:

                    try:
                        content = await response.json(content_type=None)

                    except JSONDecodeError:
                        content = await response.text()

                    except ContentTypeError:
                        content = await response.json(content_type='text/html')

                    result = {
                        "status": response.status,
                        "content": content,
                        "cookies": response.cookies
                    }

                    logger.debug(f"Destination response from {url}, response: {result}")

                    # todo log

        except ClientConnectorError as e:
            logger.error(str(e), e, exc_info=True)
            raise e

        except asyncio.exceptions.TimeoutError as e:
            logger.error(str(e), e, exc_info=True)
            raise e

    async def dispatch_profile(self, data, profile: Profile, session: Optional[Session],
                               changed_fields: List[dict] = None, metadata=None):
        await self._dispatch(data, changed_fields)

    async def dispatch_event(self, data, profile: Optional[Profile], session: Optional[Session], event: Event,
                             metadata=None):
        await self._dispatch(data, [])
