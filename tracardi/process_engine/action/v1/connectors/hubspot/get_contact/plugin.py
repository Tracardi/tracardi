from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from .model.config import Config
from tracardi.service.domain import resource as resource_db
from tracardi.domain.resource import Resource
from tracardi.process_engine.action.v1.connectors.hubspot.client import HubSpotClient, HubSpotClientException


def validate(config: dict) -> Config:
    return Config(**config)


class HubSpotContactGetter(ActionRunner):

    resource: Resource
    config: Config
    client: HubSpotClient

    async def set_up(self, init):
        config = validate(init)
        resource = await resource_db.load(config.source.id)

        self.config = config
        self.resource = resource
        self.client = HubSpotClient(**resource.credentials.get_credentials(self, None))
        self.client.set_retries(self.node.on_connection_error_repeat)

    async def run(self, payload: dict, in_edge=None) -> Result:
        try:
            result = await self.client.get_contact(self.config.contact_id)
            return Result(port="response", value=result)

        except HubSpotClientException as e:
            return Result(port="error", value={"message": str(e)})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='HubSpotContactGetter',
            inputs=["payload"],
            outputs=["response", "error"],
            version='0.7.2',
            license="MIT + CC",
            author="Marcin Gaca, Risto Kowaczewski, Ben Ullrich",
            manual="hubspot_get_contact_action",
            init={
                "source": {
                    "name": "",
                    "id": ""
                },
                "contact_id": None,
            },
            form=Form(
                groups=[
                    FormGroup(
                        name="Plugin configuration",
                        fields=[
                            FormField(
                                id="source",
                                name="HubSpot resource",
                                description="Please select your HubSpot resource.",
                                component=FormComponent(type="resource", props={"label": "Resource", "tag": "hubspot"})
                            ),
                            FormField(
                                id="contact_id",
                                name="Contact id",
                                description="Please write an id of the contact you want to get.",
                                component=FormComponent(type="text", props={"label": "Company id"})
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Get contact by Id',
            brand="Hubspot",
            desc='Gets a contact from HubSpot based on provided contact id.',
            icon='hubspot',
            group=["Hubspot"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "response": PortDoc(desc="This port returns response from HubSpot API."),
                    "error": PortDoc(desc="This port gets triggered if an error occurs.")
                }
            )
        )
    )
