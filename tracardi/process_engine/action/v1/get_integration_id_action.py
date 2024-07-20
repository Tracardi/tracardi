from pydantic import field_validator

from tracardi.service.storage.elastic.interface.integration_id import load_integration_id
from tracardi.service.plugin.domain.config import PluginConfig
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner


class Config(PluginConfig):
    name: str
    get_ids_only: bool = True

    @field_validator("name")
    @classmethod
    def name_can_not_be_empty(cls, value):
        if not value:
            raise ValueError("Name can not be empty.")
        return value



def validate(config: dict) -> Config:
    return Config(**config)


class GetIntegrationIdAction(ActionRunner):
    config: Config

    async def set_up(self, init):
        self.config = validate(init)

    """
    If your profile has some id in external system this plugin can be used to load the connection between these
    systems and put external id to the profile in tracardi
    """

    async def run(self, payload: dict, in_edge=None):
        try:
            system_name = self.config.name.lower().replace(" ", "-")
            result = await load_integration_id(self.profile.id, system_name)

            if result is not None:
                if self.config.get_ids_only:
                    result = [item.traits.get('id', None) for item in result]
                else:
                    result = list(result)
                return Result(port="payload", value={"result": result})

            return Result(port="missing", value=payload)
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
            className=GetIntegrationIdAction.__name__,
            inputs=["payload"],
            outputs=["payload", "missing", "error"],
            version='0.8.2',
            license="MIT + CC",
            author="Risto Kowaczewski",
            init={
                "name": "",
                "get_ids_only": True
            },
            manual="get_external_id_action",
            form=Form(groups=[
                FormGroup(
                    fields=[
                        FormField(
                            id="name",
                            name="External System Name",
                            description="The name will be lower-cased and spaces will be replaced by hyphens.",
                            component=FormComponent(type="text", props={"label": "External System Name"})
                        ),
                        FormField(
                            id="get_ids_only",
                            name="Get only IDs",
                            description="When switched will only return IDs without metadata.",
                            component=FormComponent(type="bool", props={"label": "Return only IDs"})
                        )
                    ]
                )
            ]),
        ),
        metadata=MetaData(
            name='Load Integration Id',
            desc='Load external system ID for current profile.',
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
