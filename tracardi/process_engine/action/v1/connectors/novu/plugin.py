import json
from json import JSONDecodeError
from typing import Optional

import aiohttp
from tracardi.domain.resources.token import Token
from tracardi.service.tracardi_http_client import HttpClient
from tracardi.service.storage.driver import storage
from tracardi.service.plugin.domain.register import Plugin, Spec, Form, FormGroup, FormField, FormComponent, MetaData, \
    Documentation, PortDoc
from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.resource import ResourceCredentials
from tracardi.service.plugin.domain.config import PluginConfig
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner


class Config(PluginConfig):
    source: NamedEntity
    template_name: str
    subscriber_id: str
    recipient_email: Optional[str] = ""
    payload: Optional[str] = "{}"


def validate(config: dict) -> Config:
    return Config(**config)


class NotificationGeneratorAction(ActionRunner):

    @staticmethod
    async def build(**kwargs) -> 'NotificationGeneratorAction':
        config = validate(kwargs)
        resource = await storage.driver.resource.load(config.source.id)
        return NotificationGeneratorAction(config, resource.credentials)

    def __init__(self, config: Config, credentials: ResourceCredentials):
        self.config = config
        self.credentials = credentials.get_credentials(self, output=Token)  # type: Token

    async def run(self, payload: dict, in_edge=None) -> Result:
        url = 'https://api.novu.co/v1/events/trigger'
        dot = self._get_dot_accessor(payload)
        timeout = aiohttp.ClientTimeout(total=15)
        params = {
            "name": self.config.template_name,
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


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='NotificationGeneratorAction',
            inputs=['payload'],
            outputs=['response', 'error'],
            version="0.7.2",
            license="MIT",
            author="Mateusz Zitaruk",
            init={
                "source": {"id": "", "name": ""},
                "template_name": None,
                "subscriber_id": "profile@id",
                "recipient_email": "profile@pii.email",
                "payload": "{}"
            },
            manual="novu_plugin_action",
            form=Form(
                groups=[
                    FormGroup(
                        name="Novu notification configuration",
                        fields=[
                            FormField(
                                id="source",
                                name="Resource",
                                description="Select your api key resource containing your key from novu",
                                component=FormComponent(type="resource", props={"label": "resource", "tag": "novu"})
                            ),
                            FormField(
                                id="template_name",
                                name="Novu template name",
                                description="Type the template name defined in Novu. This template will be used to send"
                                            " a message.",
                                component=FormComponent(type="text", props={"label": "Template name"})
                            ),
                            FormField(
                                id="subscriber_id",
                                name="Subscriber ID",
                                description="Type path to subscriber ID. By default we use profile id.",
                                component=FormComponent(type="dotPath", props={"label": "Subscriber ID"})
                            )
                        ]
                    ),
                    FormGroup(
                        name="E-mail configuration",
                        fields=[
                            FormField(
                                id="recipient_email",
                                name="Recipient e-mail address",
                                description="Please type a reference path to e-mail address. By default we set it to "
                                            "profile@pii.email.",
                                component=FormComponent(type="dotPath", props={"label": "E-mail address"})
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name="Novu notifications",
            desc="Create and send notification to chosen recipient.",
            brand="Novu",
            icon="message",
            group=["Novu"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "response": PortDoc(desc="This port returns response status and content."),
                    "error": PortDoc(desc="This port returns error if request will fail ")}
            )
        )
    )
