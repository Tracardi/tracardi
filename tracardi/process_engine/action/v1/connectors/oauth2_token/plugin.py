from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi_plugin_sdk.domain.result import Result
from .model.config import Config
from tracardi.service.storage.driver import storage
from tracardi.domain.resource import ResourceCredentials
from tracardi.domain.resources.remote_api_resource import RemoteApiResource
import aiohttp


def validate(config: dict) -> Config:
    return Config(**config)


class TokenGetter(ActionRunner):

    @staticmethod
    async def build(**kwargs) -> 'TokenGetter':
        config = Config(**kwargs)
        source = await storage.driver.resource.load(config.source.id)
        return TokenGetter(config, source.credentials)

    def __init__(self, config: Config, credentials: ResourceCredentials):
        self.config = config
        self._credentials = credentials.get_credentials(self, RemoteApiResource)

    async def run(self, payload):
        dot = self._get_dot_accessor(payload)

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=self._credentials.url,
                data={
                    "username": self._credentials.username,
                    "password": self._credentials.password
                }
            ) as response:

                if response.status != 200:
                    return Result(port="error", value={})

                dot[self.config.destination] = await response.json()

                return Result(port="payload", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='TokenGetter',
            inputs=["payload"],
            outputs=["payload", "error"],
            version='0.6.0.1',
            license="MIT",
            author="Dawid Kruk",
            init={
                "source": {
                    "id": None,
                    "name": None
                },
                "destination": None
            },
            manual="oauth2_token_action",
            form=Form(
                name="Plugin configuration",
                groups=[
                    FormGroup(
                        fields=[
                            FormField(
                                id="source",
                                name="API endpoint resource",
                                description="Please select your API endpoint resource.",
                                component=FormComponent(type="resource", props={"label": "Resource", "tag": "api"})
                            ),
                            FormField(
                                id="destination",
                                name="Token destination",
                                description="Please provide a path to a field in payload where you want to store your "
                                            "token.",
                                component=FormComponent(type="dotPath", props={"label": "Prefix"})
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Get OAuth2 token',
            desc='Gets OAuth2 token from given endpoint, using given username and password.',
            type='flowNode',
            icon='plugin',
            group=["Connectors"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "payload": PortDoc(desc="This port returns payload object, modified or not, according to plugin "
                                            "configuration."),
                    "error": PortDoc(desc="This port gets triggered when an error occurs.")
                }
            )
        )
    )
