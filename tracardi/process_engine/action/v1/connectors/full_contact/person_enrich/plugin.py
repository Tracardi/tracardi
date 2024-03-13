from typing import Tuple

import aiohttp
import asyncio
from aiohttp import ClientConnectorError
from tracardi.domain.resource import Resource
from tracardi.domain.settings import Settings
from tracardi.service.domain import resource as resource_db
from tracardi.service.notation.dict_traverser import DictTraverser
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData
from tracardi.service.plugin.domain.result import Result
from tracardi.service.tracardi_http_client import HttpClient

from .model.configuration import Configuration
from .model.full_contact_source_configuration import FullContactSourceConfiguration


def validate(config: dict) -> Configuration:
    return Configuration(**config)


class FullContactAction(ActionRunner):

    config: Configuration
    credentials: FullContactSourceConfiguration

    async def set_up(self, init):
        config = validate(init)
        resource = await resource_db.load(config.source.id)  # type: Resource

        self.credentials = resource.credentials.get_credentials(self, output=FullContactSourceConfiguration)
        self.config = config

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)

        try:

            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            async with HttpClient(
                    self.node.on_connection_error_repeat,
                    [200, 201, 202, 203, 204],
                    timeout=timeout
            ) as client:

                mapper = DictTraverser(dot)
                payload = mapper.reshape(reshape_template=self.config.pii.model_dump())

                async with client.request(
                        method="POST",
                        headers={
                            "Content-type": "application/json",
                            "Authorization": f"Bearer {self.credentials.token}"
                        },
                        url='https://api.fullcontact.com/v3/person.enrich',
                        json=payload
                ) as response:
                    result = {
                        "status": response.status,
                        "body": await response.json()
                    }

                    if response.status in [200, 201, 202, 203, 204]:
                        return Result(port="payload", value=result)
                    else:
                        return Result(port="error", value=result)

        except ClientConnectorError as e:
            return Result(port="error", value=str(e))

        except asyncio.exceptions.TimeoutError:
            return Result(port="error", value="FullContact webhook timed out.")


def register() -> Tuple[Plugin, Settings]:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='FullContactAction',
            inputs=["payload"],
            outputs=['payload', "error"],
            version='0.6.1',
            license="Tracardi Pro",
            author="Risto Kowaczewski",
            manual="fullcontact_webhook_action"
        ),
        metadata=MetaData(
            name='Enrich profile',
            brand='Full contact',
            desc='This plugin retrieves data about the provided e-mail from FullContact service.',
            icon='fullcontact',
            group=["Connectors"],
            tags=['enhance', 'profile', 'contact'],
            pro=True
        )
    ), Settings(hidden=True)
