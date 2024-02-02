import json

from pydantic import field_validator

from tracardi.service.notation.dict_traverser import DictTraverser
from tracardi.service.plugin.domain.config import PluginConfig
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner


class Config(PluginConfig):
    id: str
    name: str
    data: str = "{}"

    @field_validator("id")
    @classmethod
    def id_can_not_be_empty(cls, value):
        if not value:
            raise ValueError("Id can not be empty.")
        return value

    @field_validator("name")
    @classmethod
    def name_can_not_be_empty(cls, value):
        if not value:
            raise ValueError("Name can not be empty.")
        return value

    @field_validator("data")
    @classmethod
    def data_can_not_be_empty(cls, value):
        if not value:
            return "{}"
        return value


def validate(config: dict) -> Config:
    return Config(**config)


class AddIntegrationIdAction(ActionRunner):
    config: Config

    async def set_up(self, init):
        self.config = validate(init)

    """
    If your profile has some id in external system this plugin can be used to add the connection between these
    systems and put external id o the profile in tracardi
    """

    async def run(self, payload: dict, in_edge=None):
        try:
            dot = self._get_dot_accessor(payload)
            external_id = dot[self.config.id]
            traverser = DictTraverser(dot)
            data = json.loads(self.config.data)
            data = traverser.reshape(data)
            # Saves in profile metadata.system.integrations external system id where the key is system name and the value is id and data.
            self.profile.metadata.system.set_integration(
                self.config.name.lower().replace(' ', '-'),
                str(external_id),
                data)
            self.profile.mark_for_update()
            return Result(port="payload", value=payload)
        except Exception as e:
            self.console.error(str(e))
            return Result(port="error", value={
                "message": str(e)
            })


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='AddIntegrationIdAction',
            inputs=["payload"],
            outputs=["payload", "error"],
            version='0.8.2',
            license="MIT + CC",
            author="Risto Kowaczewski",
            init={
                "id": "event@properties",
                "name": "",
                "data": "{}"
            },
            manual="add_external_id_action",
            form=Form(groups=[
                FormGroup(
                    fields=[
                        FormField(
                            id="id",
                            name="External ID",
                            description="Reference external ID.",
                            component=FormComponent(type="dotPath", props={"label": "External ID"})
                        ),
                        FormField(
                            id="name",
                            name="External System Name",
                            description="The name will be lower-cased and spaces will be replaced by hyphens.",
                            component=FormComponent(type="text", props={"label": "External System Name"})
                        ),
                        FormField(
                            id="data",
                            name="Additional Data",
                            description="Add additional data related to external system. You can reference any data from event or payload.",
                            component=FormComponent(type="json", props={"label": "External System Data"})
                        )
                    ]
                )
            ]),
        ),
        metadata=MetaData(
            name='Add Integration Id',
            desc='Link profile with their corresponding identities in an external systems.',
            group=["Operations"],
            purpose=['collection', 'segmentation'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "payload": PortDoc(desc="This port returns payload object."),
                    "error": PortDoc(desc="This port returns error message if plugin fails.")
                }
            )
        )
    )
