import asyncio
import aiohttp
from aiohttp import ClientConnectorError
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.notation.dot_template import DotTemplate
from tracardi.service.tracardi_http_client import HttpClient

from .model.configuration import DiscordWebHookConfiguration


def validate(config: dict) -> DiscordWebHookConfiguration:
    return DiscordWebHookConfiguration(**config)


class DiscordWebHookAction(ActionRunner):

    config: DiscordWebHookConfiguration

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)
        template = DotTemplate()

        try:

            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            async with HttpClient(
                    self.node.on_connection_error_repeat,
                    [200, 201, 202, 203, 204],
                    timeout=timeout
            ) as client:

                params = {
                    "json": {
                        "content": template.render(self.config.message, dot),
                        "username": self.config.username if self.config.username and len(
                            self.config.username) > 0 else None
                    }
                }

                async with client.request(
                        method="POST",
                        url=str(self.config.url),
                        **params
                ) as response:
                    # todo add headers and cookies
                    result = {
                        "status": response.status
                    }

                    if response.status in [200, 201, 202, 203, 204]:
                        return Result(port="response", value=payload)
                    else:
                        return Result(port="error", value=result)

        except ClientConnectorError as e:
            return Result(port="error", value=str(e))

        except asyncio.exceptions.TimeoutError:
            return Result(port="error", value="Discord webhook timed out.")


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='DiscordWebHookAction',
            inputs=['payload'],
            outputs=["response", "error"],
            init={
                "url": None,
                "timeout": 10,
                "message": "",
                "username": None
            },
            form=Form(groups=[
                FormGroup(
                    name="Discord server settings",
                    description="This action will require a webhook URL. See documentation how to obtain it.",
                    fields=[
                        FormField(
                            id="url",
                            name="Discord webhook URL",
                            description="Paste here a webhook for a given channel.",
                            component=FormComponent(type="text", props={
                                "label": "Webhook URL"
                            })
                        ),
                        FormField(
                            id="timeout",
                            name="Webhook timeout",
                            component=FormComponent(type="text", props={
                                "label": "Webhook time-out"
                            })
                        ),
                    ]
                ),
                FormGroup(
                    name="Discord message settings",
                    fields=[
                        FormField(
                            id="message",
                            name="Message",
                            description="Type message template. Data placeholders can be used to obtain data from "
                                        "profile, event etc.",
                            component=FormComponent(type="textarea", props={"label": "Message template", "rows": 6})
                        ),
                        FormField(
                            id="username",
                            name="Sender username",
                            description="Type sender username. This field is optional.",
                            component=FormComponent(type="text", props={"label": "Sender"})
                        )
                    ]
                )
            ]
            ),
            version="0.6.1",
            author="Risto Kowaczewski",
            license="MIT",
            manual="discord_webhook_action"
        ),
        metadata=MetaData(
            name='Discord push',
            desc='Sends message to discord webhook.',
            icon='discord',
            group=["Messaging"]
        )
    )
