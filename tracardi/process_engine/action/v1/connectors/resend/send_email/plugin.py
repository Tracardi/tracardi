import aiohttp
from aiohttp import ContentTypeError
from json import JSONDecodeError
from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.resources.resend import ResendResource
from tracardi.service.tracardi_http_client import HttpClient
from tracardi.service.storage.driver.elastic import resource as resource_db
from tracardi.service.plugin.domain.config import PluginConfig
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from typing import Any, Union, Optional
from pydantic import BaseModel


class SendEmailParams(BaseModel):
    sender: str
    to: Union[str, list[str]]
    subject: str
    bcc: Optional[Union[str, list[str]]] = None
    cc: Optional[Union[str, list[str]]] = None
    reply_to: Optional[Union[str, list[str]]] = None
    message: dict
    headers: Optional[dict[str, Any]] = None
    attachments: Optional[Any] = None
    tags: Optional[Any] = None


class Config(PluginConfig):
    resource: NamedEntity
    params: SendEmailParams


def validate(config: dict) -> Config:
    return Config(**config)


class ResendSendEmailAction(ActionRunner):
    credentials: ResendResource
    config: SendEmailParams

    async def set_up(self, init):
        config = validate(init)
        resource = await resource_db.load(config.resource.id)

        self.config = config.params
        self.credentials: "ResendResource" = resource.credentials.get_credentials(self, output=ResendResource)

    async def run(self, payload: dict, in_edge=None) -> Result:
        url = f"https://api.resend.com/emails"
        params = {
            "from": self.config.sender,
            "to": self.config.to,
            "subject": self.config.subject,
            "bcc": self.config.bcc,
            "cc": self.config.cc,
            "reply_to": self.config.reply_to,
            "headers": self.config.headers
        }
        if self.config.message.get("type", None) == "text/html":
            params["html"] = self.config.message.get("content", "")
        else:
            params["text"] = self.config.message.get("content", "")

        timeout = aiohttp.ClientTimeout(total=2)
        async with HttpClient(0, [200, 201, 202, 203], timeout=timeout) as client:
            async with client.post(
                url=url,
                json=params,
                headers={"Authorization": f"Bearer {self.credentials.api_key}"},
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
