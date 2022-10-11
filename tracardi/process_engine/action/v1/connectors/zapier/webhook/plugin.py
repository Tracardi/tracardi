import asyncio
import json

from tracardi.service.tracardi_http_client import HttpClient
import aiohttp
from aiohttp import ClientConnectorError
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.notation.dict_traverser import DictTraverser

from .model.configuration import Configuration


def validate(config: dict) -> Configuration:
    config = Configuration(**config)

    # Try parsing JSON just for validation purposes
    try:
        json.loads(config.body)
    except json.JSONDecodeError as e:
        raise ValueError(str(e))

    return config


class ZapierWebHookAction(ActionRunner):

    config: Configuration

    async def set_up(self, init):
        self.config = Configuration(**init)

    async def run(self, payload: dict, in_edge=None) -> Result:

        try:

            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            async with HttpClient(
                self.node.on_connection_error_repeat,
                [200, 201, 202, 203, 204],
                timeout=timeout
            ) as client:

                converter = DictTraverser(self._get_dot_accessor(payload))
                body_as_dict = json.loads(self.config.body)
                async with client.request(
                        method="POST",
                        url=str(self.config.url),
                        json=converter.reshape(body_as_dict)
                ) as response:
                    # todo add headers and cookies
                    result = {
                        "status": response.status,
                        "json": await response.json()
                    }

                    if response.status in [200, 201, 202, 203, 204]:
                        return Result(port="response", value=result)
                    else:
                        return Result(port="error", value=result)

        except ClientConnectorError as e:
            return Result(port="error", value=str(e))

        except asyncio.exceptions.TimeoutError:
            return Result(port="error", value="Zapier webhook timed out.")


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='ZapierWebHookAction',
            inputs=['payload'],
            outputs=["response", "error"],
            version="0.7.0",
            author="Risto Kowaczewski",
            license="MIT",
            manual="zapier_webhook_action"
        ),
        metadata=MetaData(
            name='Zapier webhook',
            desc='Sends message to zapier webhook.',
            icon='zapier',
            group=["Zapier"],
            tags=['automation'],
            pro=True
        )
    )
