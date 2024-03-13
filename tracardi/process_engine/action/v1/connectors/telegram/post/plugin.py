import aiohttp
from aiohttp import ContentTypeError
from json import JSONDecodeError
from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.resources.telegram import TelegramResource
from tracardi.service.notation.dot_template import DotTemplate
from tracardi.service.tracardi_http_client import HttpClient
from tracardi.service.domain import resource as resource_db
from tracardi.service.plugin.domain.config import PluginConfig
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner


class Config(PluginConfig):
    resource: NamedEntity
    message: str


def validate(config: dict) -> Config:
    return Config(**config)


class TelegramPostAction(ActionRunner):
    credentials: TelegramResource
    config: Config

    async def set_up(self, init):
        config = validate(init)
        resource = await resource_db.load(config.resource.id)

        self.config = config
        self.credentials = resource.credentials.get_credentials(self, output=TelegramResource)

    async def run(self, payload: dict, in_edge=None) -> Result:
        url = f"https://api.telegram.org/bot{self.credentials.bot_token}/sendMessage"
        dot = self._get_dot_accessor(payload)
        template = DotTemplate()
        message = template.render(self.config.message, dot)
        params = {
            "text": message,
            "chat_id": self.credentials.chat_id,
        }

        timeout = aiohttp.ClientTimeout(total=15)
        async with HttpClient(self.node.on_connection_error_repeat, [200, 201, 202, 203], timeout=timeout) as client:
            async with client.get(
                    url=url,
                    data=params
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

                if response.status in [200, 201, 202, 203]:
                    return Result(port="response", value=result)
                else:
                    return Result(port="error", value=result)
