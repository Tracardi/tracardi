from tracardi.service.storage.elastic.interface.integration_id import save_integration_id
from tracardi.service.notation.dict_traverser import DictTraverser
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from .model.config import Config
from tracardi.service.domain import resource as resource_db
from tracardi.domain.resource import Resource
from tracardi.process_engine.action.v1.connectors.hubspot.client import HubSpotClient
from datetime import datetime


def validate(config: dict) -> Config:
    return Config(**config)


class HubSpotContactAdder(ActionRunner):

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

    def parse_mapping(self):
        for key, value in self.config.properties.items():

            if isinstance(value, list):
                if key == "tags":
                    self.config.properties[key] = ",".join(value)

                else:
                    self.config.properties[key] = "|".join(value)

            elif isinstance(value, datetime):
                self.config.properties[key] = str(value)

    async def run(self, payload: dict, in_edge=None) -> Result:
        try:

            dot = self._get_dot_accessor(payload)
            traverser = DictTraverser(dot)

            self.config.properties = traverser.reshape(self.config.properties)
            self.parse_mapping()

            result = await self.client.add_contact(
                self.config.properties
            )

            if 'id' in result:
                contact_id = result['id']
                await save_integration_id(self.profile.id, 'hubspot', contact_id)

            return Result(port="response", value=result)

        except Exception as e:
            return Result(port="error", value={"message": str(e)})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='HubSpotContactAdder',
            inputs=["payload"],
            outputs=["response", "error"],
            version='0.7.2',
            license="MIT + CC",
            author="Marcin Gaca, Risto Kowaczewski, Ben Ullrich",
            manual="hubspot/hubspot_add_contact_action",
            init={
                "source": {
                    "name": "",
                    "id": "",
                },
                "properties": {},
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
                                id="properties",
                                name="Properties fields",
                                description="You must add some fields to your contact. Just type in the alias of "
                                            "the field as key, and a path as a value for this field.",
                                component=FormComponent(type="keyValueList", props={"label": "Fields"})
                            ),
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Add contact',
            brand="Hubspot",
            desc='Adds a new contact to HubSpot based on provided data.',
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
