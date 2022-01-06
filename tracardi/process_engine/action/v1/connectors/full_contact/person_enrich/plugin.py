import aiohttp
import asyncio
from aiohttp import ClientConnectorError
from tracardi.domain.resource import Resource, ResourceCredentials
from tracardi.service.storage.driver import storage
from tracardi_dot_notation.dict_traverser import DictTraverser
from tracardi_dot_notation.dot_accessor import DotAccessor
from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent
from tracardi_plugin_sdk.domain.result import Result

from .model.configuration import Configuration
from .model.full_contact_source_configuration import FullContactSourceConfiguration


def validate(config: dict) -> Configuration:
    return Configuration(**config)


class FullContactAction(ActionRunner):

    @staticmethod
    async def build(**kwargs) -> 'FullContactAction':
        config = validate(kwargs)
        resource = await storage.driver.resource.load(config.source.id)  # type: Resource

        return FullContactAction(config, resource.credentials)

    def __init__(self, config: Configuration, credentials: ResourceCredentials):
        self.credentials = credentials.get_credentials(self,
                                                       output=FullContactSourceConfiguration)  # type: FullContactSourceConfiguration
        self.config = config

    async def run(self, payload):
        dot = DotAccessor(self.profile, self.session, payload, self.event, self.flow)

        try:

            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:

                mapper = DictTraverser(dot)
                payload = mapper.reshape(reshape_template=self.config.pii.dict())

                async with session.request(
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
                        return Result(port="payload", value=result), Result(port="error", value=None)
                    else:
                        return Result(port="payload", value=None), Result(port="error", value=result)

        except ClientConnectorError as e:
            return Result(port="payload", value=None), Result(port="error", value=str(e))

        except asyncio.exceptions.TimeoutError:
            return Result(port="payload", value=None), Result(port="error", value="FullContact webhook timed out.")


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='FullContactAction',
            inputs=["payload"],
            outputs=['payload', "error"],
            version='0.6.1',
            license="MIT",
            author="Risto Kowaczewski",
            manual="fullcontact_webhook_action",
            init={
                "source": {
                    "id": None
                },
                "pii": {
                    "email": None,
                    "emails": [],
                    "phone": None,
                    "phones": [],
                    "location": None,
                    "name": None
                }
            },
            form=Form(groups=[
                FormGroup(
                    fields=[
                        FormField(
                            id="source",
                            name="FullContact resource",
                            description="Select FullContact resource. Credentials from selected resource will be used "
                                        "to connect the service.",
                            required=True,
                            component=FormComponent(type="resource", props={"label": "resource", "tag": "token"})
                        )
                    ]
                ),
                FormGroup(
                    fields=[
                        FormField(
                            id="pii.email",
                            name="E-mail",
                            description="Type path to E-mail",
                            component=FormComponent(type="dotPath", props={"label": "Path to e-mail"})
                        ),
                        FormField(
                            id="pii.phone",
                            name="Phone",
                            description="Type path to phone",
                            component=FormComponent(type="dotPath", props={"label": "Path to phone"})
                        )
                    ]
                ),
            ]),
        ),
        metadata=MetaData(
            name='Full contact person enrich',
            desc='This plugin retrieves data about the provided e-mail from FullContact service.',
            icon='fullcontact',
            group=["Connectors"]
        )
    )
