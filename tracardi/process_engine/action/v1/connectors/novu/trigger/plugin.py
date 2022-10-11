import json
from json import JSONDecodeError
from typing import Optional

import aiohttp
from tracardi.domain.resources.token import Token
from tracardi.service.plugin.plugin_endpoint import PluginEndpoint
from tracardi.service.tracardi_http_client import HttpClient
from tracardi.service.storage.driver import storage
from tracardi.domain.named_entity import NamedEntity
from tracardi.service.plugin.domain.config import PluginConfig
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner


class Config(PluginConfig):
    source: NamedEntity
    template: NamedEntity
    subscriber_id: str
    recipient_email: Optional[str] = ""
    payload: Optional[str] = "{}"


def validate(config: dict) -> Config:
    return Config(**config)


class Endpoint(PluginEndpoint):

    @staticmethod
    async def get_templates(config: dict):
        config = Config(**config)
        if config.source.is_empty():
            raise ValueError("Resource not set.")

        resource = await storage.driver.resource.load(config.source.id)
        creds = Token(**resource.credentials.production)
        timeout = aiohttp.ClientTimeout(total=15)
        async with HttpClient(2, [200, 201, 202, 203], timeout=timeout) as client:
            async with client.get(
                    url="https://api.novu.co/v1/notification-templates",
                    headers={"Authorization": f"ApiKey {creds.token}",
                             "Content Type": "application/json"},
                    ssl=True
            ) as response:
                content = await response.json()
                result = [{"id": item['triggers'][0]['identifier'], "name": item['name']} for item in content['data'] if
                          item['active'] is True]
                return {
                    "total": len(result),
                    "result": result
                }


class NovuTriggerAction(ActionRunner):
    credentials: Token
    config: Config

    async def set_up(self, init):
        config = validate(init)
        resource = await storage.driver.resource.load(config.source.id)

        self.config = config
        self.credentials = resource.credentials.get_credentials(self, output=Token)

    async def run(self, payload: dict, in_edge=None) -> Result:
        url = 'https://api.novu.co/v1/events/trigger'
        dot = self._get_dot_accessor(payload)
        timeout = aiohttp.ClientTimeout(total=15)
        params = {
            "name": self.config.template.id,
            "to": {
                "subscriberId": dot[self.config.subscriber_id],
                "email": dot[self.config.recipient_email]
            },
            "payload": json.loads(self.config.payload)
        }

        async with HttpClient(self.node.on_connection_error_repeat, [200, 201, 202, 203],
                              timeout=timeout) as client:
            async with client.post(
                    url=url,
                    headers={"Authorization": f"ApiKey {self.credentials.token}",
                             "Content Type": "application/json"},
                    ssl=False,
                    json=params
            ) as response:
                try:
                    content = await response.json()
                except JSONDecodeError:
                    content = await response.text()

                result = {
                    "status": response.status,
                    "content": content
                }

                if response.status in [200, 201, 202, 203]:
                    return Result(port="response", value=result)
                else:
                    return Result(port="error", value=result)
