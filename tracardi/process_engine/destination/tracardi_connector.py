import asyncio
from json import JSONDecodeError

import aiohttp
from typing import Optional, List

from aiohttp import ClientConnectorError, BasicAuth, ContentTypeError
from pydantic import BaseModel

from tracardi.domain.flat_profile import FlatProfile
from tracardi.domain.session import Session
from tracardi.exceptions.log_handler import get_logger
from .destination_interface import DestinationInterface
from ...domain import ExtraInfo
from ...domain.flat_event import FlatEvent

logger = get_logger(__name__)


class TracardiApiCredentials(BaseModel):
    url: str  # AnyHttpUrl
    source_id: str
    username: Optional[str] = None
    password: Optional[str] = None
    timeout: Optional[int] = 30

    def has_basic_auth(self):
        return self.username and self.password


class TracardiConnector(DestinationInterface):

    async def _dispatch(self, flat_profile: Optional[FlatProfile], session: Optional[Session], flat_event: FlatEvent, metadata, context):
        try:
            credentials = self.resource.credentials.test if self.debug is True else self.resource.credentials.production
            credentials = TracardiApiCredentials(**credentials)

            timeout = aiohttp.ClientTimeout(total=credentials.timeout)
            url = str(credentials.url)

            if url.endswith('/'):
                url = url[:-1]

            async with aiohttp.ClientSession(timeout=timeout) as http:
                params = {
                    "source": {
                        "id": credentials.source_id
                    },
                    "session": {
                        "id": session.id
                    },
                    "profile": {
                        "id": flat_profile.id
                    },
                    "context": context,
                    "properties": {},
                    "events": [
                        {
                            "type": flat_event.type,
                            "properties": flat_event.properties,
                            "options": {},
                            "context": flat_event.context
                        }
                    ],
                    "options": {}
                }

                async with http.request(
                        method='POST',
                        url=f"{url}",
                        headers={
                            "referer": "none",
                            "content-type": "application/json"
                        },
                        ssl=True,
                        auth=BasicAuth(credentials.username,
                                       credentials.password) if credentials.has_basic_auth() else None,
                        json=params
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

    async def dispatch_profile(self, data, flat_profile: Optional[FlatProfile], session: Optional[Session],
                               changed_fields: List[dict] = None, metadata=None):
        logger.error("Tracardi API Destination can be only used with events.", extra=ExtraInfo.build(
            origin="destination",
            profile_id=flat_profile.id
        ))

    async def dispatch_event(self, data, flat_profile: Optional[FlatProfile], session: Optional[Session], flat_event: FlatEvent,
                             metadata=None):
        await self._dispatch(flat_profile, session, flat_event, metadata, context=data)
