import asyncio
import json
import logging
from json import JSONDecodeError

import aiohttp
from typing import Optional

from aiohttp import ClientConnectorError, BasicAuth, ContentTypeError
from pydantic import BaseModel

from tracardi.config import tracardi
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.exceptions.log_handler import log_handler
from tracardi.process_engine.tql.utils.dictonary import flatten
from tracardi.process_engine.action.v1.connectors.api_call.model.configuration import Method
from .destination_interface import DestinationInterface
from ...domain.event import Event

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


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


class HttpConnector(DestinationInterface):

    @staticmethod
    def _validate_key_value(values, label):
        for name, value in values.items():
            if not isinstance(value, str):
                raise ValueError(
                    "{} values must be strings, `{}` given for {} `{}`".format(label, type(value), label.lower(),
                                                                               name))

    async def _dispatch(self, data):
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
                params = config.get_params(data)
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

                    logger.debug(f"Profile destination response from {url}, response: {result}")

                    # todo log

        except ClientConnectorError as e:
            logger.error(str(e))

        except asyncio.exceptions.TimeoutError as e:
            logger.error(str(e))

    async def dispatch_profile(self, data, profile: Profile, session: Session):
        await self._dispatch(data)

    async def dispatch_event(self, data, profile: Profile, session: Session, event: Event):
        await self._dispatch(data)
