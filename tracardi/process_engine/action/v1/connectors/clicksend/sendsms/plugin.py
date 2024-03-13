import aiohttp
from aiohttp import ContentTypeError
from json import JSONDecodeError
from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.resources.clicksend_resource import ClicksendResourceCredentials
from tracardi.service.notation.dot_template import DotTemplate
from tracardi.service.tracardi_http_client import HttpClient
from tracardi.service.domain import resource as resource_db
from tracardi.service.plugin.domain.config import PluginConfig
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner


class Config(PluginConfig):
    resource: NamedEntity
    message: str
    recipient: str
    sender: str


def validate(config: dict) -> Config:
    return Config(**config)


class ClicksendSendSmsAction(ActionRunner):
    credentials: ClicksendResourceCredentials
    config: Config

    async def set_up(self, init):
        config = validate(init)
        resource = await resource_db.load(config.resource.id)

        self.config = config
        self.credentials = resource.credentials.get_credentials(self, output=ClicksendResourceCredentials)

    async def run(self, payload: dict, in_edge=None) -> Result:
        url = 'https://rest.clicksend.com/v3/sms/send'
        dot = self._get_dot_accessor(payload)
        timeout = aiohttp.ClientTimeout(total=15)
        template = DotTemplate()
        message = template.render(self.config.message, dot)
        params = {
            "messages": [
                {
                    "body": message,
                    "to": dot[self.config.recipient],
                    "from": dot[self.config.sender],
                },
            ],
        }

        async with HttpClient(
                self.node.on_connection_error_repeat,
                [200],
                timeout=timeout,
                auth=aiohttp.BasicAuth(self.credentials.username, self.credentials.api_key)
        ) as client:
            async with client.post(
                    url=url,
                    json=params
            ) as response:
                try:
                    content = await response.json()
                except ContentTypeError:
                    content = await response.text()
                except JSONDecodeError:
                    content = await response.text()

                result = {
                    "status": response.status,
                    "content": content
                }

                if response.status in [200]:
                    return Result(port="response", value=result)
                else:
                    return Result(port="error", value=result)
