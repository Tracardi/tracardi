from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result
from .model.config import Config
from tracardi.service.domain import resource as resource_db
from tracardi.domain.resources.remote_api_resource import RemoteApiResource
from tracardi.service.tracardi_http_client import HttpClient


def validate(config: dict) -> Config:
    return Config(**config)


class TokenGetter(ActionRunner):

    _credentials: RemoteApiResource
    config: Config

    async def set_up(self, init):
        config = validate(init)
        source = await resource_db.load(config.source.id)

        self.config = config
        self._credentials = source.credentials.get_credentials(self, RemoteApiResource)

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)

        async with HttpClient(self.node.on_connection_error_repeat) as client:
            async with client.post(
                    url=self._credentials.url,
                    data={
                        "username": self._credentials.username,
                        "password": self._credentials.password
                    } if self._credentials.username and self._credentials.password else None
            ) as response:
                result = await response.json()

                if response.status == 404:
                    return Result(port="error", value={
                        "detail": "URL {}, method POST, returned status 404: Not Found".format(self._credentials.url)})

                if response.status != 200:
                    return Result(port="error", value=result)

                dot[self.config.destination] = result

                return Result(port="payload", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='TokenGetter',
            inputs=["payload"],
            outputs=["payload", "error"],
            version='0.6.1',
            license="MIT + CC",
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
                groups=[
                    FormGroup(
                        name="Oauth2 Connection Configuration",
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
            group=["Operations"],
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
