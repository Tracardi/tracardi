import json
from json import JSONDecodeError
from pprint import pprint
from typing import Optional

import aiohttp
from tracardi.domain.resources.token import Token
from tracardi.service.plugin.plugin_endpoint import PluginEndpoint
from tracardi.service.tracardi_http_client import HttpClient
from tracardi.service.storage.driver import storage
from tracardi.service.plugin.domain.register import Plugin, Spec, Form, FormGroup, FormField, FormComponent, MetaData, \
    Documentation, PortDoc
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
                pprint(content)
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


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='NovuTriggerAction',
            inputs=['payload'],
            outputs=['response', 'error'],
            version="0.7.2",
            license="MIT",
            author="Mateusz Zitaruk, Risto Kowaczewski",
            init={
                "source": {"id": "", "name": ""},
                "template": {"id": "", "name": ""},
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
                                id="template",
                                name="Novu template name",
                                description="Type the template name defined in Novu. This template will be used to send"
                                            " a message.",
                                component=FormComponent(type="autocomplete", props={
                                    "label": "Template name",
                                    "endpoint": {
                                        "url": Endpoint.url(__name__, "get_templates"),
                                        "method": "post"
                                    },
                                })
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
                            ),
                            FormField(
                                id="payload",
                                name="Data",
                                description="Please type the data you would like to use within template. "
                                            "You may use the reference to data e.g. profile@pii.name. Please look for "
                                            "the term \"Object template\" in documentation for more details.",
                                component=FormComponent(type="json", props={"label": "Data"})
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
