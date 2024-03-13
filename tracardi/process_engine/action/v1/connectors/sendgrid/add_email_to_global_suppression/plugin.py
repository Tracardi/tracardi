from tracardi.domain.resource import Resource
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.domain import resource as resource_db
from .model.config import Config, Token
from ..client import SendgridClient


def validate(config: dict) -> Config:
    return Config(**config)


class SendgridGlobalSuppressionAdder(ActionRunner):
    client: SendgridClient
    resource: Resource
    config: Config
    credentials: Token

    async def set_up(self, init):
        config = validate(init)
        resource = await resource_db.load(config.source.id)

        self.config = config
        self.resource = resource
        self.credentials = self.resource.credentials.get_credentials(self, output=Token)  # type: Token
        self.client = SendgridClient(**dict(self.credentials))
        self.client.set_retries(self.node.on_connection_error_repeat)

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)
        email = dot[self.config.email]

        try:
            result = await self.client.add_email_to_global_suppression(email=email, )
            return Result(port="response", value=result)

        except Exception as e:
            return Result(port="error", value={"message": str(e)})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='SendgridGlobalSuppressionAdder',
            inputs=["payload"],
            outputs=["response", "error"],
            version='0.7.2',
            license="MIT + CC",
            author="Ben Ullrich",
            manual="sendgrid_add_to_global_suppression",
            init={
                "source": {
                    "id": "",
                    "name": ""
                },
                "email": None,
            },
            form=Form(
                groups=[
                    FormGroup(
                        name="Plugin configuration",
                        fields=[
                            FormField(
                                id="source",
                                name="Token resource",
                                description="Please select your Token resource, containing your api key",
                                component=FormComponent(type="resource",
                                                        props={"label": "Resource", "tag": "sendgrid"})
                            ),
                            FormField(
                                id="email",
                                name="Email address",
                                description="Please type in the path to the email address for your Suppressed Contact.",
                                component=FormComponent(type="dotPath", props={"label": "Email",
                                                                               "defaultSourceValue": "profile",
                                                                               "defaultPathValue": "data.contact.email.main"
                                                                               })
                            ),

                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Suppress contact',
            brand='Sendgrid',
            desc='Adds a contact to Sendgrid global Suppression based on provided data.',
            icon='email',
            group=["Sendgrid"],
            tags=['mailing'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "response": PortDoc(desc="This port returns response from Sendgrid API."),
                    "error": PortDoc(desc="This port gets triggered if an error occurs.")
                }
            )
        )
    )
