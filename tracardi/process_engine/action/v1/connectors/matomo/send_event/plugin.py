from tracardi.process_engine.action.v1.connectors.matomo.client import MatomoClient, MatomoClientException
from tracardi.domain.resource import ResourceCredentials
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.storage.driver import storage
from .model.config import Config, MatomoPayload


def validate(config: dict) -> Config:
    return Config(**config)


class SendEventToMatomoAction(ActionRunner):

    @staticmethod
    async def build(**kwargs) -> 'SendEventToMatomoAction':
        config = Config(**kwargs)
        credentials = (await storage.driver.resource.load(config.source.id)).credentials
        return SendEventToMatomoAction(config, credentials)

    def __init__(self, config: Config, credentials: ResourceCredentials):
        self.config = config
        self.client = MatomoClient(**credentials.get_credentials(self))

    async def run(self, payload):
        dot = self._get_dot_accessor(payload)

        data = MatomoPayload(
            idsite=2,
            url="http://localhost:8686/tracker/",
            action_name="page-view"
        )

        try:
            await self.client.send_event(data)
            return Result(port="response", value=payload)

        except MatomoClientException as e:
            return Result(port="error", value=str(e))


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='SendEventToMatomoAction',
            inputs=["payload"],
            outputs=["response", "error"],
            version='0.6.2',
            license="MIT",
            author="Dawid Kruk",
            #manual,
            init={
                "source": {
                    "id": None,
                    "name": None
                }
            },
            form=Form(
                groups=[
                    FormGroup(
                        name="Plugin configuration",
                        fields=[
                            FormField(
                                id="source",
                                name="Matomo resource",
                                description="Please select your Matomo resource, containing Matomo URL and token.",
                                component=FormComponent(type="resource", props={"label": "Resource", "tag": "matomo"})
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Send event to Matomo',
            desc='Sends currently processed event to Matomo.',
            icon='plugin',
            group=["Connectors"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "response": PortDoc(desc="This port returns payload if everything is OK."),
                    "error": PortDoc(desc="This port gets triggered if an error occurs.")
                }
            )
        )
    )
